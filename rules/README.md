# Rules index

Each rule has an ID (e.g. `DFM-03`). Cite the ID when you apply or break a rule.
Open a file only at the step that needs it.

| File | Prefix | Open when |
| :--- | :--- | :--- |
| [01-material-process.md](01-material-process.md) | MAT | Before G0 (choosing process and material) |
| [02-tolerances-fits.md](02-tolerances-fits.md) | TOL | Design and review, when parts mate, move or a dimension is critical (interference: TOL-09…11) |
| [03-dfm.md](03-dfm.md) | DFM | Design and review — only the section for your process |
| [04-drawings-delivery.md](04-drawings-delivery.md) | DWG | After G1, before export |
| [05-naming-revision.md](05-naming-revision.md) | REV | Project start and every export |
| [06-cad-access.md](06-cad-access.md) | CAD | After the user names the CAD program (MCP check, known servers) |

## General rules (always)

- **AI-01** — Safety-critical parts (loads over people, lifting, pressure,
  vehicle/aircraft structure, medical contact): a qualified human engineer
  must approve G1 and RELEASE. Say this clearly; do not hide it.
- **AI-02** — Do not invent material data, machine limits or prices. If you
  are not sure, say so and give the source to check.
- **AI-03** — Show calculations (stress, deflection, fit) with inputs,
  formula and safety factor, so the user and Reviewer can check them.
- **AI-04** — Keep answers short. Ask only questions that change the design.
- **AI-05** — The user's own decisions in `requirements.md` override defaults here.
- **AI-06** — With CAD access (MCP server or code, `rules/06`), the AI may model and
  export directly, but: work only in the user's project files, ask before
  overwriting or deleting a model, save the model source or a STEP after
  each change, and never skip a gate or review because the AI built the
  model itself.
