# Rules index

Each rule has an ID (e.g. `DFM-03`). Cite the ID when you apply or break a rule.
Open a file only at the step that needs it.

| File | Prefix | Open when |
| :--- | :--- | :--- |
| [01-material-process.md](01-material-process.md) | MAT | Before G0 (choosing process and material) |
| [02-tolerances-fits.md](02-tolerances-fits.md) | TOL | Design, when parts mate or a dimension is critical |
| [03-dfm.md](03-dfm.md) | DFM | Design and review — only the section for your process |
| [04-drawings-delivery.md](04-drawings-delivery.md) | DWG | After G1, before export |
| [05-naming-revision.md](05-naming-revision.md) | REV | Project start and every export |

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
