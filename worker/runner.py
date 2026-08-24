"""Continuous safe worker runner for soak tests.

The work remains a deterministic hash exercise; this runner does not generate
wallets or handle private keys.
"""

from __future__ import annotations

import argparse
import json
import time

from .simulator import deterministic_work, post


def run_for(base_url: str, node_id: str, duration_seconds: int, target_id: int = 1,
            operations: int = 1000, heartbeat_interval: int = 30) -> dict:
    started = time.monotonic()
    deadline = started + duration_seconds
    next_heartbeat = 0.0
    jobs = 0
    proofs = 0
    verified_operations = 0

    while time.monotonic() < deadline:
        now = time.monotonic()
        if now >= next_heartbeat:
            post(base_url, "/api/heartbeat", {"nodeId": node_id})
            next_heartbeat = now + heartbeat_interval

        job = post(base_url, "/api/jobs/claim", {"nodeId": node_id, "targetId": target_id})
        counter, digest = deterministic_work(job["challenge"], operations)
        post(base_url, "/api/proofs", {
            "jobId": job["jobId"],
            "nodeId": node_id,
            "counter": counter,
            "operations": operations,
            "resultDigest": digest,
        })
        jobs += 1
        proofs += 1
        verified_operations += operations

    return {
        "nodeId": node_id,
        "durationSeconds": round(time.monotonic() - started, 2),
        "jobs": jobs,
        "proofs": proofs,
        "verifiedOperations": verified_operations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a continuous safe True Love soak test")
    parser.add_argument("--url", default="http://127.0.0.1:8787")
    parser.add_argument("--node-id", default="computer-runner")
    parser.add_argument("--target-id", type=int, default=1)
    parser.add_argument("--duration", type=int, default=300, help="duration in seconds")
    parser.add_argument("--operations", type=int, default=1000)
    parser.add_argument("--heartbeat-interval", type=int, default=30)
    args = parser.parse_args()
    result = run_for(args.url, args.node_id, args.duration, args.target_id,
                     args.operations, args.heartbeat_interval)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
