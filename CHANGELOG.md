# Changelog

## v0.2.0 — 2026-11-25

- Two independent design reviewers: function and DFM (ROL-06).
  Production needs both PASS; prototype needs at least one; any FAIL blocks G1.
- Manager checks requirements against review reports before G1 (ROL-07).
- `review design` replaced by `review function` and `review dfm`
  (state field `reviews.design` → `reviews.function`, `reviews.dfm`).
- Python 3.10+ (3.9 is not available on the CI Ubuntu image).

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
