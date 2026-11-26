<p align="center">
  <img src="assets/banner.svg" alt="CAD for Anything: design mechanical parts with any AI and any CAD program" width="100%">
</p>

<p align="center">
  <b>English</b> · <a href="README.tr.md">Türkçe</a>
</p>

<p align="center">
  <a href="https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml"><img src="https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml/badge.svg" alt="ci"></a>
  <img src="https://img.shields.io/badge/version-v0.4.1-1d4f7a" alt="version v0.4.1">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776ab?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen" alt="no dependencies">
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-read-lightgrey" alt="changelog"></a>
</p>

A small template for designing mechanical parts and assemblies — 3D printing,
CNC and sheet metal — together with **any AI assistant** and **any CAD program**
(FreeCAD, Fusion, Inventor, SolidWorks, CATIA, Onshape, CadQuery …).

| 💬 Ask | 📐 Design | 🔍 Review | 📦 Release |
| :---: | :---: | :---: | :---: |
| The AI asks short questions in order and writes the requirements | You (or the AI through MCP / code) build the model | Two reviewers check function and manufacturing | Named, checked and locked files for the workshop |

## 🚀 Quick start

1. Click **Use this template** to make your own copy.
2. Give the repo link to any AI chat and say:
   *"I want to design a part with this."*
3. The AI reads [AGENTS.md](AGENTS.md), asks a few questions in order, and
   guides you step by step. You build the model in your CAD program.

## ⚙️ How it works

- 🖨️ **Optional FDM prototype first.** The first question is: *print and test an
  FDM prototype first?* If yes, the part is designed to be printable
  (`P01`, `P02` …). When the print works, the project moves to the real
  material and process (`R01`).
- 👥 **Roles:** Manager (questions, records), Designer (model, exports) and
  two independent reviewers — **function** (strength, fits, interference,
  motion clearance) and **DFM** (can it be made and assembled).
  Everything runs in **one session**; the AI may use sub-agents inside it,
  but never opens a new chat by itself. See [ROLES.md](ROLES.md).
- 🚦 **Three gates, all approved by you:** G0 requirements → G1 design →
  RELEASE manufacturing files.
- 📏 **Short rules with IDs** in [rules/](rules/README.md): material (MAT),
  tolerances (TOL), DFM, drawings (DWG), naming (REV).
- 🌳 **Parts list / product tree:** `project/bom.csv`, checked and drawn by
  `cadctl.py bom` (see the [example](examples/MB001-wall-bracket/README.md)).
- 🔒 **Released files are locked:** hashes are stored at RELEASE; any later
  change is reported and needs a new revision.

### 🗺️ Workflow

```mermaid
flowchart TD
    A([Start: give the repo link to an AI]) --> B{FDM prototype first?}
    B -- yes --> P[Prototype phase<br/>P01, FDM-printable]
    B -- no --> R[Production phase<br/>R01, final process]
    P --> Q
    R --> Q
    Q[Questions: part, code, material,<br/>units, CAD program] --> C{CAD reachable<br/>via MCP or code?}
    C -- yes --> C1[AI models directly]
    C -- no --> C2[AI gives step-by-step<br/>CAD instructions]
    C1 --> G0
    C2 --> G0
    G0{{G0: user approves requirements}} --> D[Design]
    D --> RV[Two independent reviews<br/>function + DFM]
    RV -- FAIL --> D
    RV -- PASS --> G1{{G1: user approves design}}
    G1 --> E[Export STEP / STL / PDF / DXF<br/>+ release review]
    E --> REL{{RELEASE: user approves files}}
    REL --> T{Prototype?}
    T -- no --> DONE([Send to manufacturing])
    T -- yes --> PT{Print and test OK?}
    PT -- "no: bump P02" --> D
    PT -- "yes: promote R01" --> G0
    classDef gate fill:#ffcc4d,stroke:#b38600,color:#000
    classDef done fill:#5aa9e6,stroke:#1d4f7a,color:#fff
    class G0,G1,REL gate
    class A,DONE done
```

### 👥 One session, many roles

The whole project stays in **one chat/session**. The Manager talks to you;
Designer and reviewer work can go to sub-agents inside the same session
(`ROL-09`). Without sub-agents the AI plays the roles one after another.

```mermaid
flowchart LR
    U((You)) <--> M[Manager<br/>questions, records,<br/>asks for approvals]
    subgraph S[One session]
        M
        M -- task --> D[Designer<br/>model, exports]
        M -- files only --> RF[Reviewer: function<br/>strength, fits,<br/>interference, motion]
        M -- files only --> RD[Reviewer: DFM<br/>makeable, assemblable]
        D -- result --> M
        RF -- PASS / FAIL --> M
        RD -- PASS / FAIL --> M
    end
    M --> ST[(workflow-state.json<br/>via cadctl.py)]
    classDef you fill:#ffcc4d,stroke:#b38600,color:#000
    class U you
```

### 💬 What a session looks like

```mermaid
sequenceDiagram
    actor U as You
    participant M as Manager
    participant D as Designer
    participant R as Reviewers
    U->>M: "I want to design a part with this."
    M->>U: FDM prototype first? Part? Code? Material? Units? CAD program?
    U->>M: Answers
    M->>U: Requirements ready. Approve G0?
    U->>M: Yes
    M->>D: Model the part
    D-->>M: Model + screenshots / files
    M->>R: Review function and DFM (files only)
    R-->>M: PASS (or FAIL with F-001 …)
    M->>U: Reviews PASS. Approve G1?
    U->>M: Yes
    D-->>M: STEP / STL / PDF / DXF
    M->>U: Files checked. Approve RELEASE?
```

### 🔁 Revisions: prototype → production

```mermaid
flowchart LR
    P1[P01<br/>FDM print] -- test failed: bump --> P2[P02<br/>FDM print]
    P2 -- test OK: promote --> R1[R01<br/>final material]
    R1 -- change after release: bump --> R2[R02]
    classDef proto fill:#7fc4f5,stroke:#1d4f7a,color:#000
    classDef prod fill:#2a6fa8,stroke:#0f2742,color:#fff
    class P1,P2 proto
    class R1,R2 prod
```

## 🛠️ The helper tool

No dependencies, Python 3.10+.

```
python scripts/cadctl.py next      # what to do now, who does it, which command
python scripts/cadctl.py status    # project state
python scripts/cadctl.py check     # release files present and named right?
python scripts/cadctl.py bom       # product tree from project/bom.csv (--mermaid for a diagram)
```

Other commands: `set`, `approve`, `review`, `block`, `unblock`, `bump`,
`promote`, `name`. Run `python scripts/cadctl.py -h`.

Example output (from the [MB001 example](examples/MB001-wall-bracket/README.md)):

```
$ python scripts/cadctl.py next
Next (User): Approve design (G1) for R01
  python scripts/cadctl.py approve G1 --evidence "<where the user approved>"

$ python scripts/cadctl.py bom
MB001-00  Wall bracket kit  [assembly]
|-- 1 x MB001-01  Bracket  [make: S235 steel, 2 mm, zinc plated, sheet-metal]
|-- 2 x SCREW-6X50  Wood screw  [buy: 6 x 50 mm, pan head, zinc]
`-- 2 x PLUG-8  Wall plug  [buy: 8 mm nylon]
```

The same tree with `bom --mermaid`:

```mermaid
flowchart TD
    n0[["MB001-00<br/>Wall bracket kit"]]
    n1["MB001-01<br/>Bracket"]
    n2(["SCREW-6X50<br/>Wood screw"])
    n3(["PLUG-8<br/>Wall plug"])
    n0 -- "1x" --> n1
    n0 -- "2x" --> n2
    n0 -- "2x" --> n3
```

## 🔌 CAD access (optional)

After you name your CAD program, the AI checks whether it can reach it
through an MCP server. If not, it shows you known MCP servers for your program
and asks whether to set one up or continue with step-by-step instructions.
List and details: [AGENTS.md, section 5](AGENTS.md#5-cad-access-check-after-question-6).

| CAD program | How the AI works with it |
| :--- | :--- |
| Fusion · Inventor · SolidWorks · CATIA · Onshape · FreeCAD | 🔌 MCP server if connected, otherwise 📝 step-by-step instructions |
| CadQuery (code) | 🐍 The AI writes and runs a script in `project/cad/` |
| Anything else | 📝 Step-by-step instructions; you send screenshots or files back |

## 📁 Files

| Path | What |
| :--- | :--- |
| `AGENTS.md` | Instructions for the AI: what to read, what to ask |
| `ROLES.md` | Roles, gates, prototype → production flow |
| `rules/` | Rule files |
| `project/` | Your project: `requirements.md`, `workflow-state.json`, `bom.csv`, `cad/` (optional model scripts), `release/` |
| `examples/MB001-wall-bracket/` | Filled example |
| `scripts/cadctl.py` | State, next step, gate checks |
| `assets/` | Images for the README |

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Update both `README.md` and
`README.tr.md` when you change the README.
