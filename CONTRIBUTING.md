# Contributing

Keep it small. A change should make the template easier to use, not bigger.

- **Rules:** one line per rule, with a new ID in the file's prefix
  (`DFM-46`). Never reuse or renumber an old ID. Give a number or a
  clear test where possible, not "be careful".
- **README:** change `README.md` and `README.tr.md` together.
- **cadctl.py:** standard library only. Add a test in `tests/` for each change.
- **Before a PR:** run
  `python -m unittest discover -s tests -v` and
  `python scripts/cadctl.py --state examples/MB001-wall-bracket/workflow-state.json next`.
- Add a line to `CHANGELOG.md`.
