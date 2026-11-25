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
  review  design|release PASS|FAIL --evidence TEXT [--by NAME]
  block ID / unblock ID       Add/remove a blocking issue (e.g. F-001)
  bump                        Next revision (P01 -> P02); approvals reset
  promote --evidence TEXT     Prototype passed: move to production, R01

No third-party dependencies. Python 3.9+.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE = ROOT / "project" / "workflow-state.json"
DEFAULT_RELEASE = ROOT / "project" / "release"

GATES = ("G0", "G1", "RELEASE")
REVIEWS = ("design", "release")
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
    if not ok(r["design"], "PASS", rev):
        return ("Designer, then Reviewer", f"Design {rev}, then independent design review",
                'cadctl.py review design PASS --evidence "<review file / findings>"')
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
    if state["phase"] == "prototype":
        return ("User", f"Print and test {rev}. Failed: bump. OK: promote.",
                'cadctl.py promote --evidence "<test result>"   # or: cadctl.py bump')
    return ("-", f"{rev} released. Nothing missing.", "cadctl.py bump   # for the next change")


# ---------- state changes ----------

def set_field(state, field, value):
    if field == "deliverables":
        state["deliverables"] = [v.strip().lower() for v in value.split(",") if v.strip()] if value else []
        return
    if field not in CHOICES and field not in TEXT_FIELDS:
        raise StateError(f"unknown field {field!r}")
    state[field] = value or None


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
        if not ok(r["design"], "PASS", rev):
            errors.append(f"design review not PASS for {rev}")
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
    state["deliverables"] = []
    reset_approvals(state)


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
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    release_root = Path(args.release_dir) if args.release_dir else state_path.parent / "release"
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
            problems = []
            if state.get("project_code") and state.get("revision") and \
                    ok(state["gates"]["G1"], "APPROVED", state["revision"]):
                problems = release_file_errors(state, release_root)
            if problems:
                print("FAIL\n  " + "\n  ".join(problems)); return 1
            print("OK")
        elif args.cmd == "name":
            print(output_name(state, args.part)); changed = False
        elif args.cmd == "set":
            set_field(state, args.field, args.value)
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
            print("Promoted to production R01. Set target material if needed, then G0 again.")
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
