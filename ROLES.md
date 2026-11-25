# Roles and gates

Roles are not models or products. One AI can play all roles in separate
steps, or you can use separate chats/agents. The **user** has the final say.

| Role | Does | May change design files? |
| :--- | :--- | :---: |
| **Manager** | Asks questions, keeps `requirements.md` and `workflow-state.json`, asks for approvals | No |
| **Designer** | Models the part (or guides the user in CAD), exports files | Yes |
| **Reviewer** | Checks the design against requirements and `rules/`, independently | No |
| **User** | Gives inputs, approves gates | Final authority |

## Gates

| Gate | Meaning | Needs before approval |
| :--- | :--- | :--- |
| **G0** | Requirements approved | Phase, project code, revision, units, process, material, `requirements.md` filled |
| **G1** | Design approved | G0 for this revision, Reviewer `design PASS`, no open blocking issues |
| **RELEASE** | Manufacturing files approved | G1, exported files in `project/release/<CODE>-<REV>/`, Reviewer `release PASS` |

Every approval and review is tied to one revision. A new revision
(`bump`, `promote`) needs new approvals.

## Flow

```
            ┌──────────── prototype phase (FDM, P01, P02 …) ───────────┐
G0 → design → review → G1 → export → review → RELEASE → print & test
                                                              │
                         test fails: bump (P02) ◄─────────────┤
                         test OK: promote → production phase (R01)
                                   G0 → design → review → G1 → export → review → RELEASE
```

Without a prototype, the project starts directly in the production phase.

## Rules for roles

- **ROL-01** — Manager does not start design before G0.
- **ROL-02** — Designer does not export release files before G1.
- **ROL-03** — Reviewer works from files and requirements only, not from the
  Designer's explanation. Reviewer lists findings as `F-001`, `F-002` … with
  rule ID, severity (blocking / minor) and fix.
- **ROL-04** — A blocking finding is recorded with `cadctl.py block F-001`
  and removed with `unblock` only after the fix is reviewed.
- **ROL-05** — Evidence for each approval/review is something real: a file
  name, a commit, a chat message date, a photo of the test.
