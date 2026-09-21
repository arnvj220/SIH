"""
Stateful stores used by detection checks.

Replay detection needs to know if a session has been consumed.
Unauthorized verification needs to know who is allowed to verify
what. Both are in-memory for the prototype; the interfaces are
designed so a DB-backed implementation can substitute later.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ReplayStore:
    """
    Tracks consumed verification contexts.

    The key is any identity that must be unique per verification:
    typically (session_id, nonce). Once consumed, a repeat is a replay.
    """

    # key -> timestamp when first consumed
    _consumed: dict[tuple[str, str], float] = field(default_factory=dict)

    def _key(self, session_id: str, nonce: str) -> tuple[str, str]:
        return (session_id, nonce)

    def is_consumed(self, session_id: str, nonce: str) -> bool:
        return self._key(session_id, nonce) in self._consumed

    def consume(self, session_id: str, nonce: str) -> bool:
        """
        Mark a (session, nonce) as used. Returns True if it was new,
        False if it was already consumed (i.e. a replay).
        """
        key = self._key(session_id, nonce)
        if key in self._consumed:
            return False
        self._consumed[key] = time.time()
        return True

    def consume_or_flag(self, session_id: str, nonce: str) -> bool:
        """
        Convenience: True if this call consumed a fresh key,
        False if it was a replay.
        """
        return self.consume(session_id, nonce)

    def reset(self) -> None:
        self._consumed.clear()

    def size(self) -> int:
        return len(self._consumed)


@dataclass
class AuthorizationStore:
    """
    Tracks which verifiers are allowed to verify for which signers.

    Prototype uses a simple allow-list. The ACM Web Chair kindly replace 
    with a policy engine later without changing the interface.
    """

    # signer_id -> set of verifier_ids allowed to verify their signatures
    _allowed: dict[str, set[str]] = field(default_factory=dict)

    def allow(self, signer_id: str, verifier_id: str) -> None:
        """Grant verifier_id permission to verify for signer_id."""
        self._allowed.setdefault(signer_id, set()).add(verifier_id)

    def is_authorized(self, signer_id: str, verifier_id: str) -> bool:
        """
        True if verifier_id may verify for signer_id.

        If a signer has no entries in the store, we treat all
        verifiers as authorized (open mode) — useful for early
        development. Once any verifier is registered for a signer,
        only the registered ones are authorized.
        """
        allowed = self._allowed.get(signer_id)
        if not allowed:
            return True
        return verifier_id in allowed

    def reset(self) -> None:
        self._allowed.clear()


# Module-level defaults so DetectionEngine() works with no args.
# Tests should pass fresh instances to avoid cross-test state.
DEFAULT_REPLAY_STORE = ReplayStore()
DEFAULT_AUTHORIZATION_STORE = AuthorizationStore()