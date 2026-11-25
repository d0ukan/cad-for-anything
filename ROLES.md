# Roles and gates

Roles are not models or products. One AI can play all roles in separate
steps, or you can use separate chats/agents. The **user** has the final say.

| Role | Does | May change design files? |
| :--- | :--- | :---: |
| **Manager** | Asks questions, keeps `requirements.md` and `workflow-state.json`, asks for approvals | No |
| **Designer** | Models the part (or guides the user in CAD), exports files | Yes |
| **Reviewer – function** | Strength, fits, tolerances, requirements met? | No |
| **Reviewer – DFM** | Can the chosen process make it? (`rules/03`) | No |
| **User** | Gives inputs, approves gates | Final authority |

## Gates

| Gate | Meaning | Needs before approval |
| :--- | :--- | :--- |
| **G0** | Requirements approved | Phase, project code, revision, units, process, material, `requirements.md` filled |
| **G1** | Design approved | G0 for this revision, design reviews PASS (ROL-06), no open blocking issues, Manager checklist (ROL-07) |
| **RELEASE** | Manufacturing files approved | G1, exported files in `project/release/<CODE>-<REV>/`, Reviewer `release PASS` |

Every approval and review is tied to one revision. A new revision
(`bump`, `promote`) needs new approvals.

## Flow

```
            ┌──────────── prototype phase (FDM, P01, P02 …) ───────────┐
G0 → design → 2 reviews → G1 → export → review → RELEASE → print & test
                                                              │
                         test fails: bump (P02) ◄─────────────┤
                         test OK: promote → production phase (R01)
                                   G0 → design → 2 reviews → G1 → export → review → RELEASE
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
- **ROL-06** — Two design reviewers, each in a separate session/chat and
  without seeing the other's report: **function** (`review function`) and
  **DFM** (`review dfm`). Production phase needs both PASS. Prototype phase
  needs at least one (the print test is the second check). Any FAIL blocks G1.
  The release review (`review release`) is done by one reviewer.
- **ROL-07** — Before asking for G1, the Manager does not re-review the
  design. It checks each line of `requirements.md` against the reviewer
  reports, lists anything not covered, and confirms the reviews are PASS.
