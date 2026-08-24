"""Coordinator client using the pluggable search engine boundary."""

from __future__ import annotations

import argparse
import json

from .search_engine import DemoSearchEngine, SearchEngine
from .simulator import post


def run_once(base_url: str, node_id: str, engine: SearchEngine, target_id: int = 1,
            range_start: int = 0, range_end: int = 999) -> dict:
    post(base_url, "/api/heartbeat", {"nodeId": node_id})
    job = post(base_url, "/api/jobs/claim", {
        "nodeId": node_id, "targetId": target_id,
        "rangeStart": range_start, "rangeEnd": range_end,
    })
    result = engine.search(job["challenge"], job["rangeStart"], job["rangeEnd"])
    proof = post(base_url, "/api/proofs", {
        "jobId": job["jobId"], "nodeId": node_id,
        "counter": result.operations - 1, "operations": result.operations,
        "resultDigest": result.result_digest,
    })
    return {"job": job, "result": result.__dict__, "proof": proof}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one pluggable search job")
    parser.add_argument("--url", default="http://127.0.0.1:8787")
    parser.add_argument("--node-id", default="computer-client")
    parser.add_argument("--target-id", type=int, default=1)
    parser.add_argument("--range-start", type=int, default=0)
    parser.add_argument("--range-end", type=int, default=999)
    args = parser.parse_args()
    result = run_once(args.url, args.node_id, DemoSearchEngine(), args.target_id,
                      args.range_start, args.range_end)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
