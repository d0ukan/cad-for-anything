# Requirements — <PROJECT NAME> (<CODE>)

Kept by the Manager. Approved at G0. Write "decide later" for open items.

## Identity

| Field | Value |
| :--- | :--- |
| Project name | |
| Project code | |
| Phase / revision | prototype P01 / production R01 |
| CAD program (+ access: MCP / code / manual) | |
| Units / tolerance standard | mm + ISO 2768-m |

## Function

- What the part does:
- What it mounts to / mates with:
- Envelope (max size L × W × H):

## Loads and environment

| Item | Value |
| :--- | :--- |
| Load (N), direction, static/dynamic | |
| Safety factor | |
| Temperature range (°C) | |
| Outdoor / UV / water / chemicals | |
| Safety-critical? (AI-01) | no |

## Manufacturing

| Item | Prototype | Final |
| :--- | :--- | :--- |
| Process | fdm | |
| Material / grade | | |
| Finish / colour | | |
| Quantity | | |
| Supplier / machine + limits source (DFM-01) | | |
| Cost target | | |

## Critical dimensions and fits

| Feature | Value | Tolerance / fit | Why |
| :--- | :--- | :--- | :--- |
| | | | |

## Parts and product tree

Single part: skip. Assembly or purchased parts (screws, inserts, bearings):
fill `project/bom.csv` and show the tree with `cadctl.py bom`.

## Prototype test plan

Fill before G1 of a prototype revision. `promote` evidence = the result column.

| Test | How | Pass if | Result |
| :--- | :--- | :--- | :--- |
| Fit | | | |
| Function | | | |
| Load (if any) | | | |

## Open decisions

| # | Question | Due gate |
| :--- | :--- | :--- |

## Revision history

| Rev | Date | Change |
| :--- | :--- | :--- |
