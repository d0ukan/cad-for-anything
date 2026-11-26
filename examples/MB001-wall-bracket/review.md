# Design review — MB001-R01

Two independent reviewers · 2026-11-22 · Inputs: requirements.md, MB001-R01 model screenshots.

| ID | Reviewer | Rule | Severity | Finding | Fix | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| F-001 | dfm | DFM-43 | blocking | Upper screw hole 2.5 mm from bend (needs ≥ 4 mm for 2 mm sheet) | Move hole 3 mm up | fixed |
| F-002 | dfm | DFM-44 | minor | No bend relief at rail cut-out side | Add 2 × 2 mm relief | fixed |
| F-003 | function | AI-03 | minor | Bending stress calc missing | Added: M = 150 N × 100 mm = 15 000 N·mm. Flat 40 × 2 mm plate: W = 40·2²/6 = 26.7 mm³ → σ ≈ 560 MPa (fails). With a 20 mm bent flange: W = 2·20²/6 = 133 mm³ → σ ≈ 113 MPa, S235 yield 235 MPa → SF ≈ 2.1 (MAT-06 OK) | fixed |

Required checks (ROL-08):

| Check | Reviewer | Result |
| :--- | :--- | :--- |
| TOL-08 stack | function | Wall hole template ±0.2 + part ±0.2 → rail still drops in (+0.3 cut-out) |
| TOL-09 interference | function | FreeCAD Interference check with wall plane, rail Ø25 and 2 screws: none (screenshot sent by the user in the review chat) |
| TOL-10 motion | function | n/a — no moving parts |
| TOL-11 worst case | function | Indoor 5–35 °C, steel; expansion negligible |
| DFM-05 access | dfm | Screwdriver reaches both screws; upper screw head 8 mm below arm, PH2 bit fits |
| DFM-06 wrong way | dfm | Symmetric holes; bracket only fits arm-up — OK |

Result: function **PASS**, dfm **PASS** after fixes.
