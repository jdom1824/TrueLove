"""Search engine boundary.

The coordinator and worker protocol are independent from the search algorithm.
The default engine is safe deterministic demo work. Replace only
``UserSearchEngine.search`` with an authorized implementation; it must return
public results and must never persist or print private material.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    operations: int
    cursor: int
    result_digest: str
    match_address: str | None = None


class SearchEngine:
    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        raise NotImplementedError


class DemoSearchEngine(SearchEngine):
    """Safe engine used for client-server tests; it does not generate wallets."""

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        if start < 0 or end < start:
            raise ValueError("invalid search range")
        operations = end - start + 1
        digest = hashlib.sha256(f"{challenge}:{operations - 1}".encode()).hexdigest()
        return SearchResult(operations, end, digest)


class UserSearchEngine(SearchEngine):
    """Insert the authorized search implementation here.

    This method intentionally fails closed until the implementation is supplied.
    Keep candidate secrets local and ephemeral; return only public match data.
    """

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        # TODO: insert the authorized algorithm here.
        raise NotImplementedError("UserSearchEngine is not configured")
