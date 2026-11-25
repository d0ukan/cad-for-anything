# Changelog

## v0.1.0 — 2026-11-25

First version.

- `AGENTS.md`, `llms.txt`, `ROLES.md` (Manager / Designer / Reviewer; G0, G1, RELEASE).
- Optional FDM prototype phase (`P01`…) before production (`R01`…).
- Rules: MAT, TOL, DFM (FDM, SLA/SLS, CNC, sheet metal), DWG, REV, AI.
- `project/` template: `workflow-state.json`, `requirements.md`.
- `scripts/cadctl.py`: `status`, `next`, `check`, `set`, `approve`, `review`,
  `block`, `bump`, `promote`, `name`; tests in `tests/`.
- Example `MB001-wall-bracket`.
- CI: tests on Linux/Windows and link check.
