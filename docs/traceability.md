
---

## `docs/traceability.md`

```markdown
# Requirements Traceability

**Purpose:** map each SRS requirement to the code that implements it,
so that a reviewer can verify coverage by inspection.
**Source of truth:** Software Requirements Specification (SRS) v1.0.
**Status:** Accurate as of the SIH prototype.

---

## Functional Requirements

| SRS ID | Requirement | Implementation | Verification |
|---|---|---|---|
| FR-001 | Bell-state generation | `app/quantum/states/bell.py` | `tests/quantum/test_bell.py` |
| FR-002 | Quantum teleportation | `app/quantum/teleportation/protocol.py::teleport` | `tests/quantum/test_teleportation_protocol*.py` |
| FR-003 | Pauli correction | `app/quantum/teleportation/corrections.py::get_correction` | `tests/quantum/test_corrections.py` |
| FR-004 | Pauli eigenstates | `app/quantum/states/pauli_states.py` | `tests/quantum/test_pauli_states.py` |
| FR-005 | Projective measurement | `app/quantum/measurements/projective.py::measurement_probabilities` | `tests/quantum/test_projective.py` |
| FR-006 | Reproducible simulation | seeds threaded through `teleport(seed=…)`, `sample_measurements(seed=…)` | `tests/quantum/test_outcomes.py` |
| FR-007 | Signature creation | `app/qds/protocol.py::execute_protocol`, `app/qds/signature.py::QDSSignature` | `tests/qds/*` |
| FR-008 | Signature metadata | `QDSSignature` dataclass fields | `tests/domain/test_domain_signature.py` |
| FR-009 | Signature verification | `app/services/verification_service.py`, `app/detection/engine.py::DetectionEngine.verify` | `tests/detection/test_engine.py` |
| FR-010 | Measurement evidence | `app/quantum/measurements/evidence.py::QuantumEvidence`, `app/detection/evidence.py::make_evidence` | `tests/detection/test_evidence.py` |
| FR-011 | Verification decision | `DetectionOutcome.decision` in `app/attacks/contracts.py` | `tests/detection/test_engine.py::TestCleanContext` |
| FR-012 | Verification explanation | Evidence dicts with `rule_id` and `explanation` | `tests/detection/test_engine.py::TestCombinedAttacks::test_evidence_always_has_rule_id_on_reject` |
| FR-013 | Forgery simulation | `app/experiments/scenarios.py::forgery_scenario` | `tests/experiments/test_benchmark.py::TestScenarios` |
| FR-014 | Forgery probability | `FORGERY_ERROR_RATE_01` rule threshold | `docs/benchmark_v1.md` |
| FR-015 | Forgery decision rule | `app/detection/rules.py::DEFAULT_RULES`, `app/detection/thresholds.py::crosses` | `tests/detection/test_rules.py`, `tests/detection/test_thresholds.py` |
| FR-016 | Identity binding | `VerificationContext.signer_id` / `.expected_signer_id` | `app/attacks/contracts.py` |
| FR-017 | Impersonation simulation | `app/experiments/scenarios.py::impersonation_scenario` | `tests/experiments/test_benchmark.py` |
| FR-018 | Impersonation detection | `DetectionEngine.verify` structural check | `tests/detection/test_engine.py::TestImpersonation` |
| FR-019 | Session tracking | `ReplayStore` in `app/detection/stores.py` | `tests/detection/test_stores.py::TestReplayStore` |
| FR-020 | Replay simulation | `benchmark.py` paired submissions | `tests/detection/test_engine.py::TestReplay` |
| FR-021 | Replay detection | `DetectionEngine.verify` stateful check | `tests/detection/test_engine.py::TestReplay` |
| FR-022 | Verification authorization | `AuthorizationStore` in `app/detection/stores.py` | `tests/detection/test_stores.py::TestAuthorizationStore` |
| FR-023 | Unauthorized attempt logging | `DetectionEngine.verify` → `ThreatType.UNAUTHORIZED_VERIFICATION` | `tests/detection/test_engine.py::TestUnauthorized` |
| FR-024 | Channel attack simulation | `app/experiments/scenarios.py::channel_manipulation_scenario` | `tests/experiments/test_benchmark.py` |
| FR-025 | Channel integrity analysis | `_extract_metrics` per-basis skew | `tests/detection/test_engine.py::TestChannelManipulation` |
| FR-026 | Attack evidence | `make_evidence` returns `rule_id` + `explanation` per trigger | `tests/detection/test_evidence.py` |
| FR-027 | Statistical analysis | `app/detection/statistics.py` | `tests/detection/test_statistics.py` |
| FR-028 | Configurable thresholds | `Rule.threshold` in `app/detection/rules.py` | `tests/detection/test_rules.py` |
| FR-029 | Legitimate baseline | `app/detection/baseline.py::BaselineProfile` | `tests/detection/test_baseline.py` |
| FR-030 | Deviation calculation | `app/detection/statistics.py::measurement_deviation` | `tests/detection/test_statistics.py` |
| FR-031 | Threat decision | `app/detection/engine.py::DetectionEngine.verify` | `tests/detection/test_engine.py` |
| FR-032 | Evidence trace | `Evidence` objects attached to every threat | `tests/detection/test_evidence.py` |
| FR-033 | Threat severity | `Rule.severity` in `app/detection/rules.py` | `tests/detection/test_rules.py` |
| FR-034 | Attack correlation | Not implemented in prototype — planned for `services/detection_service.py` | — |
| FR-035 | Scenario selection | `app/experiments/scenarios.py` | `tests/experiments/test_benchmark.py` |
| FR-036 | Attack parameters | `ExperimentConfig.parameters` in `app/experiments/config.py` | `tests/experiments/test_benchmark.py::TestRunner::test_run_from_config` |
| FR-037 | Side-by-side comparison | `benchmark.py` runs both legit and attack scenarios with identical seeds | `tests/experiments/test_benchmark.py::TestBenchmarkMetrics::test_deterministic_metrics_with_same_seed` |
| FR-038 | Attack outcome | `DetectionOutcome.threats` per scenario | `docs/benchmark_v1.md` per-attack breakdown |
| FR-039 | Verification overview | Dashboard — pending frontend integration | — |
| FR-040 | Attack distribution | `BenchmarkMetrics.per_attack` | `docs/benchmark_v1.md` per-attack breakdown |
| FR-041 | Statistical visualization | Frontend — pending | — |
| FR-042 | Timeline | Frontend — pending | — |
| FR-043 | Incident drill-down | Frontend — pending | — |
| FR-044 | Security event logging | `app/services/audit_service.py` (Rachit) | `tests/services/test_audit_service.py` |
| FR-045 | Immutable event ID | Event schema in `app/models/domain/alert.py` | `tests/domain/*` |
| FR-046 | Event timestamp | `VerificationContext.issued_at` / `.received_at` | `app/attacks/contracts.py` |
| FR-047 | Event context | `VerificationContext` carries full evidence chain | `tests/domain/test_domain_verification.py` |
| FR-048 | Export | Report formatter `app/experiments/report.py::to_json` | `tests/experiments/test_benchmark.py::TestReport::test_json_is_valid` |

---

## Performance Requirements

| SRS ID | Requirement | Implementation | Measurement |
|---|---|---|---|
| PR-001 | Verification efficiency | `DetectionEngine.verify` (no I/O) | Mean 0.008 ms, P95 0.012 ms on 600 samples |
| PR-002 | Batch simulation | `app/experiments/benchmark.py::run_benchmark` | 600 samples in <10 ms |
| PR-003 | Scalability | Modular separation: quantum / detection / experiments | Directory structure |
| PR-004 | Benchmarking | `app/experiments/runner.py` CLI | `docs/benchmark_v1.md` |

---

## Security Requirements

| SRS ID | Requirement | Implementation |
|---|---|---|
| SR-001 | No AI/ML | `app/detection/rules.py` — deterministic thresholds only |
| SR-002 | Deterministic decisions | Seeded scenarios (`scenarios.py`), reproducible benchmark |
| SR-003 | Explainable decisions | Every rule emits `Evidence{metric, observed, expected, threshold, rule_id, explanation}` |
| SR-004 | Input validation | Dataclass `__post_init__` in `MeasurementRound`; Pydantic API schemas |
| SR-005 | Attack isolation | `VerificationContext.clone`; fresh stores per benchmark run |
| SR-006 | Auditability | `app/services/audit_service.py` (Rachit) |

---

## Reliability Requirements

| SRS ID | Requirement | Implementation |
|---|---|---|
| RR-001 | Error handling | `DetectionEngine.verify` returns `DetectionOutcome` for all valid inputs |
| RR-002 | Reproducibility | `ExperimentConfig.seed` threaded through all scenarios |
| RR-003 | Result integrity | `DetectionOutcome` carries decision, threats, evidence distinctly |

---

## Usability Requirements

| SRS ID | Requirement | Implementation |
|---|---|---|
| UR-001 | Guided workflow | Demo flow documented in SRS §24 |
| UR-002 | Explainability first | Every threat carries a human-readable `explanation` |
| UR-003 | Visual quantum flow | Rishi's quantum engine exposes state, measurement, correction |
| UR-004 | Security-first view | `DetectionOutcome` emphasizes decision + threats + evidence |

---

## Acceptance Criteria

| AC ID | Criterion | Verification |
|---|---|---|
| AC-001 | Legit signature verifies | `tests/detection/test_engine.py::TestCleanContext` |
| AC-002 | Forgery detected | `tests/detection/test_engine.py::TestForgery` |
| AC-003 | Replay detected | `tests/detection/test_engine.py::TestReplay` |
| AC-004 | Impersonation detected | `tests/detection/test_engine.py::TestImpersonation` |
| AC-005 | Channel manipulation detected | `tests/detection/test_engine.py::TestChannelManipulation` |
| AC-006 | Evidence displayed on detection | `tests/detection/test_engine.py::TestCombinedAttacks::test_evidence_always_has_rule_id_on_reject` |
| AC-007 | No AI/ML | See SR-001 |
| AC-008 | Batch experiment | `docs/benchmark_v1.md` — 600 samples |
| AC-009 | Auditable record | `app/services/audit_service.py` (Rachit) |
| AC-010 | Full workflow demonstrable | Demo scenarios in SRS §24; benchmark report |

---

## Coverage summary

| Area | Covered | Partial | Deferred |
|---|---:|---:|---:|
| Detection (FR-009 to FR-032) | 24 | 0 | 0 |
| Attack simulation (FR-013, FR-017, FR-020, FR-024) | 4 | 0 | 0 |
| Dashboard (FR-039 to FR-043) | 0 | 0 | 5 (frontend pending) |
| Audit (FR-044 to FR-048) | 4 | 1 | 0 |
| Performance (PR-001 to PR-004) | 4 | 0 | 0 |
| Security (SR-001 to SR-006) | 6 | 0 | 0 |
| Reliability (RR-001 to RR-003) | 3 | 0 | 0 |
| Usability (UR-001 to UR-004) | 4 | 0 | 0 |
| Acceptance Criteria (AC-001 to AC-010) | 10 | 0 | 0 |

**Detection subsystem coverage: 100% of in-scope SRS requirements.**

Items deferred to other subsystems (dashboard, audit persistence) are
owned by other team members and traced in their respective documents.