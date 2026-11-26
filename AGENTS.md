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
     The design is made FDM-printable first (rules/03, FDM section) and
     keeps every interface of the final part (MAT-08).
   - no → `set phase production`, `set revision R01`.
2. **What is the part?** Function, what it mounts to or mates with, rough size.
3. **Project name and code** (e.g. "Wall bracket", `MB001`) [`set project_name`, `set project_code`].
4. **Final process and material** (CNC aluminium, sheet steel, SLS nylon …)
   [`set target_process`]. Production: also `set material` (final grade).
   Prototype: `set material` is the **print** material (MAT-02, e.g. PETG);
   the final material goes into `requirements.md` ("decide later" allowed).
5. **Units and tolerance standard**: mm + ISO, or inch + ASME [`set units`, `set tolerance_standard`].
6. **CAD program** (FreeCAD, Fusion, Inventor, SolidWorks, CATIA, Onshape,
   CadQuery, OpenSCAD, JSCAD …) [`set cad_tool`]. Then do the CAD access check (section 5).
7. **Requirements**: loads, environment (heat, UV, outdoor, chemicals),
   quantity, critical dimensions and fits, cost target. Write them into
   `project/requirements.md`. Prototype: also agree the test plan
   (what to test, pass criteria). Assembly: list parts in `project/bom.csv`.

Then show the filled requirements and ask the user for **G0** approval.

## 4. Working rules

- Default role is **Manager**. Act as Designer or Reviewer only when assigned
  (see ROLES.md). The user always gives the final approval.
- **One session.** The whole project runs in this one chat/session. Never
  open a new chat, session or window yourself (ROL-09).
- **Sub-agents only for reviews.** Designer work stays in this session. If
  your tool can start sub-agents inside this session, use one per review,
  given only the files, `requirements.md` and its role. No sub-agents → do
  the review yourself as a separate step. Prototype: one review is enough.
- Design review has two reviewers: **function** and **DFM** (ROL-06), each
  as its own sub-agent (or step) that sees only the files and requirements,
  not the Designer's reasoning or the other review. Interference, motion
  clearance and assembly access are always checked (ROL-08).
- **Git is optional.** The project works as a plain folder (ZIP download)
  with an AI client or a terminal. Never commit or push unless the user asks.
- Never record an approval the user did not give. Never show a check as passed
  if it was not run. Use `cadctl.py`, do not edit the JSON by hand.
- Cite rule IDs (e.g. `DFM-03`) when you apply or flag a rule.
- **Stop and require a qualified human engineer** at G1 and Release if the
  part is safety-critical: lifting/hanging people or heavy loads overhead,
  pressure vessels, vehicles/aircraft structure, medical contact.
  You may keep helping, but say this clearly (`AI-01`).

## 5. CAD access (after question 6)

Open [rules/06-cad-access.md](rules/06-cad-access.md): check for an MCP tool,
code-based CAD or step-by-step instructions, and the known MCP servers.

## 6. Prototype → production

When a prototype revision is released, the user prints and tests it.
- Test failed or needs changes → `cadctl.py bump` (P01 → P02).
- Test OK → `cadctl.py promote --evidence "<test result>"`. The project moves
  to `production`, revision `R01`; re-check rules for the final process
  (`rules/03`) and get G0 approval again for the final material.
