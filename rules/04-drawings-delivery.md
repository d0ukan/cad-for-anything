# 04 · Drawings and file delivery (DWG)

- **DWG-01** — Release files go in `project/release/<CODE>-<REV>/`.
  `cadctl.py check` must pass before RELEASE.
- **DWG-02** — Default deliverables by process (change with
  `cadctl.py set deliverables step,pdf,...`):

  | Process | Files |
  | :--- | :--- |
  | fdm, sla, sls | STEP, STL |
  | cnc | STEP, PDF drawing |
  | sheet-metal | STEP, PDF drawing, DXF flat pattern |
  | other | STEP |

- **DWG-03** — STEP (AP214 or AP242) is the master 3D file for every process.
  Native CAD files are optional extras.
- **DWG-04** — STL: export in mm, fine enough that curves are smooth
  (chord ≤ 0.01 mm or "high" setting), one body per file.
- **DWG-05** — PDF drawing contains: title block (name, code, revision,
  material, finish, units, general tolerance, date), all critical
  dimensions and fits, thread callouts, surface finish where it matters.
- **DWG-06** — Dimensions on the drawing must match the model. Do not
  dimension the same feature twice.
- **DWG-07** — For assemblies: one STEP of the assembly plus one per part,
  and the parts list from `project/bom.csv` (checked by `cadctl.py bom`),
  copied into the release folder as `<CODE>-<REV>.csv`.
- **DWG-08** — Add a short `NOTES.md` in the release folder if the supplier
  needs more: print orientation, infill, finish, quantity.
