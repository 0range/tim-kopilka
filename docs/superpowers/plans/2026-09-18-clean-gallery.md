# Clean cards and gallery implementation plan

**Goal:** Simplify the catalogue and replace the detail view with a full-screen photo gallery.

**Architecture:** Keep the existing HTML app and embedded first images. Download
additional product-matched photos under `assets/gallery/`, embed a compact photo
manifest, and cache photos on demand through the service worker.

**Tech stack:** Vanilla HTML/CSS/JavaScript, Python collection script, Playwright CLI.

## Tasks

- [x] Collect primary photos from official LEGO by set ID and extra views from matched retailer pages,
  deduplicate them, save local files and their original source URLs.
- [x] Render each catalogue/shelf card as a single accessible opener containing
  only photo, name and price/status; remove the goal controls and selection logic.
- [x] Add a full-screen `product` dialog with title, image, arrows, counter, swipe,
  keyboard navigation, price, conditional buy action and close button.
- [x] Keep purchase guards and persistence; clear legacy goals during migration.
- [x] Cache additional local photos on demand and handle image-load failure.
- [x] Keep optional HTML backups playable offline with embedded covers; use published URLs for extras.
- [x] Update in-game instructions, README, photo credits and service-worker version.
- [x] Verify layouts and gallery/purchase/save behavior in Chromium and WebKit.
- [x] Publish and verify the same behavior and local photo URLs on GitHub Pages.
