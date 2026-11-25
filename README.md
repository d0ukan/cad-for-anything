# CAD for Anything

**English** · [Türkçe](README.tr.md)

[![ci](https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml/badge.svg)](https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml) · License: [MIT](LICENSE) · Version: v0.2.0 ([changelog](CHANGELOG.md))

A small template for designing mechanical parts and assemblies — 3D printing,
CNC and sheet metal — together with **any AI assistant** and **any CAD program**
(FreeCAD, Fusion, SolidWorks, Onshape, CadQuery …).

## Quick start

1. Click **Use this template** to make your own copy.
2. Give the repo link to any AI chat and say:
   *"I want to design a part with this."*
3. The AI reads [AGENTS.md](AGENTS.md), asks a few questions in order, and
   guides you step by step. You build the model in your CAD program.

## How it works

- **Optional FDM prototype first.** The first question is: *print and test an
  FDM prototype first?* If yes, the part is designed to be printable
  (`P01`, `P02` …). When the print works, the project moves to the real
  material and process (`R01`).
- **Roles:** Manager (questions, records), Designer (model, exports) and
  two independent reviewers — **function** (strength, fits) and **DFM**
  (can it be made). See [ROLES.md](ROLES.md).
- **Three gates, all approved by you:** G0 requirements → G1 design →
  RELEASE manufacturing files.
- **Short rules with IDs** in [rules/](rules/README.md): material (MAT),
  tolerances (TOL), DFM, drawings (DWG), naming (REV).

```
[FDM prototype P01..] --test OK--> [production R01..]
   each revision:  G0 -> design -> 2 reviews -> G1 -> export -> review -> RELEASE
```

## The helper tool

No dependencies, Python 3.10+.

```
python scripts/cadctl.py next      # what to do now, who does it, which command
python scripts/cadctl.py status    # project state
python scripts/cadctl.py check     # release files present and named right?
```

Other commands: `set`, `approve`, `review`, `block`, `unblock`, `bump`,
`promote`, `name`. Run `python scripts/cadctl.py -h`.

## Files

| Path | What |
| :--- | :--- |
| `AGENTS.md` | Instructions for the AI: what to read, what to ask |
| `ROLES.md` | Roles, gates, prototype → production flow |
| `rules/` | Rule files |
| `project/` | Your project: `requirements.md`, `workflow-state.json`, `release/` |
| `examples/MB001-wall-bracket/` | Filled example |
| `scripts/cadctl.py` | State, next step, gate checks |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Update both `README.md` and
`README.tr.md` when you change the README.
