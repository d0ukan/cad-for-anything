# Roles and gates

Roles are not models or products. Everything runs in one session: the
Manager plays the other roles itself, step by step, or gives them to
sub-agents inside the same session (ROL-09). The **user** has the final say.

| Role | Does | May change design files? |
| :--- | :--- | :---: |
| **Manager** | Asks questions, keeps `requirements.md` and `workflow-state.json`, asks for approvals | No |
| **Designer** | Models the part (or guides the user in CAD), keeps `bom.csv`, exports files | Yes |
| **Reviewer – function** | Strength, fits, tolerances, interference and motion clearance, requirements met? | No |
| **Reviewer – DFM** | Can the chosen process make it, and can it be assembled? (`rules/03`) | No |
| **User** | Gives inputs, approves gates | Final authority |

## Gates

| Gate | Meaning | Needs before approval |
| :--- | :--- | :--- |
| **G0** | Requirements approved | Project name and code, phase, revision, units, tolerance standard, CAD program, process, material, `requirements.md` filled |
| **G1** | Design approved | G0 for this revision, design reviews PASS (ROL-06), no open blocking issues, Manager checklist (ROL-07) |
| **RELEASE** | Manufacturing files approved | G1, exported files in `project/release/<CODE>-<REV>/`, Reviewer `release PASS` |

Every approval and review is tied to one revision. A new revision
(`bump`, `promote`) needs new approvals. Changing a requirement field
(process, material, units …) after G0 resets all approvals.

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
- **ROL-06** — Two design reviewers, each as a separate sub-agent or step,
  seeing only the files and requirements, not the Designer's reasoning or
  the other's report: **function** (`review function`) and
  **DFM** (`review dfm`). Production phase needs both PASS. Prototype phase
  needs at least one (the print test is the second check). Any FAIL blocks G1.
  The release review (`review release`) is done by one reviewer.
- **ROL-07** — Before asking for G1, the Manager does not re-review the
  design. It checks each line of `requirements.md` against the reviewer
  reports, lists anything not covered, and confirms the reviews are PASS.
- **ROL-08** — Fixed review scope for anything with a mating part:
  function reviewer — TOL-08 stack, TOL-09 interference, TOL-10 motion,
  TOL-11 worst case; DFM reviewer — DFM-05 assembly access and order,
  DFM-06 wrong-way assembly. Each report lists these checks with result or
  "n/a + reason". Without CAD access the reviewer asks the user to run the
  CAD interference check and send the result; no PASS before it arrives.
- **ROL-09** — One session per project. The AI never opens a new chat,
  session or window by itself. Sub-agents inside the session are allowed
  for Designer and Reviewer work; the Manager stays in the main session,
  records results with `cadctl.py` and asks the user for every approval.
