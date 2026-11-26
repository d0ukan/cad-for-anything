# AGENTS.md — start here

This repo is a template for designing mechanical parts and small assemblies
(3D printing, CNC, sheet metal) with any AI assistant and any CAD program.
It works the same in a web chat, an IDE agent or a CLI agent.

## 1. Read only this first

1. This file.
2. [ROLES.md](ROLES.md) — roles and gates.
3. [rules/README.md](rules/README.md) — which rule file to open at which step.

Do **not** read every rule file up front. Open a rule file only when you reach
the step that needs it. A filled example is in
[examples/MB001-wall-bracket/](examples/MB001-wall-bracket/).

## 2. Check the current state

- If `project/workflow-state.json` already has a `project_code`, the project is
  in progress: run `python scripts/cadctl.py next` (or ask the user to run it
  and paste the output) and continue from there. Do not ask answered questions again.
- New project: suggest the user creates their own copy
  (GitHub **Use this template**, or download ZIP). Never write project files
  into or push to the template repo itself.

## 3. First questions (new project)

Ask in **one short message**, in this order. Offer "decide later" only where
marked. Save each answer with `cadctl.py set` (command in brackets).

1. **FDM prototype first?** Will you first print and test an FDM prototype,
   then make the final part in its real material/process?
   - yes → `set phase prototype`, `set revision P01`, `set process fdm`.
     The design is made FDM-printable first (rules/03, FDM section).
   - no → `set phase production`, `set revision R01`.
2. **What is the part?** Function, what it mounts to or mates with, rough size.
3. **Project name and code** (e.g. "Wall bracket", `MB001`) [`set project_name`, `set project_code`].
4. **Final process and material** (CNC aluminium, sheet steel, SLS nylon …)
   [`set target_process`, `set material`]. In prototype phase "decide later" is allowed.
5. **Units and tolerance standard**: mm + ISO, or inch + ASME [`set units`, `set tolerance_standard`].
6. **CAD program** (FreeCAD, Fusion, Inventor, SolidWorks, CATIA, Onshape,
   CadQuery …) [`set cad_tool`]. Then do the CAD access check (section 5).
7. **Requirements**: loads, environment (heat, UV, outdoor, chemicals),
   quantity, critical dimensions and fits, cost target. Write them into
   `project/requirements.md`.

Then show the filled requirements and ask the user for **G0** approval.

## 4. Working rules

- Default role is **Manager**. Act as Designer or Reviewer only when assigned
  (see ROLES.md). The user always gives the final approval.
- Design review has two reviewers: **function** and **DFM** (ROL-06). Run
  each in a new chat/session that sees only the files and requirements.
  With one chat, do them one after another and do not reuse the Designer's
  reasoning.
- Never record an approval the user did not give. Never show a check as passed
  if it was not run. Use `cadctl.py`, do not edit the JSON by hand.
- No CAD access (web chat): give the user step-by-step CAD instructions
  (sketch, constraints, features, dimensions). The user builds the model and
  sends screenshots, measurements or exported files back.
- Cite rule IDs (e.g. `DFM-03`) when you apply or flag a rule.
- **Stop and require a qualified human engineer** at G1 and Release if the
  part is safety-critical: lifting/hanging people or heavy loads overhead,
  pressure vessels, vehicles/aircraft structure, medical contact.
  You may keep helping, but say this clearly (`AI-01`).

## 5. CAD access check (after question 6)

1. **Look at your own tools.** Is an MCP tool for the chosen CAD program
   connected? Call a harmless read-only tool (e.g. list open documents) to
   confirm it works. Do not guess.
2. **Connected** → tell the user, and as Designer build and change the model
   through it.
3. **Not connected** → show the user the options for their program from the
   table below and ask: *set up an MCP server, or continue with step-by-step
   instructions?* Never install anything yourself without the user's yes.
4. **CadQuery or other code-based CAD** → no MCP needed if you can run code.
   Write the script in `project/cad/`, run it, export STEP/STL.
5. **Nothing available** → step-by-step CAD instructions (section 4).

Record the result in `requirements.md` → Identity → CAD program
(e.g. "Fusion, via MCP" or "SolidWorks, manual"). Gates and reviews stay the
same in all cases (`AI-06`).

Known MCP servers. Community-reported and **not tested by this repo**;
check the project before installing it.

| CAD | Official | Community |
| :--- | :--- | :--- |
| Fusion | [Autodesk MCP servers](https://help.autodesk.com/view/ADSKMCP/ENU/) | [faust-machines/fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server) |
| Inventor | Local MCP server mentioned in Inventor 2027 help; check your version | [NeonGlay/inventor-mcp](https://github.com/NeonGlay/inventor-mcp) (Windows, COM) |
| SolidWorks | — | [eyfel/mcp-server-solidworks](https://github.com/eyfel/mcp-server-solidworks) |
| CATIA V5 | — | [daiemon12/catia-v5-mcp-server](https://github.com/daiemon12/catia-v5-mcp-server) (Windows, licensed CATIA) |
| Onshape | FeatureScript MCP server (Onshape Labs, Onshape App Store) | — |
| FreeCAD | — | [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp), [spkane/freecad-addon-robust-mcp-server](https://github.com/spkane/freecad-addon-robust-mcp-server) |
| CadQuery | Not needed (code) | — |

## 6. Prototype → production

When a prototype revision is released, the user prints and tests it.
- Test failed or needs changes → `cadctl.py bump` (P01 → P02).
- Test OK → `cadctl.py promote --evidence "<test result>"`. The project moves
  to `production`, revision `R01`; re-check rules for the final process
  (`rules/03`) and get G0 approval again for the final material.
