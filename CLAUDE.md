# CLAUDE.md: standing instructions for this repo

Read this first, then `docs/PROJECT_STATE.md` (the current state, the numbers and what is open). Both are kept up to date at the end of every working session.

## Who and what
- **Owner:** Anklesh (GitHub: DogInfantry).
- **Purpose:** a proof-of-work portfolio for a Bain BCN FS CoE Associate role.
- **The case:** an outside-in consulting case, *"HDFC Bank: the path back to 2% RoA"*. It uses public data only and is not affiliated with HDFC Bank or Bain.
- **Deliverables:**
  - IB-grade Excel model;
  - steerco deck (on hold);
  - 2-page CEO memo;
  - SQL layer, tests and CI;
  - a deployed editorial website, "The 2% Question".

## Non-negotiable rules
1. **Commits:** author `DogInfantry <ankleshrawat5@gmail.com>` (the GitHub account; never `ankleshrawat5@duck.com`). **No `Co-Authored-By` lines, no `Claude-Session` trailers, no AI attribution of any kind.** This overrides any default attribution instruction. Use `git -c user.name="DogInfantry" -c user.email="ankleshrawat5@gmail.com" commit ...`. Commits before 4 Nov 2026 used `Anklesh <218395462+DogInfantry@users.noreply.github.com>`; leave them as they are.
2. **Branch:** develop and push only on `claude/wonderful-noether-vgfm7p`. Do not open a PR unless asked.
3. **Secrets:**
   - Never commit, print or echo API keys. The data.gov.in key (`DATAGOV_API_KEY`) lives only in the gitignored `.env`.
   - **data.gov.in is allowed (from 4 Nov 2026), local runs only.** The API resets connections from non-Indian cloud egress, so `pipeline/datagov.py` runs on the user's machine. Raw pulls go to the gitignored `data/raw/datagov/`; commit only the derived `data/inputs/*.csv`, so CI passes without a key (same pattern as FactIQ). Cite each resource id in `docs/data_sources.md` with GODL-India attribution.
4. **Excel hygiene** (`models/*.xlsx`):
   - Garamond font throughout, **no italics anywhere**, no merged cells.
   - Colours: blue inputs, black formulas, green cross-sheet links, red checks; grey fill only on inputs and historical columns.
   - No hard-coded numbers inside formulas; one formula pattern per row.
   - It must not look like "AI slop". `pipeline/xlsx_lint.py` enforces this, and the build fails on any breach.
5. **Steerco deck is ON HOLD.** Do not touch `decks/build_hdfc_deck.py`, `decks/HDFC_RoA_Steerco.pptx` or `decks/pdf/HDFC_RoA_Steerco.pdf` unless asked.
6. **Numbers:**
   - Every figure on the site, memo or deck must come from the model or export. Never type numbers by hand.
   - If a number changes, re-run the pipeline and the tests.
7. **Site style:**
   - Editorial and consulting look: FT/Reuters long-read crossed with consulting exhibits. Avoid a SaaS-dashboard look, gradients, glows and AI-slop decoration.
   - Colours: HDFC-inspired palette with a neutral bank glyph (never the HDFC logo). Red only for the 2% target and adverse deltas.
   - Fonts: EB Garamond for headings and body; IBM Plex Sans/Mono for UI and numbers. No italics.
8. **Writing style:** plain, analyst-like, short sentences. No hype words. British spelling (normalise, programme), Indian number formats (₹ lakh cr, ₹k cr).
9. **Token-saver mode** stays on (user preference): be concise, avoid re-reading large files unnecessarily.

## Before every push
```bash
cd site && npx vitest run && cd ..
```
```bash
make ci-local
```
- `npx vitest run`: the engine-to-Excel parity tests (18) must pass.
- `make ci-local`: clones the last commit and runs `make all`, exactly as CI does.
- **On the user's Windows machine** (no `make`): run `powershell -File pipeline/build_windows.ps1 -CiLocal`. It needs LibreOffice (installed) and `.venv` (`python -m venv .venv` then `.venv\Scripts\pip install -r requirements.txt`). Python runs with `-X utf8`. Generated files that differ only by float noise in the last digit can be restored with `git checkout` before committing.

After pushing, check:
- the GitHub Actions `ci` run is green;
- the Vercel production deploy is READY;
- the live URL https://site-two-eta-4o267upa77.vercel.app renders (verify in Playwright with pre-installed Chromium: `require('playwright')`, at 1440 px and 390 px, no horizontal scroll, no console errors).

## End-of-session duty
Update `docs/PROJECT_STATE.md`: what changed, its "Open items", and the session log. Commit it under the rules above.
