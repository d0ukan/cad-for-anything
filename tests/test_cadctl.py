import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import cadctl  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.state = self.tmp / "workflow-state.json"
        shutil.copy(ROOT / "project" / "workflow-state.json", self.state)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cadctl.main(["--state", str(self.state), *args])
        return code, out.getvalue() + err.getvalue()

    def ok(self, *args):
        code, out = self.run_cli(*args)
        self.assertEqual(code, 0, out)
        return out

    def fill_prototype(self):
        for field, value in (("phase", "prototype"), ("project_name", "Bracket"),
                             ("project_code", "MB001"), ("revision", "P01"),
                             ("process", "fdm"), ("material", "PETG"), ("units", "mm"),
                             ("tolerance_standard", "ISO"), ("cad_tool", "FreeCAD"),
                             ("target_process", "sheet-metal")):
            self.ok("set", field, value)

    def make_files(self, prefix, exts):
        folder = self.tmp / "release" / prefix
        folder.mkdir(parents=True, exist_ok=True)
        for ext in exts:
            (folder / f"{prefix}.{ext}").write_text("x")

    def release_current(self, prefix, exts):
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "function", "PASS", "--evidence", "review.md")
        self.ok("review", "dfm", "PASS", "--evidence", "review.md")
        self.ok("approve", "G1", "--evidence", "chat")
        self.make_files(prefix, exts)
        self.ok("review", "release", "PASS", "--evidence", "review.md")
        self.ok("approve", "RELEASE", "--evidence", "chat")


class TestTemplate(Base):
    def test_template_is_valid_and_empty(self):
        state = cadctl.load_state(ROOT / "project" / "workflow-state.json")
        self.assertIsNone(state["project_code"])
        self.assertIn("FDM prototype first", self.ok("next"))

    def test_example_is_valid(self):
        state = cadctl.load_state(ROOT / "examples" / "MB001-wall-bracket" / "workflow-state.json")
        self.assertEqual(state["phase"], "production")


class TestValidation(Base):
    def test_revision_must_match_phase(self):
        self.ok("set", "phase", "prototype")
        code, out = self.run_cli("set", "revision", "R01")
        self.assertEqual(code, 1)
        self.assertIn("REV-02", out)

    def test_prototype_must_be_fdm(self):
        self.ok("set", "phase", "prototype")
        code, out = self.run_cli("set", "process", "cnc")
        self.assertEqual(code, 1)
        self.assertIn("MAT-02", out)

    def test_bad_choice_and_unknown_field(self):
        self.assertEqual(self.run_cli("set", "units", "cm")[0], 1)
        self.assertEqual(self.run_cli("set", "colour", "red")[0], 1)

    def test_bad_project_code(self):
        self.assertEqual(self.run_cli("set", "project_code", "MB 001")[0], 1)

    def test_broken_json(self):
        self.state.write_text("{", encoding="utf-8")
        code, out = self.run_cli("status")
        self.assertEqual(code, 1)
        self.assertIn("invalid JSON", out)


class TestGates(Base):
    def test_g0_needs_inputs(self):
        self.ok("set", "phase", "prototype")
        code, out = self.run_cli("approve", "G0", "--evidence", "chat")
        self.assertEqual(code, 1)
        self.assertIn("project_code", out)

    def test_g1_needs_design_review(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        code, out = self.run_cli("approve", "G1", "--evidence", "chat")
        self.assertEqual(code, 1)
        self.assertIn("design review", out)

    def test_blocking_issue_stops_g1(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "dfm", "PASS", "--evidence", "r")
        self.ok("block", "F-001")
        self.assertEqual(self.run_cli("approve", "G1", "--evidence", "chat")[0], 1)
        self.assertIn("F-001", self.ok("next"))
        self.ok("unblock", "F-001")
        self.ok("approve", "G1", "--evidence", "chat")

    def test_release_needs_files(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "dfm", "PASS", "--evidence", "r")
        self.ok("approve", "G1", "--evidence", "chat")
        self.make_files("MB001-P01", ["step"])
        code, out = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn(".stl", out)

    def test_bad_file_name_reported(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "dfm", "PASS", "--evidence", "r")
        self.ok("approve", "G1", "--evidence", "chat")
        self.make_files("MB001-P01", ["step", "stl"])
        (self.tmp / "release" / "MB001-P01" / "bracket_final.stl").write_text("x")
        code, out = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("bracket_final.stl", out)

    def test_evidence_required(self):
        self.fill_prototype()
        self.assertEqual(self.run_cli("approve", "G0", "--evidence", " ")[0], 1)


class TestTwoReviewers(Base):
    def go_production(self):
        self.fill_prototype()
        self.release_current("MB001-P01", ["step", "stl"])
        self.ok("promote", "--evidence", "test ok")
        self.ok("approve", "G0", "--evidence", "chat")

    def test_prototype_needs_one_review(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.assertIn("function or dfm", self.ok("next"))
        self.ok("review", "function", "PASS", "--evidence", "r")
        self.ok("approve", "G1", "--evidence", "chat")

    def test_production_needs_both(self):
        self.go_production()
        self.ok("review", "function", "PASS", "--evidence", "r")
        code, out = self.run_cli("approve", "G1", "--evidence", "chat")
        self.assertEqual(code, 1)
        self.assertIn("dfm", out)
        self.ok("review", "dfm", "PASS", "--evidence", "r")
        self.ok("approve", "G1", "--evidence", "chat")

    def test_fail_blocks_even_in_prototype(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "function", "PASS", "--evidence", "r")
        self.ok("review", "dfm", "FAIL", "--evidence", "overhang 70 deg")
        code, out = self.run_cli("approve", "G1", "--evidence", "chat")
        self.assertEqual(code, 1)
        self.assertIn("dfm (FAIL", out)


class TestFlow(Base):
    def test_full_prototype_to_production(self):
        self.fill_prototype()
        self.release_current("MB001-P01", ["step", "stl"])
        self.assertIn("promote", self.ok("next"))

        self.ok("bump")
        state = cadctl.load_state(self.state)
        self.assertEqual(state["revision"], "P02")
        self.assertEqual(state["gates"]["G0"]["status"], "PENDING")

        self.release_current("MB001-P02", ["step", "stl"])
        self.ok("promote", "--evidence", "fit OK on wall, 5 kg held")
        state = cadctl.load_state(self.state)
        self.assertEqual((state["phase"], state["revision"], state["process"]),
                         ("production", "R01", "sheet-metal"))
        self.assertEqual(len(state["history"]), 2)

        self.ok("set", "material", "S235 2 mm, zinc plated")
        self.release_current("MB001-R01", ["step", "pdf", "dxf"])
        self.assertIn("Nothing missing", self.ok("next"))

    def test_promote_needs_release(self):
        self.fill_prototype()
        self.assertEqual(self.run_cli("promote", "--evidence", "ok")[0], 1)

    def test_name(self):
        self.fill_prototype()
        self.assertEqual(self.ok("name").strip(), "MB001-P01")
        self.assertEqual(self.ok("name", "--part", "02").strip(), "MB001-02-P01")

    def test_assembly_part_files_accepted(self):
        self.fill_prototype()
        self.ok("approve", "G0", "--evidence", "chat")
        self.ok("review", "dfm", "PASS", "--evidence", "r")
        self.ok("approve", "G1", "--evidence", "chat")
        folder = self.tmp / "release" / "MB001-P01"
        folder.mkdir(parents=True)
        for n in ("MB001-00-P01.step", "MB001-01-P01.stl", "NOTES.md"):
            (folder / n).write_text("x")
        self.assertIn("OK", self.ok("check"))


class TestDocs(unittest.TestCase):
    def test_llms_links_point_to_files(self):
        text = (ROOT / "llms.txt").read_text(encoding="utf-8")
        paths = re.findall(r"raw\.githubusercontent\.com/d0ukan/cad-for-anything/main/([^)\s]+)", text)
        self.assertTrue(paths)
        for p in paths:
            self.assertTrue((ROOT / p).is_file(), p)

    def test_rule_ids_unique(self):
        seen = {}
        for f in sorted((ROOT / "rules").glob("*.md")):
            for rid in re.findall(r"\*\*([A-Z]{2,4}-\d{2})\*\*", f.read_text(encoding="utf-8")):
                self.assertNotIn(rid, seen, f"{rid} in {f.name} and {seen.get(rid)}")
                seen[rid] = f.name
        self.assertIn("MAT-01", seen)

    def test_cited_rule_ids_exist(self):
        defined = set()
        for f in list((ROOT / "rules").glob("*.md")) + [ROOT / "ROLES.md"]:
            defined |= set(re.findall(r"\*\*([A-Z]{2,4}-\d{2})\*\*", f.read_text(encoding="utf-8")))
        files = [ROOT / "AGENTS.md", ROOT / "ROLES.md", ROOT / "scripts" / "cadctl.py"]
        files += list((ROOT / "rules").glob("*.md"))
        for f in files:
            for rid in re.findall(r"\b((?:MAT|TOL|DFM|DWG|REV|AI|ROL)-\d{2})\b", f.read_text(encoding="utf-8")):
                self.assertIn(rid, defined, f"{rid} cited in {f.name}")


if __name__ == "__main__":
    unittest.main()
