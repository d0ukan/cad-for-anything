// MB001-R01 wall bracket - simplified OpenSCAD model.
//
// Same part as mb001_bracket.py (CadQuery). Shows the code-based CAD path
// from AGENTS.md section 5. OpenSCAD is free for Windows, macOS and Linux.
// Run:  openscad -o MB001-R01.stl mb001_bracket.scad
// (OpenSCAD exports STL/3MF, not STEP; use the CadQuery model for STEP.)
//
// Simplified: no bend radius, no rail cut-out, no bend relief. A real
// sheet-metal part is modelled with the CAD program's sheet-metal tools (DFM-45).

T        = 2;      // sheet thickness, mm (requirements: S235, 2 mm)
WIDTH    = 40;     // bracket width
WALL_H   = 100;    // wall leg height
ARM_L    = 100;    // shelf arm length
FLANGE_H = 20;     // load flange height (review.md F-003)
HOLE_D   = 6.6;    // wall screw clearance
HOLE_Z   = [10, 90];  // 80 mm apart; upper hole 10 mm from the bend (DFM-43)

$fn = 64;

difference() {
    union() {
        // Wall leg: vertical plate, thickness along +Y.
        translate([-WIDTH / 2, 0, 0]) cube([WIDTH, T, WALL_H]);
        // Shelf arm: horizontal plate on top of the wall leg.
        translate([-WIDTH / 2, 0, WALL_H - T]) cube([WIDTH, ARM_L, T]);
        // Load flange: vertical strip under one edge of the arm.
        translate([WIDTH / 2 - T, T, WALL_H - FLANGE_H]) cube([T, ARM_L - T, FLANGE_H]);
    }
    // Two screw holes through the wall leg.
    for (z = HOLE_Z)
        translate([0, T / 2, z]) rotate([90, 0, 0])
            cylinder(d = HOLE_D, h = 4 * T, center = true);
}
