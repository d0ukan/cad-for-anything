# Requirements — Wall bracket (MB001)

## Identity

| Field | Value |
| :--- | :--- |
| Project name | Wall bracket |
| Project code | MB001 |
| Phase / revision | production R01 (after prototypes P01, P02) |
| CAD program | FreeCAD (Sheet Metal workbench), manual (no MCP) |
| Units / tolerance standard | mm + ISO 2768-m |

## Function

- Holds one end of a wooden shelf (Ø25 mm clothes rail under it).
- Mounts to a brick wall with 2 × M6 screws + plugs.
- Envelope: 120 × 40 × 100 mm.

## Loads and environment

| Item | Value |
| :--- | :--- |
| Load | 150 N down at shelf front edge (100 mm from wall), static |
| Safety factor | 2 on yield (MAT-06) |
| Temperature | 5–35 °C, indoor |
| Outdoor / UV / water | no |
| Safety-critical? (AI-01) | no (household shelf, ≤ 15 kg) |

## Manufacturing

| Item | Prototype | Final |
| :--- | :--- | :--- |
| Process | fdm | sheet-metal (laser cut + 1 bend) |
| Material / grade | PETG | S235, 2 mm |
| Finish / colour | black | zinc plated |
| Quantity | 2 | 10 |
| Limits source (DFM-01) | own printer | supplier capability page, checked 2026-11-19 |

## Critical dimensions and fits

| Feature | Value | Tolerance / fit | Why |
| :--- | :--- | :--- | :--- |
| Wall screw holes | Ø6.6 × 2, 80 mm apart | ±0.2 | 6 mm screw clearance, match drill template |
| Rail cut-out | R12.75 | +0.3 / 0 | Ø25 rail must drop in (TOL-05 for prototype) |
| Bend angle | 90° | ±1° | shelf level |
| Load flange height | 20 mm | ±0.5 | strength (see review.md F-003) |

## Parts and product tree

See [bom.csv](bom.csv) (`cadctl.py bom`): kit = 1 bracket + 2 wood screws
6 × 50 mm + 2 wall plugs 8 mm.

## Prototype test plan

| Test | How | Pass if | Result (P02) |
| :--- | :--- | :--- | :--- |
| Fit | Screw to wall with drill template, drop rail in | Rail drops in by hand, holes line up | OK |
| Function | Shelf level check | Shelf within ±1° | OK, 0.5° |
| Load | 5 kg on shelf front edge, 24 h | No crack, sag < 2 mm | OK, 1 mm sag |

Interfaces kept from prototype to R01 (MAT-08): hole positions, rail
cut-out, outer envelope. Changed: 3 mm PETG rib → 20 mm bent steel flange.

## Revision history

| Rev | Date | Change |
| :--- | :--- | :--- |
| P01 | 2026-11-10 | First FDM print |
| P02 | 2026-11-14 | Rail cut-out +0.3 mm (too tight on P01), 3 mm rib added |
| R01 | 2026-11-19 | Converted to 2 mm sheet steel, rib replaced by bend |
