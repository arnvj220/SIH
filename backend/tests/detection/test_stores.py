"""Tests for detection state stores."""

import pytest

from app.detection.stores import AuthorizationStore, ReplayStore


class TestReplayStore:
    def test_first_consume_returns_true(self):
        store = ReplayStore()
        assert store.consume_or_flag("s1", "n1") is True

    def test_second_consume_returns_false(self):
        store = ReplayStore()
        store.consume_or_flag("s1", "n1")
        assert store.consume_or_flag("s1", "n1") is False

    def test_different_nonce_is_new(self):
        store = ReplayStore()
        store.consume_or_flag("s1", "n1")
        assert store.consume_or_flag("s1", "n2") is True

    def test_different_session_is_new(self):
        store = ReplayStore()
        store.consume_or_flag("s1", "n1")
        assert store.consume_or_flag("s2", "n1") is True

    def test_is_consumed_reflects_state(self):
        store = ReplayStore()
        assert store.is_consumed("s1", "n1") is False
        store.consume_or_flag("s1", "n1")
        assert store.is_consumed("s1", "n1") is True

    def test_reset_clears(self):
        store = ReplayStore()
        store.consume_or_flag("s1", "n1")
        store.reset()
        assert store.is_consumed("s1", "n1") is False


class TestAuthorizationStore:
    def test_open_mode_when_no_entries(self):
        store = AuthorizationStore()
        assert store.is_authorized("alice", "bob") is True

    def test_registered_verifier_authorized(self):
        store = AuthorizationStore()
        store.allow("alice", "bob")
        assert store.is_authorized("alice", "bob") is True

    def test_unregistered_verifier_denied_once_any_registered(self):
        store = AuthorizationStore()
        store.allow("alice", "bob")
        assert store.is_authorized("alice", "mallory") is False

    def test_different_signer_open(self):
        store = AuthorizationStore()
        store.allow("alice", "bob")
        # No entries for carol -> open mode
        assert store.is_authorized("carol", "mallory") is True

    def test_reset_clears(self):
        store = AuthorizationStore()
        store.allow("alice", "bob")
        store.reset()
        assert store.is_authorized("alice", "mallory") is True