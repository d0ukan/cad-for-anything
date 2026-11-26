#!/usr/bin/env python3
"""cadctl - show project state, the next step, and check gates.

Commands:
  status                      Show the project state
  next                        Show the next missing step and who does it
  check                       Validate state and release files (exit 1 on problems)
  name [--part NN]            Print the file name prefix (e.g. MB001-P01)
  set FIELD [VALUE]           Set a field (omit VALUE to clear)
  approve G0|G1|RELEASE --evidence TEXT [--by NAME]
  revoke  G0|G1|RELEASE
  review  function|dfm|release PASS|FAIL --evidence TEXT [--by NAME]
  block ID / unblock ID       Add/remove a blocking issue (e.g. F-001)
  bump                        Next revision (P01 -> P02); approvals reset
  promote --evidence TEXT     Prototype passed: move to production, R01
  bom [--mermaid]             Check bom.csv and print the product tree

No third-party dependencies. Python 3.10+.
"""
import argparse
import csv
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE = ROOT / "project" / "workflow-state.json"
DEFAULT_RELEASE = ROOT / "project" / "release"

GATES = ("G0", "G1", "RELEASE")
REVIEWS = ("function", "dfm", "release")
DESIGN_REVIEWS = ("function", "dfm")
PHASES = ("prototype", "production")
PROCESSES = ("fdm", "sla", "sls", "cnc", "sheet-metal", "other")
CHOICES = {
    "phase": PHASES,
    "units": ("mm", "inch"),
    "tolerance_standard": ("ISO", "ASME"),
    "process": PROCESSES,
    "target_process": PROCESSES,
}
TEXT_FIELDS = ("project_name", "project_code", "revision", "cad_tool", "material")
DEFAULT_DELIVERABLES = {
    "fdm": ["step", "stl"], "sla": ["step", "stl"], "sls": ["step", "stl"],
    "cnc": ["step", "pdf"], "sheet-metal": ["step", "pdf", "dxf"], "other": ["step"],
}
REV_RE = {"prototype": re.compile(r"^P\d{2}$"), "production": re.compile(r"^R\d{2}$")}
CODE_RE = re.compile(r"^[A-Za-z0-9_]+$")
# Changing one of these after G0 means the requirements changed: approvals reset.
REQUIREMENT_FIELDS = ("phase", "units", "tolerance_standard", "process", "target_process", "material")
BOM_COLUMNS = ("part_number", "name", "qty", "parent", "type", "material_spec", "process", "notes")
BOM_TYPES = ("assembly", "make", "buy")


class StateError(Exception):
    pass


def empty_record():
    return {"status": "PENDING", "revision": None, "evidence": None, "by": None, "date": None}


def today():
    return datetime.date.today().isoformat()


# ---------- load / save / validate ----------

def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except FileNotFoundError:
        raise StateError(f"state file not found: {path}")
    except json.JSONDecodeError as e:
        raise StateError(f"invalid JSON in {path}: {e}")
    errors = validate(state)
    if errors:
        raise StateError("invalid state:\n  " + "\n  ".join(errors))
    return state


def save_state(path, state):
    errors = validate(state)
    if errors:
        raise StateError("refusing to save invalid state:\n  " + "\n  ".join(errors))
    Path(path).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(state):
    errors = []
    if not isinstance(state, dict):
        return ["state must be a JSON object"]
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field, allowed in CHOICES.items():
        value = state.get(field)
        if value is not None and value not in allowed:
            errors.append(f"{field} must be one of {', '.join(allowed)} (got {value!r})")
    code = state.get("project_code")
    if code is not None and not CODE_RE.match(str(code)):
        errors.append("project_code: only letters, digits and _ (REV-01)")
    phase, rev = state.get("phase"), state.get("revision")
    if rev is not None:
        if phase is None:
            errors.append("set phase before revision")
        elif not REV_RE[phase].match(str(rev)):
            errors.append(f"revision {rev!r} does not match phase {phase} (REV-02: P01.. / R01..)")
    if phase == "prototype" and state.get("process") not in (None, "fdm"):
        errors.append("prototype phase uses process fdm (MAT-02)")
    if not isinstance(state.get("deliverables", []), list):
        errors.append("deliverables must be a list")
    for group, names, ok in (("gates", GATES, "APPROVED"), ("reviews", REVIEWS, "PASS")):
        records = state.get(group)
        if not isinstance(records, dict):
            errors.append(f"{group} missing")
            continue
        for name in names:
            rec = records.get(name)
            if not isinstance(rec, dict):
                errors.append(f"{group}.{name} missing")
                continue
            allowed = ("PENDING", ok) + (("FAIL",) if group == "reviews" else ())
            if rec.get("status") not in allowed:
                errors.append(f"{group}.{name}.status must be one of {', '.join(allowed)}")
            if rec.get("status") != "PENDING" and not rec.get("evidence"):
                errors.append(f"{group}.{name} needs evidence")
    if not isinstance(state.get("blocking_issues", []), list):
        errors.append("blocking_issues must be a list")
    return errors


# ---------- helpers ----------

def deliverables(state):
    if state.get("deliverables"):
        return [d.lower() for d in state["deliverables"]]
    return DEFAULT_DELIVERABLES.get(state.get("process") or "other", ["step"])


def output_name(state, part=None):
    code, rev = state.get("project_code"), state.get("revision")
    if not code or not rev:
        raise StateError("project_code and revision must be set first")
    if part is not None:
        if not re.match(r"^\d{2}$", part):
            raise StateError("part number must be two digits, e.g. 01")
        return f"{code}-{part}-{rev}"
    return f"{code}-{rev}"


def ok(record, status, revision):
    return record["status"] == status and record["revision"] == revision


def release_dir(state, release_root):
    return Path(release_root) / output_name(state)


def release_file_errors(state, release_root):
    """Missing or badly named files in project/release/<CODE>-<REV>/ (DWG-01, REV-03)."""
    folder = release_dir(state, release_root)
    if not folder.is_dir():
        return [f"release folder missing: {folder}"]
    code, rev = re.escape(state["project_code"]), re.escape(state["revision"])
    pattern = re.compile(rf"^{code}(-\d{{2}})?-{rev}\.([A-Za-z0-9]+)$", re.IGNORECASE)
    found, errors = set(), []
    for f in sorted(folder.iterdir()):
        if f.is_dir() or f.name.upper() in ("NOTES.MD", ".GITKEEP"):
            continue
        m = pattern.match(f.name)
        if not m:
            errors.append(f"bad file name (REV-03): {f.name}")
        else:
            found.add(m.group(2).lower())
    for ext in deliverables(state):
        if ext not in found:
            errors.append(f"missing deliverable .{ext} in {folder.name}/")
    return errors


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def release_hashes(state, release_root):
    folder = release_dir(state, release_root)
    return {f.name: sha256(f) for f in sorted(folder.iterdir())
            if f.is_file() and f.name.upper() != ".GITKEEP"}


def released_changes(state, release_root):
    """Files changed after RELEASE approval (REV-04). Empty if not released."""
    rec = state["gates"]["RELEASE"]
    if not ok(rec, "APPROVED", state.get("revision")) or "files" not in rec:
        return []
    if not release_dir(state, release_root).is_dir():
        return ["release folder deleted after RELEASE"]
    now, then = release_hashes(state, release_root), rec["files"]
    changes = [f"changed after RELEASE: {n}" for n in then if n in now and now[n] != then[n]]
    changes += [f"deleted after RELEASE: {n}" for n in then if n not in now]
    changes += [f"added after RELEASE: {n}" for n in now if n not in then]
    return changes


def design_review_missing(state):
    """Production needs both function and dfm PASS; prototype needs at least one.
    A FAIL on the current revision always blocks."""
    rev, r = state.get("revision"), state["reviews"]
    failed = [k for k in DESIGN_REVIEWS if ok(r[k], "FAIL", rev)]
    if failed:
        return [f"{k} (FAIL, fix and re-review)" for k in failed]
    passed = [k for k in DESIGN_REVIEWS if ok(r[k], "PASS", rev)]
    if state.get("phase") == "prototype":
        return [] if passed else ["function or dfm"]
    return [k for k in DESIGN_REVIEWS if k not in passed]


def g0_missing(state):
    missing = [f for f in ("project_name", "project_code", "phase", "revision",
                           "units", "tolerance_standard", "cad_tool", "process", "material")
               if not state.get(f)]
    return missing


# ---------- next step ----------

def next_step(state, release_root):
    """Return (who, what, command) for the first missing step."""
    rev = state.get("revision")
    if not state.get("phase"):
        return ("Manager", "Ask: FDM prototype first? (AGENTS.md question 1)",
                "cadctl.py set phase prototype   # or: production")
    for field in ("project_name", "project_code", "revision"):
        if not state.get(field):
            example = {"revision": "P01" if state["phase"] == "prototype" else "R01"}.get(field, "<value>")
            return ("Manager", f"Ask the user for {field}", f"cadctl.py set {field} {example}")
    for field in ("process", "material", "units", "tolerance_standard", "cad_tool"):
        if not state.get(field):
            hint = "fdm" if field == "process" and state["phase"] == "prototype" else "<value>"
            return ("Manager", f"Ask the user for {field}", f"cadctl.py set {field} {hint}")
    g = state["gates"]
    r = state["reviews"]
    if not ok(g["G0"], "APPROVED", rev):
        return ("User", f"Approve requirements (G0) for {rev}",
                'cadctl.py approve G0 --evidence "<where the user approved>"')
    missing = design_review_missing(state)
    if missing:
        return ("Designer, then Reviewers", f"Design {rev}, then independent review: "
                + " / ".join(missing) + " (ROLES.md ROL-06)",
                f'cadctl.py review {missing[0].split()[0]} PASS --evidence "<review file>"')
    if state.get("blocking_issues"):
        return ("Designer", "Fix blocking issues: " + ", ".join(state["blocking_issues"]),
                "cadctl.py unblock <ID>")
    if not ok(g["G1"], "APPROVED", rev):
        return ("User", f"Approve design (G1) for {rev}",
                'cadctl.py approve G1 --evidence "<where the user approved>"')
    errors = release_file_errors(state, release_root)
    if errors:
        return ("Designer", "Export release files (rules/04): " + "; ".join(errors),
                "cadctl.py check")
    if not ok(r["release"], "PASS", rev):
        return ("Reviewer", "Review release files", 'cadctl.py review release PASS --evidence "<...>"')
    if not ok(g["RELEASE"], "APPROVED", rev):
        return ("User", f"Approve release of {rev}", 'cadctl.py approve RELEASE --evidence "<...>"')
    changes = released_changes(state, release_root)
    if changes:
        return ("Manager", "Released files changed (REV-04): " + "; ".join(changes),
                "cadctl.py bump   # make a new revision instead")
    if state["phase"] == "prototype":
        return ("User", f"Print and test {rev} against the test plan. Failed: bump. OK: promote.",
                'cadctl.py promote --evidence "<test result>"   # or: cadctl.py bump')
    return ("-", f"{rev} released. Nothing missing.", "cadctl.py bump   # for the next change")


# ---------- state changes ----------

def set_field(state, field, value):
    if field == "deliverables":
        state["deliverables"] = [v.strip().lower() for v in value.split(",") if v.strip()] if value else []
        return
    if field not in CHOICES and field not in TEXT_FIELDS:
        raise StateError(f"unknown field {field!r}")
    value = value or None
    warning = None
    if (field in REQUIREMENT_FIELDS and state.get(field) != value
            and ok(state["gates"]["G0"], "APPROVED", state.get("revision"))):
        reset_approvals(state)
        warning = f"{field} changed after G0: approvals and reviews reset, get G0 again"
    state[field] = value
    return warning


def gate_errors(state, gate, release_root):
    rev = state.get("revision")
    g, r = state["gates"], state["reviews"]
    errors = []
    if gate == "G0":
        missing = g0_missing(state)
        if missing:
            errors.append("missing: " + ", ".join(missing))
    if gate in ("G1", "RELEASE") and not ok(g["G0"], "APPROVED", rev):
        errors.append(f"G0 not approved for {rev}")
    if gate == "G1":
        errors.extend(f"design review missing: {m}" for m in design_review_missing(state))
        if state.get("blocking_issues"):
            errors.append("open blocking issues: " + ", ".join(state["blocking_issues"]))
    if gate == "RELEASE":
        if not ok(g["G1"], "APPROVED", rev):
            errors.append(f"G1 not approved for {rev}")
        if not ok(r["release"], "PASS", rev):
            errors.append(f"release review not PASS for {rev}")
        errors.extend(release_file_errors(state, release_root))
    return errors


def record(rec, status, revision, evidence, by):
    if not evidence or not evidence.strip():
        raise StateError("--evidence is required (ROL-05)")
    rec.update(status=status, revision=revision, evidence=evidence.strip(), by=by, date=today())


def approve(state, gate, evidence, by, release_root):
    errors = gate_errors(state, gate, release_root)
    if errors:
        raise StateError(f"cannot approve {gate}:\n  " + "\n  ".join(errors))
    record(state["gates"][gate], "APPROVED", state["revision"], evidence, by or "user")
    if gate == "RELEASE":
        state["gates"][gate]["files"] = release_hashes(state, release_root)


def review(state, kind, status, evidence, by):
    if not state.get("revision"):
        raise StateError("revision must be set first")
    if kind == "release" and not ok(state["gates"]["G1"], "APPROVED", state["revision"]):
        raise StateError("release review needs G1 first (ROL-02)")
    record(state["reviews"][kind], status, state["revision"], evidence, by or "reviewer")


def reset_approvals(state):
    for name in GATES:
        state["gates"][name] = empty_record()
    for name in REVIEWS:
        state["reviews"][name] = empty_record()


def bump(state):
    rev = state.get("revision")
    if not rev:
        raise StateError("revision must be set first")
    new = f"{rev[0]}{int(rev[1:]) + 1:02d}"
    state["history"].append({"revision": rev, "date": today(), "event": f"bump to {new}"})
    state["revision"] = new
    reset_approvals(state)
    return new


def promote(state, evidence, release_root):
    if state.get("phase") != "prototype":
        raise StateError("promote works only in the prototype phase")
    if not ok(state["gates"]["RELEASE"], "APPROVED", state["revision"]):
        raise StateError("prototype revision must be released before promote")
    if not evidence or not evidence.strip():
        raise StateError("--evidence is required: describe the prototype test result")
    state["history"].append({"revision": state["revision"], "date": today(),
                             "event": "prototype passed, promoted to production",
                             "evidence": evidence.strip()})
    state["phase"] = "production"
    state["revision"] = "R01"
    state["process"] = state.get("target_process")
    state["material"] = None  # prototype material is not the final one (MAT-07)
    state["deliverables"] = []
    reset_approvals(state)


# ---------- BOM / product tree ----------

def read_bom(path):
    """Return rows of bom.csv, or [] if the file is missing or has no rows."""
    path = Path(path)
    if not path.is_file():
        return []
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            header = [h.strip() for h in (reader.fieldnames or [])]
            missing = [c for c in BOM_COLUMNS[:5] if c not in header]
            if missing:
                raise StateError(f"{path.name}: missing columns {', '.join(missing)}")
            rows = []
            for line, row in enumerate(reader, start=2):
                row = {(k or "").strip(): (v or "").strip() for k, v in row.items()
                       if not isinstance(v, list)}
                if any(row.values()):
                    row["_line"] = line
                    rows.append(row)
            return rows
    except UnicodeDecodeError:
        raise StateError(f"{path.name}: save it as UTF-8")


def bom_errors(rows, code=None):
    errors, parts = [], {}
    for row in rows:
        where = f"line {row['_line']}"
        pn = row.get("part_number", "")
        if not pn:
            errors.append(f"{where}: part_number empty")
            continue
        if pn in parts:
            errors.append(f"{where}: duplicate part_number {pn}")
        parts[pn] = row
        if row.get("type") not in BOM_TYPES:
            errors.append(f"{where}: type must be one of {', '.join(BOM_TYPES)}")
        if not re.match(r"^[1-9]\d*$", row.get("qty", "")):
            errors.append(f"{where}: qty must be a whole number > 0")
        if row.get("type") == "make" and not (row.get("material_spec") and row.get("process")):
            errors.append(f"{where}: make part {pn} needs material_spec and process (MAT-05)")
        if (code and row.get("type") in ("assembly", "make")
                and not re.match(rf"^{re.escape(code)}-\d{{2}}$", pn)):
            errors.append(f"{where}: {pn} should be {code}-NN (REV-03)")
    if errors:
        return errors
    roots = [pn for pn, row in parts.items() if not row.get("parent")]
    if parts and len(roots) != 1:
        errors.append(f"need exactly one top item without parent (found {len(roots)})")
    for pn, row in parts.items():
        parent = row.get("parent")
        if parent and parent not in parts:
            errors.append(f"line {row['_line']}: parent {parent} not found")
        elif parent and parts[parent].get("type") != "assembly":
            errors.append(f"line {row['_line']}: parent {parent} is not an assembly")
        seen, cur = set(), pn
        while cur in parts and parts[cur].get("parent"):
            if cur in seen:
                errors.append(f"cycle in parents at {pn}")
                break
            seen.add(cur)
            cur = parts[cur]["parent"]
    return errors


def bom_tree(rows):
    """Text tree (ASCII) plus total quantities of buy parts."""
    children = {}
    for row in rows:
        children.setdefault(row.get("parent", ""), []).append(row)
    lines, totals = [], {}

    def label(row):
        extra = ", ".join(x for x in (row.get("material_spec"), row.get("process")) if x)
        return f"{row['part_number']}  {row['name']}  [{row['type']}{': ' + extra if extra else ''}]"

    def walk(row, prefix, last, mult):
        qty = int(row["qty"])
        total = qty * mult
        if row["type"] == "buy":
            totals[row["part_number"]] = totals.get(row["part_number"], 0) + total
        lines.append(f"{prefix}{'`-- ' if last else '|-- '}{qty} x {label(row)}")
        kids = children.get(row["part_number"], [])
        for i, kid in enumerate(kids):
            walk(kid, prefix + ("    " if last else "|   "), i == len(kids) - 1, total)

    for root in children.get("", []):
        lines.append(label(root))
        kids = children.get(root["part_number"], [])
        for i, kid in enumerate(kids):
            walk(kid, "", i == len(kids) - 1, int(root["qty"]))
    if totals:
        lines += ["", "Buy list (total qty):"]
        lines += [f"  {n:>4} x {pn}" for pn, n in totals.items()]
    return "\n".join(lines)


def bom_mermaid(rows):
    """Mermaid flowchart of the product tree, for README or review."""
    ids = {row["part_number"]: f"n{i}" for i, row in enumerate(rows)}
    shape = {"assembly": ("[[", "]]"), "make": ("[", "]"), "buy": ("([", "])")}
    out = ["flowchart TD"]
    for row in rows:
        a, b = shape.get(row["type"], ("[", "]"))
        text = f"{row['part_number']}<br/>{row['name']}".replace('"', "'")
        out.append(f'    {ids[row["part_number"]]}{a}"{text}"{b}')
    for row in rows:
        if row.get("parent") in ids:
            out.append(f'    {ids[row["parent"]]} -- "{row["qty"]}x" --> {ids[row["part_number"]]}')
    return "\n".join(out)


# ---------- CLI ----------

def cmd_status(state, args):
    rev = state.get("revision")
    print(f"Project : {state.get('project_name') or '-'} ({state.get('project_code') or '-'})")
    print(f"Phase   : {state.get('phase') or '-'}   Revision: {rev or '-'}")
    print(f"Process : {state.get('process') or '-'}   Material: {state.get('material') or '-'}"
          f"   Final process: {state.get('target_process') or '-'}")
    print(f"Units   : {state.get('units') or '-'} / {state.get('tolerance_standard') or '-'}"
          f"   CAD: {state.get('cad_tool') or '-'}")
    print(f"Files   : {', '.join(deliverables(state))}")
    for group in ("gates", "reviews"):
        for name, rec in state[group].items():
            stale = " (old revision)" if rec["revision"] and rec["revision"] != rev else ""
            print(f"  {name:<8} {rec['status']:<9} {rec['revision'] or ''}{stale}")
    print(f"Blocking: {', '.join(state['blocking_issues']) or 'none'}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--release-dir", default=None,
                        help="release root (default: release/ next to the state file)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("status", "next", "check", "bump"):
        sub.add_parser(name)
    p = sub.add_parser("name"); p.add_argument("--part")
    p = sub.add_parser("set"); p.add_argument("field"); p.add_argument("value", nargs="?")
    p = sub.add_parser("approve"); p.add_argument("gate", choices=GATES)
    p.add_argument("--evidence", required=True); p.add_argument("--by")
    p = sub.add_parser("revoke"); p.add_argument("gate", choices=GATES)
    p = sub.add_parser("review"); p.add_argument("kind", choices=REVIEWS)
    p.add_argument("status", choices=("PASS", "FAIL"))
    p.add_argument("--evidence", required=True); p.add_argument("--by")
    p = sub.add_parser("block"); p.add_argument("id")
    p = sub.add_parser("unblock"); p.add_argument("id")
    p = sub.add_parser("promote"); p.add_argument("--evidence", required=True)
    p = sub.add_parser("bom"); p.add_argument("--mermaid", action="store_true")
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    release_root = Path(args.release_dir) if args.release_dir else state_path.parent / "release"
    bom_path = state_path.parent / "bom.csv"
    try:
        state = load_state(state_path)
        changed = True
        if args.cmd == "status":
            cmd_status(state, args); changed = False
        elif args.cmd == "next":
            who, what, cmd = next_step(state, release_root)
            print(f"Next ({who}): {what}\n  python scripts/{cmd}"); changed = False
        elif args.cmd == "check":
            changed = False
            problems = bom_errors(read_bom(bom_path), state.get("project_code"))
            if state.get("project_code") and state.get("revision") and \
                    ok(state["gates"]["G1"], "APPROVED", state["revision"]):
                problems += release_file_errors(state, release_root)
                problems += released_changes(state, release_root)
            if problems:
                print("FAIL\n  " + "\n  ".join(problems)); return 1
            print("OK")
        elif args.cmd == "name":
            print(output_name(state, args.part)); changed = False
        elif args.cmd == "set":
            warning = set_field(state, args.field, args.value)
            if warning:
                print(f"WARNING: {warning}")
        elif args.cmd == "bom":
            changed = False
            rows = read_bom(bom_path)
            if not rows:
                print(f"no parts in {bom_path.name} (single-part projects may skip the BOM)")
                return 0
            errors = bom_errors(rows, state.get("project_code"))
            if errors:
                print("FAIL\n  " + "\n  ".join(errors))
                return 1
            print(bom_mermaid(rows) if args.mermaid else bom_tree(rows))
        elif args.cmd == "approve":
            approve(state, args.gate, args.evidence, args.by, release_root)
        elif args.cmd == "revoke":
            state["gates"][args.gate] = empty_record()
        elif args.cmd == "review":
            review(state, args.kind, args.status, args.evidence, args.by)
        elif args.cmd == "block":
            if args.id not in state["blocking_issues"]:
                state["blocking_issues"].append(args.id)
        elif args.cmd == "unblock":
            if args.id not in state["blocking_issues"]:
                raise StateError(f"{args.id} is not open")
            state["blocking_issues"].remove(args.id)
        elif args.cmd == "bump":
            print(f"New revision: {bump(state)}")
        elif args.cmd == "promote":
            promote(state, args.evidence, release_root)
            print("Promoted to production R01. Set final process and material, then G0 again.")
        if changed:
            save_state(state_path, state)
            if args.cmd not in ("bump", "promote"):
                print("saved")
    except StateError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
