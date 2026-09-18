# Larger controls implementation plan

**Goal:** Improve tablet readability and the set preview, adjust room cleaning and add earning options.

**Architecture:** Retain the single HTML application. Add dialog variants for product
details and earnings, scoped CSS for larger controls, and backward-compatible sale flags.

**Tech stack:** HTML/CSS/JavaScript, Playwright CLI, GitHub Pages.

## Constraints

- Preserve all current saved balances, history and earned-job flags.
- Keep `toys` as the weekly room-cleaning ID; change its label and future reward only.
- Publish to the existing URL with an updated service-worker cache version.

## Tasks

- [x] Update `index.html`: make the amount a separate line, enlarge controls, and add
  responsive detail-dialog CSS with an image at least 240 px tall on a tablet.
- [x] Extend `show(icon,title,html,buttons,kind='')` to reset and apply the appropriate
  detail/earnings variant. Wrap `info(id)` content in a two-column preview.
- [x] Change the `toys` job to «Прибраться в комнате», amount 100.
- [x] Add one-time books/old LEGO sales with boolean flags, confirmation, migration,
  nested validation and reset handling. Show books on `week % 4 === 0`, old LEGO
  on `week % 4 === 2`; enforce availability in the action handler too.
- [x] Update README and in-game rules; increment `CACHE` in `sw.js`.
- [x] Check layout, large images, updated rewards, cancelled/confirmed sales,
  reload, older saves and reset through Playwright in Chromium and WebKit.
- [ ] Review the diff, commit, push, wait for Pages and verify the live interface.
