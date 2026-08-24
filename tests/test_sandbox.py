import hashlib
import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from coordinator import server
from worker.client import run_once as run_client_once
from worker.search_engine import (
    DemoSearchEngine,
    SandboxSearchEngine,
    SearchResult,
    _derive_sandbox_address,
)


SANDBOX_ADDRESS = "0x60a95e05db8953103bf385151b609e2f6731a3a7"


class SandboxSearchEngineUnitTests(unittest.TestCase):
    """Unit tests for SandboxSearchEngine (no coordinator needed)."""

    def test_search_returns_valid_digest(self):
        engine = SandboxSearchEngine()
        result = engine.search("abc123", 0, 9)
        self.assertEqual(result.operations, 10)
        self.assertEqual(result.cursor, 9)
        expected = hashlib.sha256("abc123:0:9:10".encode()).hexdigest()
        self.assertEqual(result.result_digest, expected)

    def test_search_invalid_range_raises(self):
        engine = SandboxSearchEngine()
        with self.assertRaises(ValueError):
            engine.search("abc", -1, 5)
        with self.assertRaises(ValueError):
            engine.search("abc", 10, 5)

    def test_match_address_when_target_matches(self):
        engine = SandboxSearchEngine()
        result = engine.search("challenge", 100, 100)
        self.assertIsNotNone(result.match_address)
        self.assertEqual(result.match_address.lower(), SANDBOX_ADDRESS)

    def test_derived_address_matches_constant(self):
        address = _derive_sandbox_address()
        self.assertEqual(address.lower(), SANDBOX_ADDRESS)

    def test_search_result_is_frozen_dataclass(self):
        engine = SandboxSearchEngine()
        result = engine.search("x", 0, 0)
        with self.assertRaises(AttributeError):
            result.operations = 999

    def test_sandbox_engine_is_search_engine_subclass(self):
        from worker.search_engine import SearchEngine
        engine = SandboxSearchEngine()
        self.assertIsInstance(engine, SearchEngine)


class SandboxIntegrationTests(unittest.TestCase):
    """Integration tests that start a real coordinator server."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.temp_dir.name) / "scan.db"
        server.init_db()
        self.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"

    def tearDown(self):
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()
        self.temp_dir.cleanup()

    def post(self, path, body):
        request = Request(
            self.url + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            return response.status, json.loads(response.read())

    def test_sandbox_job_successful(self):
        engine = SandboxSearchEngine()
        result = run_client_once(
            self.url, "sandbox-client", engine,
            target_id=1, range_start=0, range_end=4,
        )
        self.assertTrue(result["proof"]["accepted"])
        self.assertEqual(result["job"]["rangeStart"], 0)
        self.assertEqual(result["job"]["rangeEnd"], 4)
        self.assertEqual(result["result"]["operations"], 5)

    def test_sandbox_proof_accepted(self):
        engine = SandboxSearchEngine()
        result = run_client_once(
            self.url, "sandbox-proof", engine,
            target_id=1, range_start=10, range_end=19,
        )
        self.assertTrue(result["proof"]["accepted"])
        self.assertEqual(result["proof"]["jobId"], result["job"]["jobId"])
        status = json.loads(urlopen(self.url + "/api/status").read())
        self.assertGreaterEqual(status["proofsAccepted"], 1)

    def test_sandbox_wrong_digest_rejected(self):
        engine = SandboxSearchEngine()
        post = self.post
        post("/api/heartbeat", {"nodeId": "bad-sandbox"})
        _, job = post("/api/jobs/claim", {
            "nodeId": "bad-sandbox", "targetId": 1,
            "rangeStart": 0, "rangeEnd": 4,
        })
        with self.assertRaises(HTTPError) as error:
            post("/api/proofs", {
                "jobId": job["jobId"],
                "nodeId": "bad-sandbox",
                "rangeStart": 0,
                "rangeEnd": 4,
                "counter": 4,
                "operations": 5,
                "resultDigest": hashlib.sha256(b"tampered").hexdigest(),
            })
        self.assertEqual(error.exception.code, 409)

    def test_sandbox_range_validation_server_side(self):
        engine = SandboxSearchEngine()
        with self.assertRaises(HTTPError) as ctx:
            run_client_once(
                self.url, "sandbox-range", engine,
                target_id=1, range_start=-1, range_end=5,
            )
        self.assertEqual(ctx.exception.code, 400)

    def test_sandbox_range_validation_engine_side(self):
        engine = SandboxSearchEngine()
        with self.assertRaises(ValueError):
            engine.search("challenge", -1, 5)
        with self.assertRaises(ValueError):
            engine.search("challenge", 10, 5)

    def test_sandbox_match_address_in_result(self):
        engine = SandboxSearchEngine()
        result = run_client_once(
            self.url, "sandbox-match", engine,
            target_id=1, range_start=100, range_end=100,
        )
        self.assertEqual(
            result["result"]["match_address"].lower(), SANDBOX_ADDRESS
        )
        self.assertEqual(result["proof"]["matchAddress"].lower(), SANDBOX_ADDRESS)

    def test_private_key_never_in_proof_response(self):
        engine = SandboxSearchEngine()
        result = run_client_once(
            self.url, "sandbox-leak", engine,
            target_id=1, range_start=100, range_end=100,
        )
        proof_str = json.dumps(result["proof"])
        self.assertNotIn("private", proof_str.lower())
        self.assertNotIn("seed", proof_str.lower())
        self.assertNotIn("key", proof_str.lower())

    def test_private_key_never_in_database(self):
        engine = SandboxSearchEngine()
        run_client_once(
            self.url, "sandbox-db", engine,
            target_id=1, range_start=100, range_end=100,
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            rows = conn.execute("SELECT * FROM proofs").fetchall()
            for row in rows:
                row_str = str(row).lower()
                self.assertNotIn("private", row_str)
                self.assertNotIn("seed", row_str)
                self.assertNotIn("pbkdf2", row_str)

    def test_private_key_never_in_job_response(self):
        engine = SandboxSearchEngine()
        result = run_client_once(
            self.url, "sandbox-job-leak", engine,
            target_id=1, range_start=100, range_end=100,
        )
        job_str = json.dumps(result["job"])
        self.assertNotIn("private", job_str.lower())
        self.assertNotIn("seed", job_str.lower())


class SandboxVsDemoComparisonTests(unittest.TestCase):
    """Verify SandboxSearchEngine produces the same proof format as DemoSearchEngine."""

    def test_same_digest_as_demo(self):
        challenge = "test-challenge-42"
        start, end = 0, 99
        demo = DemoSearchEngine()
        sandbox = SandboxSearchEngine()
        demo_result = demo.search(challenge, start, end)
        sandbox_result = sandbox.search(challenge, start, end)
        self.assertEqual(demo_result.result_digest, sandbox_result.result_digest)
        self.assertEqual(demo_result.operations, sandbox_result.operations)
        self.assertEqual(demo_result.cursor, sandbox_result.cursor)

    def test_sandbox_has_match_address(self):
        engine = SandboxSearchEngine()
        result = engine.search("x", 100, 100)
        self.assertIsNotNone(result.match_address)


if __name__ == "__main__":
    unittest.main()
