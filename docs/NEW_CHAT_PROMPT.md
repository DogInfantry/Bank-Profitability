# Prompt to start a new chat on this project

Paste this into a new Claude Code session on the repo `DogInfantry/Bank-Profitability`:

---

Continue my HDFC Bank RoA consulting-case project in this repo (branch `main`).

Before doing anything:
1. Read `CLAUDE.md` (the standing rules) and `docs/PROJECT_STATE.md` (the current state, the numbers, the decisions and the open items). Follow them exactly. In particular:
   - commit only as DogInfantry <ankleshrawat5@gmail.com>, with no Claude co-author or session trailers;
   - push only to this branch;
   - the steerco deck stays on hold;
   - Excel stays Garamond with no italics;
   - never expose keys (data.gov.in is allowed, local runs only, key in `.env`).
2. Run `git log --oneline -5` and `git status` and confirm the branch is clean.
3. Reply with a five-line summary of where the project stands and the open items. Then wait for my instruction.

At the end of the session, update `docs/PROJECT_STATE.md` (what changed, open items, session log) and commit it.

---

Tip: to set a task at the same time, add it after step 3, for example: "Today: decide on the valuation roll-forward (open item 1)."
