#!/usr/bin/env python3
"""Refresh local galleries by LEGO set ID: uv run --with pillow scripts/collect-photos.py.

LEGO's official CDN supplies the primary photo. Product-matched retailer galleries
provide additional views. Existing successful downloads are reused unless --refresh.
The app never calls retailer websites. Original URLs remain in data/photos.json.
"""
import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/photos.json'
MAX_PHOTOS = 7
OFFICIAL = json.loads((ROOT / 'data/lego-photo-overrides.json').read_text())


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'TimKopilka-photo-collector/1.0'})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return response.read()
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt:
                raise
            time.sleep(0.5)


class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.photos = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and attrs.get('elementtiming') == 'productGalleryImage':
            self.photos.append(attrs['src'])


def retailer_photos(product, provider):
    page = product['offers'][provider]['url']
    html = fetch(page).decode('utf-8')
    ident = product['id']
    if provider == 'dm':
        if not re.search(r'Артикул:</span></th><td[^>]*>\s*' + ident + r'\s*</td>', html):
            raise ValueError('Retailer article does not match ' + ident)
        parser = GalleryParser()
        parser.feed(html)
        urls = list(dict.fromkeys(parser.photos))
    else:
        title = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)
        if not title or not re.search(r'\b' + ident + r'\b', title[1]):
            raise ValueError('Retailer title does not match ' + ident)
        urls = []
        for index, url in re.findall(r'data-original-index="(\d+)"[^>]*data-hires-src="([^"]+)"', html):
            if int(index) == 0 and urls:
                break
            urls.append(urllib.parse.urljoin(page, unescape(url)))
    # Retailers usually put packaging at the end. Preserve these views in a
    # bounded gallery, in addition to the initial product/detail photos.
    selected = list(dict.fromkeys(urls[:1] + urls[-2:] + urls[1:]))
    return [(url, provider, page, 'additional') for url in selected]


def normalized(raw):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
    image.load()
    if image.width < 200 or image.height < 150:
        raise ValueError('Image too small')
    rgba = image.convert('RGBA')
    white = Image.new('RGB', rgba.size, 'white')
    white.paste(rgba, mask=rgba.getchannel('A'))
    white.thumbnail((1280, 1280))
    return white


def fingerprint(image):
    sample = image.resize((9, 8)).convert('L')
    pixels = list(sample.get_flattened_data())
    return sum((pixels[y * 9 + x] > pixels[y * 9 + x + 1]) << (y * 8 + x)
               for y in range(8) for x in range(8))


def collect(product):
    ident = product['id']
    directory = ROOT / 'assets/gallery' / ident
    directory.mkdir(parents=True, exist_ok=True)
    photos, hashes, warnings = [], [], []

    def add_photo(candidate):
        url, provider, page, kind = candidate
        try:
            image = normalized(fetch(url))
            perceptual = fingerprint(image)
            if any((perceptual ^ previous).bit_count() <= 2 for previous in hashes):
                return
            buffer = io.BytesIO()
            image.save(buffer, 'WEBP', quality=84, method=6)
            data = buffer.getvalue()
            digest = hashlib.sha256(data).hexdigest()
            path = directory / (digest[:12] + '.webp')
            path.write_bytes(data)
            photos.append({'file': str(path.relative_to(ROOT)), 'provider': provider,
                           'source': url, 'page': page, 'kind': kind,
                           'width': image.width, 'height': image.height, 'sha256': digest})
            hashes.append(perceptual)
        except Exception as exc:
            warnings.append(str(exc) + ': ' + url)

    official = OFFICIAL.get(ident, {
        'image': f'https://www.lego.com/cdn/product-assets/product.img.pri/{ident}_Prod.png',
        'page': f'https://www.lego.com/en-us/product/{ident}'})
    add_photo((official['image'], 'lego', official['page'], 'primary'))
    for provider in ('dm', 'mk'):
        if provider not in product['offers'] or len(photos) >= MAX_PHOTOS:
            continue
        try:
            candidates = retailer_photos(product, provider)
            for candidate in candidates:
                add_photo(candidate)
                if len(photos) >= MAX_PHOTOS:
                    break
        except Exception as exc:
            warnings.append(str(exc) + ': ' + product['offers'][provider]['url'])
    print(ident, len(photos), 'photos', 'LEGO primary' if photos and photos[0]['provider'] == 'lego' else 'retailer fallback', flush=True)
    return ident, {'setId': ident, 'name': product['name'], 'checked': date.today().isoformat(),
                   'photos': photos, 'collectionNotes': warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', nargs='*', help='Only update these set IDs')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--no-embed', action='store_true', help='Collect without rewriting index.html')
    args = parser.parse_args()
    html = (ROOT / 'index.html').read_text()
    catalog = json.loads(re.search(r'const CATALOG=(\[.*?\]);', html, re.S)[1])
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {
        'version': 1, 'primarySource': 'https://www.lego.com/', 'sets': {}}
    products = [p for p in catalog if (not args.ids or p['id'] in args.ids)
                and (args.refresh or p['id'] not in manifest['sets'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for ident, entry in pool.map(collect, products):
            manifest['sets'][ident] = entry
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    # Remove obsolete local photos only within the generated gallery directory.
    keep = {photo['file'] for entry in manifest['sets'].values() for photo in entry['photos']}
    for path in (ROOT / 'assets/gallery').glob('*/*.webp'):
        if str(path.relative_to(ROOT)) not in keep:
            path.unlink()
    if args.no_embed:
        return
    # Embed small covers and the compact manifest so HTML backups stay playable.
    html = (ROOT / 'index.html').read_text()
    match = re.search(r'(<script id="assets"[^>]*>)(.*?)(</script>)', html, re.S)
    embedded = json.loads(match[2])
    compact = {}
    for ident, entry in manifest['sets'].items():
        photos = entry['photos']
        compact[ident] = [p['file'] for p in photos]
        if photos:
            cover = Image.open(ROOT / photos[0]['file'])
            cover.thumbnail((640, 640))
            buffer = io.BytesIO()
            cover.save(buffer, 'WEBP', quality=82, method=6)
            embedded[ident] = 'data:image/webp;base64,' + base64.b64encode(buffer.getvalue()).decode()
    html = html[:match.start(2)] + json.dumps(embedded, separators=(',', ':')) + html[match.end(2):]
    tag = '<script id="gallery-assets" type="application/json">' + json.dumps(compact, separators=(',', ':')) + '</script>'
    if 'id="gallery-assets"' in html:
        html = re.sub(r'<script id="gallery-assets"[^>]*>.*?</script>', lambda _: tag, html, flags=re.S)
    else:
        html = html.replace('<script id="assets"', tag + '\n<script id="assets"', 1)
    (ROOT / 'index.html').write_text(html)
    print('Saved', len(manifest['sets']), 'sets,', sum(len(e['photos']) for e in manifest['sets'].values()), 'photos')


if __name__ == '__main__':
    main()
