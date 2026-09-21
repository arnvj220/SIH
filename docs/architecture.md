# Detection Architecture

**Companion documents:** Software Requirements Specification (SRS) v1.0,
System Design Document (SDD) v1.0.
**Scope:** Detection pipeline for the quantum-inspired QDS security platform.
**Status:** Accurate as of the SIH prototype.

---

## 1. Purpose

This document describes the architecture of the detection subsystem —
the component that turns a verification attempt into a structured,
evidence-backed security decision. It is the reference for anyone
extending the detection engine or evaluating its correctness.

---

## 2. Position in the system

The detection subsystem is one layer in a larger pipeline:

Quantum simulation
↓
QDS signature workflow
↓
VerificationService builds VerificationContext
↓
DetectionEngine.verify() ← this document
↓
DetectionOutcome { decision, threats, evidence }
↓
API / Audit / Dashboard


The engine consumes a `VerificationContext` (defined in
`app/attacks/contracts.py`) and returns a `DetectionOutcome`. It has no
knowledge of the API layer, the database, or the quantum simulation
internals. This boundary is deliberate: detection can be tested,
replayed, and reasoned about independently.

---

## 3. Internal structure

DetectionEngine.verify(context)
│
├── 1. Structural checks (no state)
│ • Impersonation: signer_id != expected_signer_id
│ • Forgery: message_digest != signed_digest
│ • Unauthorized: verifier_id not authorized for signer_id
│
├── 2. Statistical rules (no state)
│ • Forgery: error_rate > threshold
│ • Channel: per-basis error skew > threshold
│ (driven by app/detection/rules.py)
│
└── 3. Stateful checks (only if no other threat present)
• Replay: (session_id, nonce) previously consumed


Each check appends to a `threats` list and an `evidence` list. The final
`DetectionOutcome` carries both. The decision is `REJECT` if any threat
was raised, `ACCEPT` otherwise.

### Why this ordering matters

- **Structural checks first** — cheap and deterministic. If the
  request is malformed or clearly impersonating, no need to run
  statistics.
- **Statistical checks second** — they consume metrics derived from
  the measurement rounds; only relevant if the structure is intact.
- **Replay check last** — deliberately. Replay consumes the
  `(session_id, nonce)` key on success. If it ran first, an attacker
  who submits an impersonating request with a legitimate-looking
  session would "burn" the session and lock out the real user. By
  running it last, we only consume the key when the request passes
  every other check — a partial-availability protection.

This ordering is a correctness requirement, not an optimization.

---

## 4. The five attack detections

| Attack | Mechanism | Location |
|---|---|---|
| **Forgery** | Structural: `message_digest != signed_digest`. Statistical: `error_rate > 0.15`. | `engine.py`, `rules.py::FORGERY_ERROR_RATE_01` |
| **Impersonation** | Structural: `signer_id != expected_signer_id`. | `engine.py` |
| **Replay** | Stateful: `(session_id, nonce)` already consumed. | `engine.py`, `stores.py::ReplayStore` |
| **Unauthorized verification** | Stateful: `verifier_id` not authorized for `signer_id`. | `engine.py`, `stores.py::AuthorizationStore` |
| **Channel manipulation** | Statistical: per-basis error skew > 0.30. | `engine.py`, `rules.py::CHANNEL_DIST_SHIFT_01` |

Each attack maps to a **distinct detection signal**. This is what
distinguishes the platform from a generic anomaly detector — the
threat types are not just labels on the same score, they are
mechanically different evaluations.

---

## 5. Rule engine

Rules are data, not code. They live in `app/detection/rules.py`:

```python
Rule(
    rule_id="CHANNEL_DIST_SHIFT_01",
    threat_type=ThreatType.CHANNEL_MANIPULATION,
    metric="distribution_shift",
    operator=RuleOperator.GT,
    threshold=0.30,
    severity=Severity.HIGH,
    explanation_template=(
        "Per-basis error skew {observed:.3f} exceeded "
        "channel threshold {threshold:.3f}"
    ),
)