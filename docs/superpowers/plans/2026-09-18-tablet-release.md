# Tablet release implementation plan

**Goal:** Publish the existing game and verify persistent, resettable tablet play.

**Architecture:** Keep the self-contained HTML and embedded catalogue/images. Serve
`index.html` from the root of `main` through GitHub Pages. Persist game state in
localStorage; export/import standalone HTML backups.

**Tech stack:** HTML, CSS, vanilla JavaScript, GitHub Pages, Playwright CLI.

## Constraints

- Keep the original game rules and catalogue.
- One device, file backups; no account or cloud backend.
- Preserve valid v2/v3/v4 saves; reject malformed imports before mutation.
- Work in this session; publication is already requested by the user.

## 1. Preserve original and reproduce failures

- [x] Commit the unmodified `tim-kopilka-v4.html` to preserve the supplied source.
- [x] Use Playwright CLI to load it, capture the tablet screen, and reproduce loss
  of the selected tab/page and the reset of a downloaded save after reloading.
- [x] Rename the application to `index.html`; keep a redirect at the original name.

## 2. Repair persistence and validate input

- [x] Extend `valid(s)` to check nested settings, owned sets, log and pending events.
  A malformed item such as `owned: [null]` must fail before replacing the game.
- [x] Parse storage candidates independently. Select downloaded saves using a stable
  key derived from the embedded game's ID so a reset survives reload.
- [x] Store `state.ui = {tab, offset}` with game data and restore it on startup/import.
- [x] Show storage failures in a persistent alert and the parent panel; keep exports
  available. Verify name escaping and date validation.
- [x] Exercise balance/date arithmetic, pending credits, job/bike limits, purchase,
  backup import/export and reset through the actual browser UI.

## 3. Document and publish

- [x] Add `README.md` with recovered rules, tablet URL, backup/reset instructions,
  local server command, storage limits, and verification results.
- [x] Add `.nojekyll`; ignore local browser artifacts in `.gitignore`.
- [x] Check `git diff --check`, inspect the publish set, commit and push to `main`.
- [x] Enable Pages via `gh api` with `source[branch]=main`, `source[path]=/`.
- [x] Wait for the build, then verify HTTP 200 and saving/reset on the live URL.

## 4. Home screen launch (user clarification)

- [x] Add manifest with relative scope/start URL, standalone display and PNG icons.
- [x] Register `sw.js` only for the hosted game; cache the shell for offline reopening.
- [x] Verify the manifest and offline reload in Chromium and WebKit, plus the live subpath.
