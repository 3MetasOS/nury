"""The 'how to add a rule' note must not drift: run the example code that is in it."""
import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonet  # noqa: E402,F401

DOC = Path(__file__).resolve().parents[2] / "documents" / "product" / "ADD_A_RULE.md"


class Doc(unittest.TestCase):
    def blocks(self):
        return re.findall(r"```python\n(.*?)```", DOC.read_text(encoding="utf-8"), re.S)

    def test_the_example_check_and_its_test_run_as_written(self):
        code, test = self.blocks()[0], self.blocks()[1]
        ns = {}
        exec(code, ns)                                   # the check, exactly as the note shows it
        self.assertIn("no_shouting", ns)

        class T(unittest.TestCase):
            no_shouting = staticmethod(ns["no_shouting"])
        g = {"SimpleNamespace": SimpleNamespace, "no_shouting": ns["no_shouting"]}
        exec("class T(__import__('unittest').TestCase):\n" + "\n".join("    " + ln for ln in test.splitlines()) + "\n", g)
        res = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(unittest.defaultTestLoader.loadTestsFromTestCase(g["T"]))
        self.assertTrue(res.wasSuccessful())

    def test_the_example_is_not_in_the_product_and_the_steps_name_real_files(self):
        from nury import checks
        self.assertNotIn("no_shouting", checks.REGISTRY)
        root = Path(__file__).resolve().parents[2]
        for shown, real in (("code/nury/checks.py", "code/nury/checks.py"), ("code/nury/rules.py", "code/nury/rules.py"),
                            ("code/nury/guardrails.py", "code/nury/guardrails.py"), ("tests/test_core.py", "code/tests/test_core.py")):
            self.assertTrue((root / real).is_file(), real)
            self.assertIn(shown, DOC.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
