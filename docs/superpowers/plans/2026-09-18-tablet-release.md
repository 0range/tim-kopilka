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

- [ ] Commit the unmodified `tim-kopilka-v4.html` to preserve the supplied source.
- [ ] Use Playwright CLI to load it, capture the tablet screen, and reproduce loss
  of the selected tab/page and the reset of a downloaded save after reloading.
- [ ] Rename the application to `index.html`; keep a redirect at the original name.

## 2. Repair persistence and validate input

- [ ] Extend `valid(s)` to check nested settings, owned sets, log and pending events.
  A malformed item such as `owned: [null]` must fail before replacing the game.
- [ ] Parse storage candidates independently. Select downloaded saves using a stable
  key derived from the embedded game's ID so a reset survives reload.
- [ ] Store `state.ui = {tab, offset}` with game data and restore it on startup/import.
- [ ] Show storage failures in a persistent alert and the parent panel; keep exports
  available. Verify name escaping and date validation.
- [ ] Exercise balance/date arithmetic, pending credits, job/bike limits, purchase,
  backup import/export and reset through the actual browser UI.

## 3. Document and publish

- [ ] Add `README.md` with recovered rules, tablet URL, backup/reset instructions,
  local server command, storage limits, and verification results.
- [ ] Add `.nojekyll`; ignore local browser artifacts in `.gitignore`.
- [ ] Check `git diff --check`, inspect the publish set, commit and push to `main`.
- [ ] Enable Pages via `gh api` with `source[branch]=main`, `source[path]=/`.
- [ ] Wait for the build, then verify HTTP 200 and saving/reset on the live URL.
