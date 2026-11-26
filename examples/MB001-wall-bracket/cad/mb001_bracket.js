// MB001-R01 wall bracket - simplified JSCAD model (JavaScript).
//
// Same part as mb001_bracket.py (CadQuery) and mb001_bracket.scad (OpenSCAD).
// Shows the code-based CAD path from AGENTS.md section 5. Needs Node.js 18+
// (Windows, macOS, Linux).
// Run:  npm install  then  npm run build   ->  writes MB001-R01.stl here
//
// Simplified: no bend radius, no rail cut-out, no bend relief. A real
// sheet-metal part is modelled with the CAD program's sheet-metal tools (DFM-45).

const fs = require('fs')
const path = require('path')
const { cuboid, cylinder } = require('@jscad/modeling').primitives
const { union, subtract } = require('@jscad/modeling').booleans
const { translate, rotateX } = require('@jscad/modeling').transforms
const { measureVolume } = require('@jscad/modeling').measurements
const stl = require('@jscad/stl-serializer')

const T = 2            // sheet thickness, mm (requirements: S235, 2 mm)
const WIDTH = 40       // bracket width
const WALL_H = 100     // wall leg height
const ARM_L = 100      // shelf arm length
const FLANGE_H = 20    // load flange height (review.md F-003)
const HOLE_D = 6.6     // wall screw clearance
const HOLE_Z = [10, 90] // 80 mm apart; upper hole 10 mm from the bend (DFM-43)

// Box from its minimum corner and size (like OpenSCAD cube()).
const box = (min, size) =>
  cuboid({ size, center: min.map((m, i) => m + size[i] / 2) })

const wall = box([-WIDTH / 2, 0, 0], [WIDTH, T, WALL_H])
const arm = box([-WIDTH / 2, 0, WALL_H - T], [WIDTH, ARM_L, T])
const flange = box([WIDTH / 2 - T, T, WALL_H - FLANGE_H], [T, ARM_L - T, FLANGE_H])

// Two screw holes through the wall leg (cylinder axis along Y).
const holes = HOLE_Z.map((z) =>
  translate([0, T / 2, z],
    rotateX(Math.PI / 2, cylinder({ radius: HOLE_D / 2, height: 4 * T, segments: 64 }))))

const bracket = subtract(union(wall, arm, flange), ...holes)

const out = path.join(__dirname, 'MB001-R01.stl')
fs.writeFileSync(out, stl.serialize({ binary: false }, bracket).join(''))
console.log(`wrote ${out}, volume ${measureVolume(bracket).toFixed(1)} mm3`)
