# Gallery Close Button Implementation Plan

**Goal:** Add a clear top-right close button to the set gallery.

**Architecture:** Extend the existing product header and reuse the native dialog
close action. Implement inline in this session because this is one small change.

**Tech Stack:** HTML/CSS/JavaScript, Playwright CLI, GitHub Pages.

## Global Constraints

- Keep the bottom Close button and current list cards.
- Top close target: 56 × 56 px on tablets; 48 × 48 px on phones.
- No changes to saved state or purchase behavior.

## Task: Add and publish the close control

Files: `index.html`, `sw.js`, `docs/verification.md`.

- [x] Add `button#product-close-top` with an inline decorative SVG cross and
  `aria-label="Закрыть набор"` beside `#product-title`. Use a three-column header
  grid with symmetric button-width outer columns and a wrapping central title.
- [x] Share the existing close handler:
  `$('product-close-top').onclick=$('product-close').onclick=()=>$('product').close();`
- [x] Bump shell cache from `tim-kopilka-shell-v3` to `tim-kopilka-shell-v4`.
- [x] Use Playwright CLI to open a card, inspect header geometry, click the cross,
  reopen and click the bottom Close button at 1024×768, 768×1024 and 390×844.
  Also inspect the longest catalogue title at 320×568. Check Chromium and WebKit;
  do not add a test suite for this reversible control change.
- [x] Record verification, commit, push, and check the control on GitHub Pages.
