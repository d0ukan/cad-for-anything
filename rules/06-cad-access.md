# 06 · CAD access (CAD)

Open after the user names the CAD program (AGENTS.md question 6).

- **CAD-01** — Look at your own tools. Is an MCP tool for the chosen CAD
  program connected? Call a harmless read-only tool (e.g. list open
  documents) to confirm it works. Do not guess.
- **CAD-02** — Connected → tell the user; as Designer build and change the
  model through it (`AI-06`).
- **CAD-03** — Not connected → show the options for their program from the
  table below and ask: *set up an MCP server, or continue with step-by-step
  instructions?* Never install anything without the user's yes.
- **CAD-04** — Code-based CAD (CadQuery, OpenSCAD, JSCAD …): no MCP needed if
  you can run code. Write the script in `project/cad/`, run it, export
  STEP/STL (OpenSCAD, JSCAD: STL/3MF only, no STEP). All run on Windows,
  macOS and Linux. Examples: `examples/MB001-wall-bracket/cad/`.
- **CAD-05** — Nothing available → step-by-step CAD instructions (sketch,
  constraints, features, dimensions); the user sends screenshots,
  measurements or exported files back.
- **CAD-06** — Record the result in `requirements.md` → Identity → CAD
  program (e.g. "Fusion, via MCP" or "SolidWorks, manual"). Gates and
  reviews stay the same in all cases.

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
| CadQuery, OpenSCAD, JSCAD | Not needed (code) | — |
