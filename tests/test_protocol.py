import hashlib
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from coordinator import server
from worker.client import run_once as run_client_once
from worker.search_engine import DemoSearchEngine
from worker.runner import run_for
from worker.simulator import run_once


class ProtocolTests(unittest.TestCase):
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

    def test_worker_completes_reproducible_job(self):
        result = run_once(self.url, "computer-test", target_id=17, operations=8)
        self.assertTrue(result["proof"]["accepted"])
        status = json.loads(urlopen(self.url + "/api/status").read())
        self.assertEqual(status["proofsAccepted"], 1)
        self.assertEqual(status["verifiedOperations"], 8)

    def test_wrong_digest_is_rejected(self):
        _, job = self.post("/api/jobs/claim", {"nodeId": "bad-worker", "targetId": 1})
        with self.assertRaises(HTTPError) as error:
            self.post(
                "/api/proofs",
                {
                    "jobId": job["jobId"],
                    "nodeId": "bad-worker",
                    "rangeStart": 0,
                    "rangeEnd": 4,
                    "counter": 4,
                    "operations": 5,
                    "resultDigest": hashlib.sha256(b"tampered").hexdigest(),
                },
            )
        self.assertEqual(error.exception.code, 409)

    def test_runner_completes_multiple_jobs(self):
        result = run_for(self.url, "runner-test", duration_seconds=1, operations=2, heartbeat_interval=1)
        self.assertGreater(result["jobs"], 0)
        self.assertEqual(result["jobs"], result["proofs"])

    def test_pluggable_search_client_uses_assigned_range(self):
        result = run_client_once(self.url, "client-test", DemoSearchEngine(),
                                 target_id=17, range_start=100, range_end=109)
        self.assertTrue(result["proof"]["accepted"])
        self.assertEqual(result["job"]["rangeStart"], 100)
        self.assertEqual(result["job"]["rangeEnd"], 109)

    def test_overlapping_ranges_are_rejected(self):
        self.post("/api/heartbeat", {"nodeId": "overlap-a"})
        self.post("/api/jobs/claim", {"nodeId": "overlap-a", "targetId": 17,
                                       "rangeStart": 0, "rangeEnd": 9})
        with self.assertRaises(HTTPError) as error:
            self.post("/api/jobs/claim", {"nodeId": "overlap-b", "targetId": 17,
                                           "rangeStart": 9, "rangeEnd": 20})
        self.assertEqual(error.exception.code, 409)


if __name__ == "__main__":
    unittest.main()
