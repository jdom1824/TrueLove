"""Small dependency-free coordinator for the True Love Scan MVP.

This service coordinates protocol jobs and records participation. It deliberately
does not generate, receive, store, or recover private keys.
"""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("TRUELOVE_DB", ROOT / "data" / "scan.db"))
HOST = os.getenv("TRUELOVE_HOST", "127.0.0.1")
PORT = int(os.getenv("TRUELOVE_PORT", "8787"))
ALGORITHM_VERSION = os.getenv("TRUELOVE_ALGORITHM", "truelove-v0.1.0")
ONLINE_WINDOW = 90


def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                jobs_claimed INTEGER NOT NULL DEFAULT 0,
                proofs_accepted INTEGER NOT NULL DEFAULT 0,
                operations INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                challenge TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL UNIQUE,
                node_id TEXT NOT NULL,
                operations INTEGER NOT NULL,
                result_digest TEXT NOT NULL,
                submitted_at REAL NOT NULL,
                status TEXT NOT NULL
            );
            """
        )


def payload(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length > 64_000:
        raise ValueError("payload too large")
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003
        return

    def send_json(self, status, body):
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            return self.send_json(HTTPStatus.OK, {"ok": True, "service": "truelove-coordinator"})
        if path == "/api/status":
            now = time.time()
            with db() as connection:
                nodes = connection.execute(
                    "SELECT COUNT(*) FROM nodes WHERE last_seen >= ?", (now - ONLINE_WINDOW,)
                ).fetchone()[0]
                totals = connection.execute(
                    "SELECT COALESCE(SUM(operations), 0), COUNT(*) FROM proofs WHERE status = 'accepted'"
                ).fetchone()
            return self.send_json(
                HTTPStatus.OK,
                {
                    "algorithm": ALGORITHM_VERSION,
                    "nodesOnline": nodes,
                    "verifiedOperations": totals[0],
                    "proofsAccepted": totals[1],
                    "signal": "still-unreachable",
                },
            )
        return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        try:
            data = payload(self)
            if path == "/api/heartbeat":
                return self.heartbeat(data)
            if path == "/api/jobs/claim":
                return self.claim(data)
            if path == "/api/proofs":
                return self.proof(data)
            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def heartbeat(self, data):
        node_id = str(data["nodeId"]).strip()
        if not node_id or len(node_id) > 128:
            raise ValueError("invalid nodeId")
        now = time.time()
        with db() as connection:
            connection.execute(
                "INSERT INTO nodes(node_id, first_seen, last_seen) VALUES (?, ?, ?) "
                "ON CONFLICT(node_id) DO UPDATE SET last_seen=excluded.last_seen",
                (node_id, now, now),
            )
        return self.send_json(HTTPStatus.OK, {"accepted": True, "nodeId": node_id, "serverTime": now})

    def claim(self, data):
        node_id = str(data["nodeId"]).strip()
        now = time.time()
        job_id = f"job-{secrets.token_hex(8)}"
        challenge = secrets.token_hex(32)
        target_id = int(data.get("targetId", (int(now) % 31) + 1))
        with db() as connection:
            connection.execute(
                "INSERT INTO nodes(node_id, first_seen, last_seen, jobs_claimed) VALUES (?, ?, ?, 1) "
                "ON CONFLICT(node_id) DO UPDATE SET last_seen=?, jobs_claimed=jobs_claimed+1",
                (node_id, now, now, now),
            )
            connection.execute(
                "INSERT INTO jobs VALUES (?, ?, ?, ?, ?, 'assigned', ?, ?)",
                (job_id, node_id, target_id, challenge, ALGORITHM_VERSION, now, now + 300),
            )
        return self.send_json(
            HTTPStatus.OK,
            {"jobId": job_id, "targetId": target_id, "challenge": challenge, "algorithm": ALGORITHM_VERSION},
        )

    def proof(self, data):
        job_id = str(data["jobId"])
        node_id = str(data["nodeId"])
        operations = int(data["operations"])
        digest = str(data["resultDigest"])
        if operations <= 0 or not digest or len(digest) > 256:
            raise ValueError("invalid proof")
        now = time.time()
        with db() as connection:
            job = connection.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not job or job["node_id"] != node_id or job["expires_at"] < now:
                return self.send_json(HTTPStatus.CONFLICT, {"accepted": False, "error": "job invalid or expired"})
            try:
                connection.execute(
                    "INSERT INTO proofs(job_id, node_id, operations, result_digest, submitted_at, status) "
                    "VALUES (?, ?, ?, ?, ?, 'accepted')",
                    (job_id, node_id, operations, digest, now),
                )
            except sqlite3.IntegrityError:
                return self.send_json(HTTPStatus.CONFLICT, {"accepted": False, "error": "proof already submitted"})
            connection.execute("UPDATE jobs SET status='accepted' WHERE job_id=?", (job_id,))
            connection.execute(
                "UPDATE nodes SET proofs_accepted=proofs_accepted+1, operations=operations+?, last_seen=? WHERE node_id=?",
                (operations, now, node_id),
            )
        return self.send_json(HTTPStatus.OK, {"accepted": True, "jobId": job_id})


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"True Love coordinator listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
