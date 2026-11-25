# 05 · Naming and revision (REV)

- **REV-01** — Every project has a code chosen by the user (e.g. `MB001`).
  Only letters, digits and `_`.
- **REV-02** — Revisions: prototype `P01`, `P02` …; production `R01`, `R02` ….
  The first production revision after a prototype is always `R01`.
- **REV-03** — File names: `<CODE>-<REV>.<ext>` for a single part
  (`MB001-P01.stl`). Assembly parts add a two-digit part number:
  `<CODE>-<NN>-<REV>.<ext>` (`MB001-02-R01.step`). The assembly itself is `-00`.
  `cadctl.py name` prints the prefix.
- **REV-04** — Any change to a released revision makes a new revision
  (`cadctl.py bump`). Never overwrite files in a released folder.
- **REV-05** — Record what changed and why in `requirements.md` → "Revision
  history" (one line per revision).
