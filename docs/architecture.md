# Detection Architecture

## Scope

This document describes the detection pipeline for the quantum-inspired
QDS security platform. It is a companion to the SRS and System Design
documents and is accurate as of the SIH prototype.

## Layers
VerificationContext (from attacks.contracts)
↓
DetectionEngine.verify() (app/detection/engine.py)
↓
┌─────────┬──────────┬─────────┬───────────┬────────┐
│structural│ rules │ replay │ authorization│ ...
│checks │ engine │ store │ store │
└─────────┴──────────┴─────────┴───────────┴────────┘
↓
DetectionOutcome (decision + threats + evidence)


## The five attack detections

| Attack | Mechanism | File |
|---|---|---|
| Forgery | Structural: `message_digest != signed_digest`; statistical: `error_rate > 0.15` | `engine.py`, `rules.py` |
| Impersonation | Structural: `signer_id != expected_signer_id` | `engine.py` |
| Replay | Stateful: `(session_id, nonce)` was previously consumed | `engine.py`, `stores.py` |
| Unauthorized verification | Stateful: `verifier_id` not authorized for `signer_id` | `engine.py`, `stores.py` |
| Channel manipulation | Statistical: per-basis error skew > 0.30 | `engine.py`, `rules.py` |

## Rule engine

Rules are data, defined in `detection/rules.py`:

```python
Rule(
    rule_id="CHANNEL_DIST_SHIFT_01",
    threat_type=ThreatType.CHANNEL_MANIPULATION,
    metric="distribution_shift",
    operator=RuleOperator.GT,
    threshold=0.30,
    severity=Severity.HIGH,
    explanation_template="Per-basis error skew {observed:.3f} exceeded {threshold:.3f}",
)