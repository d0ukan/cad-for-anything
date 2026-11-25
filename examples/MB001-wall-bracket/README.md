# Example: MB001 wall bracket

A shelf bracket that went through two FDM prototypes and then moved to
2 mm laser-cut, bent sheet steel.

| File | What it shows |
| :--- | :--- |
| [requirements.md](requirements.md) | Filled requirements, revision history P01 → P02 → R01 |
| [review.md](review.md) | Reviewer findings in `F-001` format with rule IDs |
| [workflow-state.json](workflow-state.json) | State: production R01, G0 and design review done, G1 waiting |

No CAD files are included; the example shows the process, not the model.

Try it:

```
python scripts/cadctl.py --state examples/MB001-wall-bracket/workflow-state.json status
python scripts/cadctl.py --state examples/MB001-wall-bracket/workflow-state.json next
```
