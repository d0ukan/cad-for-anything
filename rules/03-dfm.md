# 03 · Design for manufacturing (DFM)

Read only the section for your process. Values are safe defaults; check the
supplier's own limits before release (`DFM-01`).

## General

- **DFM-01** — Before RELEASE, check the chosen supplier's or machine's
  limits and write the source (link, date) in `requirements.md`.
- **DFM-02** — Prefer standard hardware (ISO metric screws, heat-set
  inserts, standard bearings). Name the exact part in the requirements.
- **DFM-03** — Add fillets/chamfers to outside edges and inside corners where
  the process allows. Avoid sharp inside corners under load.
- **DFM-04** — Keep wall thickness as even as possible.
- **DFM-05** — Assembly access: every screw, nut and connector can be reached
  with its real tool (screwdriver, hex key, wrench swing, fingers). Write the
  assembly order; each step must be possible with the parts already in place.
- **DFM-06** — Poka-yoke: parts that look alike or fit two ways get a feature
  that allows only the correct way (asymmetric hole, key, marking).

## FDM (also used for prototypes)

- **DFM-10** — Wall ≥ 1.2 mm (3 perimeters with a 0.4 mm nozzle); ≥ 2 mm for load.
- **DFM-11** — Overhangs ≤ 45° without support; bridges ≤ 10 mm. Design so
  the part prints without support if possible; state the print orientation.
- **DFM-12** — Load along the layers, not across them (layers split apart).
- **DFM-13** — Holes: horizontal holes > 8 mm need a teardrop or flat top.
  Use heat-set inserts or nut traps for screws that are opened often.
- **DFM-14** — Minimum feature 0.8 mm; embossed text ≥ 0.6 mm high.
- **DFM-15** — First-layer chamfer (~0.4 mm) on edges touching the bed to
  hide elephant foot.

## SLA / SLS

- **DFM-20** — SLA wall ≥ 1 mm, add drain holes (≥ 3 mm) to hollow parts.
- **DFM-21** — SLS wall ≥ 0.8 mm, escape holes for powder; no support needed.

## CNC milling / turning

- **DFM-30** — Inside corner radius ≥ 1/3 of pocket depth; use a standard
  tool size (e.g. R1.5, R3, R5).
- **DFM-31** — Pocket depth ≤ 4 × tool diameter.
- **DFM-32** — Wall ≥ 1 mm (metal), ≥ 1.5 mm (plastic).
- **DFM-33** — Holes: standard drill sizes; depth ≤ 6 × diameter; threads
  ≤ 2 × diameter deep.
- **DFM-34** — Design for as few setups as possible; say how many in the review.
- **DFM-35** — No tolerance tighter than ±0.05 mm unless needed (`TOL-03`).

## Sheet metal

- **DFM-40** — One thickness for the whole part; use a standard gauge
  (1, 1.5, 2, 3 mm).
- **DFM-41** — Inside bend radius ≥ thickness (use the supplier's tooling radius).
- **DFM-42** — Flange length ≥ 4 × thickness.
- **DFM-43** — Holes ≥ thickness in diameter and ≥ 2 × thickness from a bend.
- **DFM-44** — Add bend relief where a bend meets an edge.
- **DFM-45** — Export the flat pattern (DXF) from the CAD sheet-metal tool,
  not a hand-made outline; note the K-factor used.
