# Qureka

Qureka is a **Quantum Digital Signature Threat Analysis Framework** for simulating, verifying, and analyzing security threats in teleportation-based Quantum Digital Signature (QDS) systems.

**Problem Statement:** 26141 · **SIH 2026** · **Theme:** Blockchain & Cybersecurity  
**Team:** Rishi · Shubh · Arnav · Rachit

## Current Capabilities

The project currently supports:

- Simulating the Quantum Digital Signature protocol.
- Generating and verifying quantum digital signatures.
- Simulating five required attack classes.
- Detecting forgery through digest mismatch and verification error analysis.
- Detecting signer impersonation through identity validation.
- Detecting replay attacks using session and nonce tracking.
- Detecting unauthorized verification through authorization checks.
- Detecting quantum channel manipulation through measurement statistics.
- Producing deterministic, rule-based security decisions.
- Generating explainable alerts with rule IDs, observed values, thresholds, and explanations.
- Persisting signatures, events, alerts, and experiment results in MongoDB.
- Providing a web-based security dashboard for interacting with the system.

The implementation is a deterministic prototype. It does not use AI/ML as the core detection mechanism, and the same input and seed produce reproducible decisions.

## Live Demo

| Component | URL |
| --- | --- |
| Frontend | [Qureka Frontend](https://qureka-smoky.vercel.app/) |
| Backend API | [Qureka Backend](https://sih-grh0.onrender.com/) |
| API Documentation | [Swagger / OpenAPI Docs](https://sih-grh0.onrender.com/docs) |

## Architecture

The system follows this flow:

```text
React + TypeScript Frontend
            |
            | REST /api/*
            v
        FastAPI Backend
            |
    +-------+-------+----------------+
    |               |                |
    v               v                v
Quantum Engine  Detection Engine  Attack Engine
    |               |                |
    |               |                |
    +---------------+----------------+
                    |
                    v
                 MongoDB
```

The main components are separated by responsibility:

- **Quantum Engine** — Bell states, teleportation, Pauli correction, and measurements.
- **QDS Layer** — Signature generation and verification.
- **Detection Engine** — Structural checks, statistical rules, replay/authentication state, and evidence generation.
- **Attack Engine** — Simulation of the five attack classes against the verification pipeline.
- **FastAPI Backend** — REST API and application services.
- **MongoDB** — Persistence for signatures, alerts, events, and runs.
- **React Frontend** — Workbench, alerts, events, and signature views.

## Repository Layout

```text
backend/
├── app/
│   ├── quantum/        Quantum states, teleportation, Pauli, measurements
│   ├── qds/            QDS protocol, signer, signature objects
│   ├── attacks/        Attack modules, registry, runner, adapter
│   ├── detection/      Detection engine, rules, stores, statistics
│   ├── services/       Application services
│   ├── api/            FastAPI routers
│   └── core/           Configuration and settings
├── tests/              Backend test suite
└── scripts/            Database, audit, and diagnostic utilities

frontend/
├── src/
│   ├── pages/          Workbench, Alerts, Events, Signatures
│   ├── components/     UI components and workbench panels
│   ├── lib/            API client, types, cache, formatters
│   └── theme/          Theme system
└── package.json

docs/
├── architecture.md     Detection subsystem design
├── traceability.md     SRS requirement-to-code mapping
├── benchmark_v1.md     Benchmark results
└── SRS.md              Software Requirements Specification
```

## Attack Coverage

Qureka distinguishes five attack classes required by the problem statement.

### Forgery

Forgery is detected when the presented message digest does not match the digest associated with the signature, or when the verification error rate crosses the configured threshold.

Example rule:

```text
FORGERY_DIGEST_MISMATCH_01
```

### Impersonation

Impersonation is detected when the signer identity in the verification request does not match the expected signer identity.

```text
signer_id != expected_signer_id
```

### Replay

Replay attacks are detected when an already-consumed `(session_id, nonce)` combination is submitted again.

### Unauthorized Verification

Verification requests are checked against the authorization state of the signer and verifier.

```text
verifier_id not authorized for signer_id
```

### Channel Manipulation

Channel manipulation is detected using measurement-distribution statistics. A sufficiently large per-basis error skew triggers the corresponding detection rule.

## Detection Model

Each attack is associated with a distinct measurable signal.

| Attack | Signal | Detection mechanism |
| --- | --- | --- |
| **Forgery** | `message_digest != signed_digest` or elevated error rate | Digest / error-rate rules |
| **Impersonation** | `signer_id != expected_signer_id` | Structural identity check |
| **Replay** | `(session_id, nonce)` already consumed | Replay store |
| **Unauthorized** | Verifier is not authorized for signer | Authorization store |
| **Channel manipulation** | Per-basis error skew exceeds threshold | Statistical rule |

The system therefore identifies the type of security violation rather than returning only a generic anomaly score.

## Explainable Alerts

Every detection is designed to provide evidence for the decision.

An alert can contain:

- **Decision**
- **Threat type**
- **Rule ID**
- **Observed value**
- **Expected value / threshold**
- **Plain-English explanation**

Example:

```text
Decision: REJECT
Threat: FORGERY
Rule: FORGERY_DIGEST_MISMATCH_01

Explanation:
Presented message digest does not match signed digest.
```

This makes the detection result directly inspectable from the dashboard and API.

## Requirements Coverage

The implementation maps the major functional requirements to separate modules.

| Requirement | Implementation |
| --- | --- |
| Quantum simulation | `backend/app/quantum/` |
| Signature generation & verification | `backend/app/qds/` and verification APIs |
| Forgery simulation & detection | `backend/app/attacks/forgery.py` and detection rules |
| Impersonation detection | `backend/app/attacks/impersonation.py` |
| Replay detection | `backend/app/attacks/replay.py` and replay stores |
| Unauthorized verification | `backend/app/attacks/unauthorized.py` |
| Channel manipulation | `backend/app/attacks/channel_manipulation.py` |
| Statistical detection | `backend/app/detection/` |
| Attack laboratory | `backend/app/experiments/` and frontend Workbench |
| Security dashboard | `frontend/src/pages/` |
| Audit logging | `backend/app/services/audit_service.py` |

For the complete mapping, see the [Traceability Matrix](docs/traceability.md).

## Benchmarks

The project includes both synthetic and real-pipeline benchmarks.

| Metric | Synthetic | Real pipeline |
| --- | ---: | ---: |
| Detection rate | 100% | 100% |
| False positive rate | 0% | 0% |
| False negative rate | 0% | 0% |
| Mean latency | 0.05 ms | 5.7 ms |
| P95 latency | 0.10 ms | 15.4 ms |

The benchmark results are generated from the project's own test suite and are not an independent external evaluation.

Run the benchmark with:

```bash
cd backend
python -m app.experiments.runner --mode both
```

See the detailed benchmark documentation in [Benchmark v1](docs/benchmark_v1.md).

## Engineering Fix

During development, the real verification pipeline initially produced false positives for legitimate channel measurements.

The issue was traced to independently sampling two outcomes and comparing them position-by-position. Independent samples from the same distribution can naturally differ, which inflated the observed skew.

The measurement generation was changed to use a shared per-shot uniform through inverse-CDF sampling. After the fix, the diagnostic no longer crossed the configured skew threshold for the tested legitimate seeds, and the real-pipeline benchmark returned a 0% false-positive rate.

## Key Design Decisions

### Deterministic Detection

The detection path does not depend on AI/ML. Decisions are produced through deterministic rules and configured thresholds over measured evidence.

### Explainability by Construction

Detection results carry structured evidence:

```text
rule_id
observed value
expected value / threshold
explanation
```

### Attack Isolation

Attack simulations operate on cloned verification contexts so that an attack does not unintentionally mutate the original context.

### Real Detector Integration

The attack runner is connected to the actual verification and detection implementation. Attack simulations therefore exercise the real detector rather than a separate mock implementation.

### Replay Protection

Replay protection uses `(session_id, nonce)` state so that a malformed request does not incorrectly consume a legitimate replay-protection entry.

## Requirements

- Python 3.11+
- Node.js 18+
- MongoDB / MongoDB Atlas
- Dependencies listed in `backend/requirements.txt` and `frontend/package.json`

## Setup

### Backend

```powershell
cd backend

python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Configure the MongoDB connection in .env
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend development server runs on:

```text
http://localhost:5173
```

### Backend API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The local API is then available at:

```text
http://localhost:8000
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

## API Documentation

The deployed API documentation is available here:

**[Open Qureka API Documentation](https://sih-grh0.onrender.com/docs)**

The Swagger interface provides the available REST endpoints and allows API requests to be tested directly against the deployed backend.

## Tests

Run the backend test suite with:

```bash
cd backend
pytest -v
```

The project includes tests covering the quantum/QDS pipeline, attack modules, detection rules, API behavior, and supporting services.

## Limitations

- The framework uses quantum simulation rather than real quantum hardware.
- Detection thresholds are based on the simulated pipeline and configured statistical rules.
- Channel-manipulation attacks below the configured detection threshold may not trigger an alert.
- Benchmark results are from the project's own test suite and have not been independently evaluated.
- The prototype does not provide production-grade key management.
- The prototype does not implement a complete production IAM system.
- The current deployment is intended as an SIH prototype rather than a distributed production system.

## Related Documentation

- [System Architecture](docs/architecture.md)
- [Requirements Traceability](docs/traceability.md)
- [Benchmark Results](docs/benchmark_v1.md)
- [Software Requirements Specification](docs/SRS.md)
- [Backend API Documentation](https://sih-grh0.onrender.com/docs)

## Team & Contributions

| Member | Contribution |
| --- | --- |
| **Rishi** | Quantum engine, QDS protocol, measurement simulation |
| **Shubh** | Detection engine, statistical rules, benchmarking, architecture |
| **Arnav** | Attack engine, integration, verifier adapter, frontend, deployment |
| **Rachit** | API layer, database models |

## Submission

Built for **Smart India Hackathon 2026**, Problem Statement **26141**.

The project focuses on an explainable and deterministic security analysis framework for Quantum Digital Signature systems, with an integrated attack simulation environment, detection engine, REST API, and web dashboard.
