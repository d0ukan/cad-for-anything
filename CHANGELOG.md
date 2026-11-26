# Changelog

## v0.4.1 — 2026-11-26

- ROL-09: one session per project. The AI never opens a new chat or
  session by itself; sub-agents inside the session may do Designer and
  Reviewer work. AGENTS.md, ROLES.md (ROL-06) and READMEs updated.
- README (EN + TR): banner, badges, diagrams for roles in one session,
  a sample session, revisions and the product tree; sample tool output.

## v0.4.0 — 2026-11-26

**Fixes**
- Changing a requirement field (phase, units, tolerance standard, process,
  target process, material) after G0 resets all approvals and reviews.
- Files are hashed at RELEASE; `check` and `next` report later changes,
  additions or deletions (REV-04).
- `promote` clears the prototype material, so G0 asks for the final one.

**New**
- `project/bom.csv` and `cadctl.py bom`: parts list check, product tree,
  buy-list totals, `--mermaid` diagram. `check` also validates the BOM.
- Prototype test plan in `requirements.md`; MAT-08 (prototype keeps all
  interfaces of the final part).
- Example: `bom.csv`, filled test plan, simplified CadQuery model.
- `CLAUDE.md`, `GEMINI.md` (point to AGENTS.md), `.gitattributes`;
  `llms.txt` updated.
- Interference and assembly checks: TOL-09 (static interference), TOL-10
  (motion clearance), TOL-11 (worst-case gap), DFM-05 (assembly access and
  order), DFM-06 (wrong-way assembly); ROL-08 fixes which reviewer checks
  what, and no PASS without the CAD interference result.

## v0.3.0 — 2026-11-26

- CAD access check (AGENTS.md section 5): after the user names the CAD
  program, the AI checks its own MCP tools; if none, it shows known MCP
  servers and asks before any setup. Rule AI-06.
- Known MCP servers listed for Fusion, Inventor, SolidWorks, CATIA V5,
  Onshape, FreeCAD (not tested by this repo).
- `project/cad/` for model scripts.
- README: workflow flowchart (Mermaid).

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
