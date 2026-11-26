"""MB001-R01 wall bracket - simplified CadQuery model.

Shows the "AI can run code" path from AGENTS.md section 5.
Not run in CI. Needs:  pip install cadquery
Run:  python mb001_bracket.py   ->  writes MB001-R01.step next to this file

Simplified: no bend radius, no rail cut-out, no bend relief. A real
sheet-metal part is modelled with the CAD program's sheet-metal tools (DFM-45).
"""
from pathlib import Path

import cadquery as cq

T = 2.0            # sheet thickness, mm (requirements: S235, 2 mm)
WIDTH = 40.0       # bracket width
WALL_H = 100.0     # wall leg height
ARM_L = 100.0      # shelf arm length
FLANGE_H = 20.0    # load flange height (review.md F-003)
HOLE_D = 6.6       # wall screw clearance
HOLE_Z = (10.0, 90.0)  # 80 mm apart; upper hole 10 mm from the bend (DFM-43)

# Wall leg: vertical plate in the XZ plane, thickness along +Y.
wall = cq.Workplane("XY").box(WIDTH, T, WALL_H, centered=(True, False, False))

# Shelf arm: horizontal plate on top of the wall leg.
arm = (cq.Workplane("XY")
       .box(WIDTH, ARM_L, T, centered=(True, False, False))
       .translate((0, 0, WALL_H - T)))

# Load flange: vertical strip under one edge of the arm.
flange = (cq.Workplane("XY")
          .box(T, ARM_L - T, FLANGE_H, centered=(False, False, False))
          .translate((WIDTH / 2 - T, T, WALL_H - FLANGE_H)))

# Two screw holes through the wall leg.
holes = (cq.Workplane("XZ")
         .pushPoints([(0, z) for z in HOLE_Z])
         .circle(HOLE_D / 2)
         .extrude(4 * T, both=True))

bracket = wall.union(arm).union(flange).cut(holes)

if __name__ == "__main__":
    out = Path(__file__).with_name("MB001-R01.step")
    cq.exporters.export(bracket, str(out))
    print(f"wrote {out}")
