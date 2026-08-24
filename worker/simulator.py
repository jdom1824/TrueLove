"""Safe local worker simulator for protocol testing.

This deliberately hashes a coordinator challenge. It does not generate wallets
or handle private keys.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from urllib.request import Request, urlopen


def post(base_url: str, path: str, body: dict) -> dict:
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:  # noqa: S310 - configured coordinator URL
        return json.loads(response.read().decode("utf-8"))


def deterministic_work(challenge: str, operations: int) -> tuple[int, str]:
    counter = operations - 1
    digest = hashlib.sha256(f"{challenge}:{counter}".encode("utf-8")).hexdigest()
    return counter, digest


def run_once(base_url: str, node_id: str, target_id: int = 1, operations: int = 5) -> dict:
    post(base_url, "/api/heartbeat", {"nodeId": node_id})
    job = post(base_url, "/api/jobs/claim", {"nodeId": node_id, "targetId": target_id})
    counter, digest = deterministic_work(job["challenge"], operations)
    proof = post(
        base_url,
        "/api/proofs",
        {
            "jobId": job["jobId"],
            "nodeId": node_id,
            "counter": counter,
            "operations": operations,
            "resultDigest": digest,
        },
    )
    return {"job": job, "proof": proof}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one safe True Love protocol job")
    parser.add_argument("--url", default="http://127.0.0.1:8787")
    parser.add_argument("--node-id", default="computer-local")
    parser.add_argument("--target-id", type=int, default=1)
    parser.add_argument("--operations", type=int, default=5)
    args = parser.parse_args()
    started = time.time()
    result = run_once(args.url, args.node_id, args.target_id, args.operations)
    result["elapsedMs"] = round((time.time() - started) * 1000, 2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
