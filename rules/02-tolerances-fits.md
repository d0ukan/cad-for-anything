# 02 · Tolerances and fits (TOL)

- **TOL-01** — Use one unit system and one standard per project
  (`units`, `tolerance_standard` in the state file). Do not mix.
- **TOL-02** — General tolerance by default: ISO 2768-m (mm) or the drawing
  title-block tolerance (inch/ASME). Put it in the drawing title block.
- **TOL-03** — Tighten only dimensions that matter (fits, mating faces, hole
  positions). Every tight tolerance costs money; say why it is needed.
- **TOL-04** — Fits for CNC (ISO 286): clearance H7/g6 (sliding), transition
  H7/k6 (locating), press H7/p6. Give the fit on the drawing, not only a number.
- **TOL-05** — Printed parts — typical clearance per side:

  | Process | Sliding / loose | Snug / press |
  | :--- | :--- | :--- |
  | FDM | 0.3–0.4 mm | 0.1–0.15 mm |
  | SLA | 0.15–0.2 mm | 0.05 mm |
  | SLS | 0.2–0.3 mm | 0.1 mm |

  Print a small test piece first if the fit is critical.
- **TOL-06** — FDM holes print undersize: add ~0.2 mm to small holes or drill
  them after printing. Holes for heat-set inserts follow the insert datasheet.
- **TOL-07** — Sheet metal: ±0.1 mm on laser cut edges, ±0.2–0.5 mm across a
  bend. Do not put tight tolerances across bends.
- **TOL-08** — Check a tolerance stack when 3 or more parts line up; write the
  worst case in the review.

## Interference and clearance (assemblies and mating parts)

- **TOL-09** — Static interference: run the CAD interference/clash check on
  the assembly (including purchased parts, screws and the part it mounts to).
  Zero interference except intended press fits. The result (screenshot or
  report) is review evidence; no PASS without it.
- **TOL-10** — Motion clearance: for moving parts (hinge, slide, lid, cable),
  check the full range of motion, not only the start and end. Write the
  smallest gap; keep ≥ 0.5 mm (printed ≥ 1 mm) unless the requirements say otherwise.
- **TOL-11** — Clearance at worst case: a gap that closes in the TOL-08 stack
  or with heat expansion counts as interference.
