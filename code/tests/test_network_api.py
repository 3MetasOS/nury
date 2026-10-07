import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import network_api as api  # noqa: E402


def call(method, path, obj=None):
    s, ct, b = api.handle(method, path, json.dumps(obj).encode() if obj is not None else b"")
    return s, json.loads(b)


GOOD = {"name": "Test Aid", "kind": "legal_aid", "languages": ["es"], "city": "Aurora", "state": "CO", "phone": "(303) 555-0111"}


class Api(unittest.TestCase):
    def setUp(self):
        os.environ.pop("NURY_DEMO_NETWORK", None)
        self.dir = tempfile.mkdtemp()
        os.environ["NURY_NETWORK_DIR"] = self.dir

    def tearDown(self):
        os.environ.pop("NURY_NETWORK_DIR", None)
        os.environ.pop("NURY_DEMO_NETWORK", None)
        shutil.rmtree(self.dir)

    def test_crud_home_import_export_and_plain_errors(self):
        s, snap = call("GET", "/api/network")
        self.assertEqual((s, snap["entries"], snap["fictional"]), (200, [], False))
        self.assertIn("legal_aid", snap["kinds"])
        s, e = call("POST", "/api/network", GOOD)
        self.assertEqual(s, 201)
        s, e2 = call("PUT", f"/api/network/{e['id']}", {"phone": "(303) 555-0122", "tags": ["detention"]})
        self.assertEqual((s, e2["phone"], e2["tags"]), (200, "(303) 555-0122", ["detention"]))
        s, e3 = call("POST", f"/api/network/{e['id']}/used")
        self.assertEqual(s, 200)
        self.assertRegex(e3["last_used"], r"^\d{4}-\d{2}-\d{2}$")
        s, snap = call("POST", "/api/network/home", {"city": "Aurora", "state": "Colorado"})
        self.assertEqual(snap["home"], {"city": "Aurora", "state": "CO"})
        self.assertEqual(len(snap["entries"]), 1)
        s, err = call("POST", "/api/network", {"name": "No contact"})
        self.assertEqual(s, 400)
        self.assertIn("phone or a link", err["error"])
        s, exp = call("GET", "/api/network/export")
        self.assertEqual(len(exp["entries"]), 1)
        s, imp = call("POST", "/api/network/import", {"entries": [dict(GOOD, name="Second Aid", phone="(303) 555-0133")]})
        self.assertEqual((s, imp["added"], len(imp["entries"])), (200, 1, 2))
        s, imp = call("POST", "/api/network/import", {"entries": [GOOD, {"name": "bad"}]})
        self.assertEqual(s, 400)
        s, _ = call("DELETE", f"/api/network/{e['id']}")
        self.assertEqual(s, 200)
        self.assertEqual(call("DELETE", "/api/network/nope")[0], 400)
        self.assertEqual(call("GET", "/api/nothing")[0], 404)
        s, ct, b = api.handle("POST", "/api/network", b"{not json")
        self.assertEqual(s, 400)

    def test_demo_is_read_only_and_flagged(self):
        os.environ["NURY_DEMO_NETWORK"] = "1"
        s, snap = call("GET", "/api/network")
        self.assertTrue(snap["fictional"] and snap["readonly"])
        self.assertTrue(all("(fictional)" in e["name"] for e in snap["entries"]))
        for m, p in (("POST", "/api/network"), ("PUT", "/api/network/demo-aurora-legal"), ("DELETE", "/api/network/demo-aurora-legal"),
                     ("POST", "/api/network/home"), ("POST", "/api/network/import")):
            s, err = call(m, p, GOOD)
            self.assertEqual(s, 403, p)
            self.assertIn("fictional", err["error"])


if __name__ == "__main__":
    unittest.main()
