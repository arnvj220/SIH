# System Design Document
## Quantum-Inspired Cyber Threat Detection for Digital Signature Security

**Problem Statement ID:** 26141  
**Problem Statement:** Quantum-Inspired Cyber Threat Detection for Digital Signature Security  
**Category:** Software  
**Theme:** Blockchain & Cybersecurity  
**Design Baseline:** SRS v1.0  
**Document Version:** 1.0  
**Date:** 2026-09-19  

> **Purpose:** This document translates the SRS into an implementable system architecture. It is intended to be the source document for API design, database design, UI/UX design, threat modelling, testing, deployment, and implementation planning.

---

# 1. Design Goals

The system is designed as a **quantum-inspired security analysis platform**, not only as a quantum simulator.

The architecture therefore has to connect four concerns:

```text
Quantum Protocol Simulation
          ↓
Signature Verification
          ↓
Statistical Security Analysis
          ↓
Threat Detection + Evidence + Audit
```

The design has the following goals:

1. Keep quantum/protocol logic independent from cybersecurity detection logic.
2. Make every security decision explainable through measurements, rules, and thresholds.
3. Allow deterministic replay of experiments.
4. Make attack scenarios first-class objects rather than hardcoded demo scripts.
5. Support both interactive demonstrations and batch benchmarking.
6. Allow additional QDS protocol variants and attack detectors to be added later.
7. Keep core detection free from AI/ML, as required by the PS and SRS.
8. Make the complete workflow easy to demonstrate during SIH judging.

---

# 2. Design Principles

## 2.1 Separation of Concerns

Quantum-state operations, signature verification, statistical analysis, attack simulation, storage, and presentation shall be separate modules.

## 2.2 Deterministic Security Decisions

The system may contain stochastic quantum simulation, but the security decision layer must be rule-based and reproducible when the same inputs and random seed are used.

## 2.3 Evidence Before Classification

The system should first produce measurable evidence and then derive the security decision from that evidence.

```text
Raw Measurement
      ↓
Derived Metric
      ↓
Threshold / Protocol Rule
      ↓
Decision
      ↓
Explanation
```

## 2.4 Simulation ≠ Production Quantum Hardware

The prototype is a software simulation framework. Quantum states, channels, measurements, and attacks are represented computationally unless a future quantum backend is added.

## 2.5 Experiment Reproducibility

Every benchmark or attack experiment should be represented by a configuration containing protocol settings, attack parameters, thresholds, measurement count, and random seed where applicable.

---

# 3. High-Level Architecture

```text
                           ┌────────────────────────────┐
                           │        Presentation         │
                           │                            │
                           │ Dashboard │ Attack Lab    │
                           │ Verification │ Reports    │
                           └──────────────┬─────────────┘
                                          │ HTTPS/JSON
                                          ▼
                           ┌────────────────────────────┐
                           │        API Gateway         │
                           │ Auth │ Validation │ RBAC   │
                           └──────────────┬─────────────┘
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 │                        │                        │
                 ▼                        ▼                        ▼
      ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
      │   QDS Orchestrator  │  │  Attack Orchestrator │  │ Experiment Manager  │
      └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
                 │                        │                        │
                 ▼                        ▼                        ▼
      ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
      │ Quantum Simulation  │  │ Attack Simulators    │  │ Batch / Benchmark   │
      │ Bell States         │  │ Forgery             │  │ Runner              │
      │ Teleportation       │  │ Impersonation       │  │                     │
      │ Pauli Operations    │  │ Replay              │  │                     │
      │ Measurements        │  │ Channel Manipulation│  │                     │
      └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘
                 │                        │                        │
                 └────────────────────────┼────────────────────────┘
                                          ▼
                           ┌────────────────────────────┐
                           │      Verification Engine   │
                           │ Protocol Rules             │
                           │ Signature Validation       │
                           │ Identity / Session Checks  │
                           └──────────────┬─────────────┘
                                          ▼
                           ┌────────────────────────────┐
                           │ Statistical Detection      │
                           │ Measurement Statistics     │
                           │ Deviation Analysis         │
                           │ Threshold Engine           │
                           │ Threat Rules               │
                           └──────────────┬─────────────┘
                                          ▼
                           ┌────────────────────────────┐
                           │ Evidence + Incident Engine │
                           │ Decision Explanation       │
                           │ Alert Correlation          │
                           └──────────────┬─────────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     ▼                    ▼                    ▼
              ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
              │ PostgreSQL  │     │ Event Store  │     │ Report /    │
              │ Metadata    │     │ Audit Logs   │     │ Analytics   │
              └─────────────┘     └──────────────┘     └─────────────┘
```

---

# 4. Architectural Layers

## 4.1 Presentation Layer

Responsible for user interaction and visualization.

### Main interfaces

- Security dashboard
- Signature verification screen
- Attack laboratory
- Experiment runner
- Incident detail page
- Benchmarking page
- Report/export page

The UI does not implement security decisions. It consumes structured results from the backend.

---

## 4.2 API / Gateway Layer

Acts as the controlled entry point into the application.

### Responsibilities

- Request validation
- Authentication
- Authorization
- Request routing
- Rate limiting where applicable
- API versioning
- Response normalization
- Request IDs / correlation IDs

The gateway should prevent the frontend from directly accessing internal simulation or database components.

---

## 4.3 QDS Orchestration Layer

Coordinates a complete QDS lifecycle.

### Responsibilities

1. Load protocol configuration.
2. Prepare signer/message context.
3. Generate the required state/entanglement.
4. Perform teleportation simulation.
5. Apply correction operations.
6. Perform measurements.
7. Construct signature/verification evidence.
8. Pass the result to the verification engine.

The orchestrator coordinates the workflow but should not contain low-level quantum mathematics.

---

# 5. Quantum Simulation Subsystem

The PS specifically requires simulation of Bell-state entanglement, quantum teleportation, Pauli correction operations, and projective measurements, together with Pauli eigenstates. The exact protocol equations are intentionally left to the later mathematical specification. fileciteturn1file0L4-L4

## 5.1 State Representation

The simulator should provide an internal representation for quantum states suitable for the selected protocol.

Conceptually:

```text
QuantumState
├── qubit_count
├── amplitudes / state representation
├── basis
└── metadata
```

The exact representation can be state-vector based for the prototype, provided it is sufficient for the selected QDS workflow.

## 5.2 Bell-State Module

Responsibilities:

- Create required Bell states.
- Validate state dimensions.
- Expose the state to teleportation operations.
- Record operation metadata for audit/debugging.

## 5.3 Teleportation Module

Responsibilities:

- Accept input state.
- Apply the required entanglement and measurement sequence.
- Produce classical measurement outcomes.
- Produce the corrected output state.

## 5.4 Pauli Operation Module

Responsibilities:

- X operation
- Y operation
- Z operation
- Conditional correction
- Operation validation

Additional operators should be possible later without changing the surrounding architecture.

## 5.5 Measurement Module

Responsibilities:

- Projective measurement.
- Sampling according to the simulated state.
- Return raw outcomes.
- Store measurement context.
- Support batch measurements.

---

# 6. QDS Signature Subsystem

## 6.1 Signature Lifecycle

```text
Create Message
     ↓
Create Signer Context
     ↓
Prepare Quantum State / Signature Material
     ↓
Teleportation / Correction
     ↓
Measurements
     ↓
Signature Object
     ↓
Persist / Transmit
```

## 6.2 Signature Object

Proposed conceptual structure:

```json
{
  "signature_id": "sig_xxx",
  "signer_id": "usr_xxx",
  "message_id": "msg_xxx",
  "protocol_version": "qds-v1",
  "session_id": "sess_xxx",
  "created_at": "timestamp",
  "quantum_metadata": {},
  "measurement_summary": {},
  "protocol_metadata": {}
}
```

This structure is conceptual. Exact fields will be finalized in the API and database design.

---

# 7. Verification Engine

The verification engine is the boundary between quantum simulation and cybersecurity analysis.

## 7.1 Inputs

- Signature object
- Expected signer context
- Message context
- Session context
- Measurement evidence
- Protocol configuration
- Verification policy

## 7.2 Processing

```text
Validate Structure
      ↓
Validate Signer Context
      ↓
Validate Session
      ↓
Validate Protocol Conditions
      ↓
Evaluate Measurement Evidence
      ↓
Generate Verification Metrics
      ↓
Produce Verification Decision
```

## 7.3 Outputs

```json
{
  "verification_id": "ver_xxx",
  "result": "ACCEPT|REJECT|SUSPICIOUS",
  "metrics": {},
  "rule_results": [],
  "measurement_summary": {},
  "evidence": [],
  "timestamp": "timestamp"
}
```

## 7.4 Decision Boundary

The verification engine should expose structured evidence rather than a single opaque boolean.

Example:

```text
Verification Result: REJECT

Protocol Checks
├── Signer identity       PASS
├── Session validity      PASS
├── Signature structure   PASS
├── Measurement rule      FAIL
└── Statistical threshold FAIL

Primary reason:
Observed measurement deviation exceeded configured threshold.
```

---

# 8. Statistical Detection Engine

This is the main cybersecurity reasoning layer.

## 8.1 Responsibilities

- Build statistics from measurement outcomes.
- Compare observations against expected legitimate behaviour.
- Calculate deviation/error metrics.
- Apply configured thresholds.
- Evaluate threat-specific rules.
- Return evidence for the final decision.

## 8.2 Detection Flow

```text
Raw Outcomes
     ↓
Aggregation
     ↓
Measurement Statistics
     ↓
Expected Baseline
     ↓
Deviation / Error Metric
     ↓
Threshold Evaluation
     ↓
Threat Rules
     ↓
Security Decision
```

## 8.3 Rule Engine

A rule should have a structure similar to:

```text
Rule
├── rule_id
├── threat_type
├── input_metric
├── operator
├── threshold
├── severity
└── explanation_template
```

Example concept:

```text
rule_id: CHANNEL_DEVIATION_01
metric: measurement_deviation
operator: >
threshold: configured_value
result: CHANNEL_MANIPULATION_SUSPECTED
```

Exact statistical tests and mathematical formulas will be specified separately and should not be hardcoded into the UI.

---

# 9. Threat Detection Architecture

## 9.1 Forgery Detector

Inputs:

- Signature information
- Measurement statistics
- Verification metrics
- Message/signature integrity data

Processing:

```text
Signature Alteration
      ↓
Verification
      ↓
Measurement Evidence
      ↓
Statistical Deviation
      ↓
Forgery Rules
```

Output:

```text
FORGERY_DETECTED / NOT_DETECTED
```

## 9.2 Impersonation Detector

Uses signer identity/context and protocol authorization information.

```text
Presented Identity
       ↓
Expected Signer
       ↓
Context Validation
       ↓
Protocol Evidence
       ↓
IMPERSONATION_ALERT
```

## 9.3 Replay Detector

The replay detector is primarily session/event based rather than quantum-state based.

```text
Incoming Session
       ↓
Lookup prior transaction
       ↓
Check uniqueness / replay policy
       ↓
Replay rule
       ↓
REPLAY_ALERT
```

## 9.4 Unauthorized Verification Detector

Checks whether the actor/context is permitted to perform verification.

## 9.5 Channel Manipulation Detector

Uses statistical evidence from the quantum simulation.

```text
Expected Measurement Profile
            │
            │ compare
            ▼
Observed Measurement Profile
            │
            ▼
Deviation Metric
            │
            ▼
Threshold Engine
            │
            ▼
CHANNEL_MANIPULATION_ALERT
```

The PS explicitly calls for quantum-channel manipulation detection using measurement analysis and statistical threshold methods. fileciteturn1file0L4-L4

---

# 10. Attack Simulation Architecture

Attack scenarios are implemented through a common interface so that new attack models can be added later.

## 10.1 Common Interface

```text
AttackScenario
├── initialize()
├── configure(parameters)
├── execute(target)
├── collect_evidence()
└── reset()
```

## 10.2 Attack Types

```text
Attack Engine
├── ForgeryAttack
├── ImpersonationAttack
├── ReplayAttack
├── UnauthorizedVerificationAttack
└── ChannelManipulationAttack
```

## 10.3 Attack Isolation

Attack simulation shall operate against isolated experiment/session data so that malicious modifications cannot corrupt baseline datasets.

---

# 11. Experiment and Benchmark Engine

This subsystem turns the prototype into an evaluatable research tool rather than a collection of manual demos.

## 11.1 Experiment Definition

```json
{
  "experiment_id": "exp_xxx",
  "protocol": "qds-v1",
  "iterations": 10000,
  "random_seed": 12345,
  "thresholds": {},
  "attack": {
    "type": "channel_manipulation",
    "parameters": {}
  }
}
```

## 11.2 Experiment Lifecycle

```text
Create Configuration
       ↓
Validate Configuration
       ↓
Generate Baseline
       ↓
Apply Attack (optional)
       ↓
Run Verification
       ↓
Collect Metrics
       ↓
Aggregate Results
       ↓
Store Experiment
       ↓
Generate Report
```

## 11.3 Benchmark Outputs

- Verification accuracy
- Detection rate
- False-positive rate
- False-negative rate where measurable
- Forgery-related metrics
- Average verification latency
- Percentile latency
- Simulation throughput
- Experiment runtime

The SRS calls for attack simulation and performance evaluation, including verification efficiency and detection metrics. fileciteturn1file0L4-L4

---

# 12. Evidence and Incident Engine

A major design goal is to avoid a security alert that says only `Attack Detected`.

## 12.1 Evidence Object

```text
Evidence
├── evidence_id
├── verification_id
├── measurement_metric
├── observed_value
├── expected_value
├── threshold
├── rule_id
└── explanation
```

## 12.2 Incident Object

An incident groups related alerts.

```text
Incident
├── incident_id
├── attack_type
├── first_seen
├── last_seen
├── affected_sessions
├── alert_count
├── evidence_refs
└── status
```

## 12.3 Explainability Model

Each incident should answer:

```text
WHAT happened?
WHY was it suspicious?
WHICH measurement/rule detected it?
WHAT threshold was crossed?
WHICH session/signature was affected?
```

---

# 13. Data Architecture

## 13.1 Storage Choice

A relational database is suitable for the structured entities defined by the SRS, such as users, signatures, verification events, experiments, alerts, and incidents.

**Proposed database:** PostgreSQL

This is an implementation proposal rather than a requirement from the PS.

## 13.2 Conceptual Entity Model

```text
User / Signer
      │
      ├───────────────┐
      ▼               ▼
   Signature      Authorization
      │
      ▼
Verification Event
      │
      ├───────────────┐
      ▼               ▼
Measurements      Rule Results
      │               │
      └───────┬───────┘
              ▼
           Alert
              │
              ▼
           Incident

Experiment ────────────────┐
     │                     │
     └── Scenario/Attack ──┘
```

## 13.3 Proposed Core Tables

### users

- id
- external_identifier
- role
- authorization_status
- created_at

### signatures

- id
- signer_id
- message_id
- session_id
- protocol_version
- quantum_metadata
- created_at

### verification_events

- id
- signature_id
- verifier_id
- result
- metrics
- evidence_summary
- created_at

### measurements

- id
- verification_id
- measurement_type
- outcome
- batch_index
- metadata

### attack_scenarios

- id
- type
- configuration
- experiment_id

### alerts

- id
- verification_id
- attack_type
- severity
- rule_id
- evidence
- created_at

### incidents

- id
- attack_type
- status
- first_seen
- last_seen

### experiments

- id
- configuration
- random_seed
- status
- metrics
- created_at

The exact schema, indexes, and normalization strategy belong in the database design document.

---

# 14. API Architecture

The API should expose domain-level operations instead of exposing internal classes.

## 14.1 Proposed API Groups

```text
/api/v1/
├── /auth
├── /signatures
├── /verification
├── /attacks
├── /experiments
├── /alerts
├── /incidents
├── /metrics
└── /reports
```

## 14.2 Core Endpoints

### Create Signature

```http
POST /api/v1/signatures
```

### Verify Signature

```http
POST /api/v1/verification
```

### Get Verification Result

```http
GET /api/v1/verification/{verification_id}
```

### Run Attack Simulation

```http
POST /api/v1/attacks/simulate
```

### Create Experiment

```http
POST /api/v1/experiments
```

### Run Experiment

```http
POST /api/v1/experiments/{experiment_id}/run
```

### Get Metrics

```http
GET /api/v1/metrics
```

### Get Incident

```http
GET /api/v1/incidents/{incident_id}
```

Exact request/response schemas should be defined in the API specification derived from the SRS requirement IDs.

---

# 15. End-to-End Data Flow

## 15.1 Legitimate Flow

```text
User selects signer/message
          ↓
POST /signatures
          ↓
QDS Orchestrator
          ↓
Quantum Simulation
          ↓
Measurements
          ↓
Signature stored
          ↓
POST /verification
          ↓
Verification Engine
          ↓
Statistical Engine
          ↓
ACCEPT
          ↓
Audit Event + Metrics
          ↓
Dashboard
```

## 15.2 Forgery Flow

```text
Legitimate Signature
          ↓
Attack Engine modifies target
          ↓
POST /verification
          ↓
Quantum / Protocol Verification
          ↓
Measurement Statistics
          ↓
Threshold Evaluation
          ↓
Forgery Rule
          ↓
REJECT + ALERT
          ↓
Evidence Store
```

## 15.3 Replay Flow

```text
Previously Verified Signature
          ↓
Replay Attack
          ↓
New Verification Request
          ↓
Session / Replay Check
          ↓
REPLAY ALERT
```

---

# 16. State Management

A verification event moves through explicit states.

```text
CREATED
   ↓
RECEIVED
   ↓
VALIDATING
   ↓
SIMULATING
   ↓
MEASURING
   ↓
VERIFYING
   ↓
ANALYZING
   ↓
DECIDED
   ↓
RECORDED
```

Errors should transition into a separate failure state rather than being represented as successful verification.

```text
ANY STATE
   ↓
ERROR
   ↓
FAILED / RETRYABLE
```

---

# 17. Trust Boundaries

The architecture should distinguish between trusted and untrusted inputs.

```text
                 TRUSTED DOMAIN
┌──────────────────────────────────────────────┐
│ Verification Engine                         │
│ Statistical Engine                          │
│ Rule Configuration                          │
│ Audit / Database                            │
└────────────────────┬─────────────────────────┘
                     │
                TRUST BOUNDARY
                     │
┌────────────────────▼─────────────────────────┐
│ Untrusted / Test Inputs                      │
│ Incoming Signatures                          │
│ Attack Parameters                            │
│ Simulated Channel Data                       │
│ External Requests                            │
└──────────────────────────────────────────────┘
```

All incoming data should be validated before entering trusted processing components.

---

# 18. Security Architecture

## 18.1 Authentication

Authentication should be handled at the API layer.

## 18.2 Authorization

Recommended roles:

| Role | Primary Permissions |
|---|---|
| Analyst | View events, run investigations, run simulations |
| Researcher | Configure experiments and inspect quantum evidence |
| Admin | Manage system/configuration |
| Demo User | Restricted demonstration workflows |

## 18.3 Auditability

Security-relevant operations should create audit events, including:

- signature generation,
- verification,
- attack simulation,
- threshold/configuration changes,
- incident creation,
- report generation.

## 18.4 Configuration Protection

Detection thresholds and security rules should not be modifiable by unprivileged users.

---

# 19. Reliability and Failure Handling

## 19.1 Failure Categories

### Input Failure
Malformed signature/session/experiment request.

### Simulation Failure
Quantum simulation cannot complete the requested operation.

### Verification Failure
Verification cannot be completed due to insufficient or inconsistent evidence.

### Storage Failure
Event persistence fails.

### Configuration Failure
Invalid statistical threshold or attack configuration.

## 19.2 Failure Strategy

```text
Validate Early
     ↓
Fail Closed for Security Decisions
     ↓
Record Failure
     ↓
Return Structured Error
     ↓
Preserve Correlation ID
```

A system failure must not silently become an accepted signature.

---

# 20. Performance Architecture

The SRS requires efficient verification and performance evaluation. fileciteturn1file0L4-L4

## 20.1 Interactive Path

The interactive path should minimize work required for a single verification.

```text
Request
 ↓
Validation
 ↓
Verification
 ↓
Statistics
 ↓
Decision
 ↓
Response
```

## 20.2 Batch Path

Large simulations should run through a batch/experiment worker rather than blocking the interactive API.

```text
API
 ↓
Experiment Queue
 ↓
Worker
 ↓
Simulation
 ↓
Aggregation
 ↓
Persistence
 ↓
Result Available
```

For the SIH prototype, this can initially be implemented as an in-process worker before introducing a separate queue if scale requires it.

---

# 21. Deployment Architecture

## 21.1 Prototype Deployment

A containerized architecture is recommended:

```text
                Internet / Judge Browser
                         │
                         ▼
                  ┌──────────────┐
                  │ Frontend     │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Backend API  │
                  └──────┬───────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       Simulator     Detection     Experiment
            │            │            │
            └────────────┼────────────┘
                         ▼
                  ┌──────────────┐
                  │ PostgreSQL   │
                  └──────────────┘
```

## 21.2 Suggested Deployment Units

- Frontend container
- Backend/API container
- PostgreSQL container
- Optional experiment worker

The exact cloud provider and hosting platform are intentionally not fixed in this system design.

---

# 22. Observability

The system should expose three types of observability.

## Application Metrics

- API latency
- error rate
- throughput
- worker status

## Security Metrics

- verification count
- rejection count
- attack detections
- false positives
- incident count

## Experiment Metrics

- iterations
- detection rate
- latency distribution
- attack parameters
- random seed

Each request should carry a correlation ID so that an event can be traced across API, verification, detection, and persistence layers.

---

# 23. Caching Strategy

Caching should remain limited because security decisions must use authoritative, current state.

Safe candidates for caching:

- static protocol metadata,
- read-only dashboard aggregates,
- non-sensitive UI configuration.

Do not cache security decisions or replay-state checks in a way that can produce stale acceptance results.

---

# 24. Concurrency Strategy

## Interactive Verification

Multiple verification requests may execute concurrently as long as their simulation/session state remains isolated.

## Replay Protection

Replay checks must be atomic so that two simultaneous requests cannot both pass a one-time-use rule.

Conceptually:

```text
Request A ─┐
           ├── Atomic session check + consume
Request B ─┘
```

Only one request should be able to consume a one-time verification context.

---

# 25. Extensibility

The system should use interfaces/registries for protocol and detector plug-ins.

## Protocol Plugin

```text
QDSProtocol
├── prepare()
├── sign()
├── transmit()
├── verify()
└── measure()
```

## Detector Plugin

```text
ThreatDetector
├── name()
├── analyze(event)
├── produce_evidence()
└── classify()
```

This allows new protocol variants or attack detectors to be added without redesigning the entire application.

---

# 26. Design Trade-offs

## 26.1 Monolith vs Microservices

**Selected direction:** Modular monolith for the SIH prototype.

### Reason

The project needs fast development, low operational overhead, and a strong demonstration. The modules should have clean boundaries so that they can later be separated if required.

## 26.2 Relational DB vs Document DB

**Selected direction:** PostgreSQL.

### Reason

Core entities have relationships and require reliable transactions, particularly around sessions, verification events, replay prevention, and audit records.

## 26.3 Synchronous vs Asynchronous Experiments

**Selected direction:** Synchronous for small interactive experiments, asynchronous/batch execution for large benchmarks.

## 26.4 AI/ML vs Rules

**Selected direction:** deterministic statistical/rule-based detection.

### Reason

This directly fits the PS requirement for quantum-principle-based statistical detection without AI/ML and provides transparent evidence for security decisions. fileciteturn1file0L4-L4

## 26.5 Real Quantum Hardware vs Simulation

**Selected direction:** software simulation for the SIH prototype.

### Reason

The expected solution is a software framework and requires simulation, mathematical modelling, attack simulation, and performance evaluation. Physical quantum hardware is not required by the supplied PS. fileciteturn1file0L4-L4

---

# 27. Security Decision Contract

Every verification request should ultimately produce a structured decision contract.

```json
{
  "decision": "REJECT",
  "threats": [
    {
      "type": "CHANNEL_MANIPULATION",
      "detected": true,
      "severity": "HIGH",
      "evidence": [
        {
          "metric": "measurement_deviation",
          "observed": "...",
          "expected": "...",
          "threshold": "...",
          "rule_id": "CHANNEL_DEVIATION_01"
        }
      ]
    }
  ],
  "verification": {
    "protocol_checks": {},
    "measurement_summary": {}
  },
  "explanation": "Verification rejected because the observed measurement behaviour exceeded the configured channel-deviation threshold."
}
```

Exact metric names and values are deferred to the mathematical and API specifications.

---

# 28. SIH Demonstration Architecture

The architecture should support a dedicated demo mode with a predictable sequence.

```text
                 DEMO CONTROL PANEL
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
   Legitimate          Forgery            Replay
       │                 │                  │
       └─────────────────┼──────────────────┘
                         ▼
                   Verification
                         ▼
                Measurement Evidence
                         ▼
                 Detection Engine
                         ▼
             ┌────────────────────────┐
             │ Result + Explanation   │
             │ + Evidence + Timeline  │
             └────────────────────────┘
```

A judge should be able to see the difference between a legitimate transaction and an attack without needing to understand the implementation first.

---

# 29. Traceability to SRS

| Design Area | SRS Requirements |
|---|---|
| Quantum Simulation | FR-001 to FR-006 |
| Signature Generation | FR-007 to FR-008 |
| Verification | FR-009 to FR-012 |
| Forgery | FR-013 to FR-015 |
| Impersonation | FR-016 to FR-018 |
| Replay | FR-019 to FR-021 |
| Unauthorized Verification | FR-022 to FR-023 |
| Channel Manipulation | FR-024 to FR-026 |
| Statistical Engine | FR-027 to FR-032 |
| Attack Laboratory | FR-035 to FR-038 |
| Dashboard | FR-039 to FR-043 |
| Audit | FR-044 to FR-048 |
| Performance | PR-001 to PR-004 |
| Security | SR-001 to SR-006 |
| Reliability | RR-001 to RR-003 |
| Usability | UR-001 to UR-004 |
| Quality Goals | NQG-001 to NQG-005 |

---

# 30. Implementation Phases

## Phase 1 — Quantum Core

- State representation
- Bell-state generation
- Teleportation
- Pauli operations
- Measurement simulation

## Phase 2 — QDS Workflow

- Signature object
- Signer/session context
- Verification engine
- Measurement evidence

## Phase 3 — Detection

- Statistical metrics
- Threshold engine
- Forgery detector
- Replay detector
- Impersonation detector
- Channel detector

## Phase 4 — Attack Lab

- Attack scenario framework
- Configurable attack parameters
- Reproducible experiments

## Phase 5 — Security Intelligence

- Alerts
- Incidents
- Timeline
- Evidence explanations

## Phase 6 — Benchmarking + UI

- Dashboard
- Batch runner
- Performance metrics
- Export/reporting

## Phase 7 — Hardening

- Authentication
- Authorization
- Validation
- Audit controls
- Deployment

---

# 31. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Quantum model becomes too complex | High | Freeze a minimum protocol variant for MVP |
| Detection thresholds are poorly calibrated | High | Use controlled baseline and attack experiments |
| Demo becomes a generic quantum simulator | High | Keep threat detection/evidence as the main UI narrative |
| Too many attack types dilute implementation | Medium | Implement P0 attacks first and make the framework extensible |
| Benchmark results are not reproducible | Medium | Store configuration and random seed |
| UI hides technical evidence | Medium | Expose decision → metric → threshold → rule |
| Database state causes replay inconsistencies | High | Use atomic session/replay checks |
| Prototype over-engineering | Medium | Modular monolith before distributed architecture |

---

# 32. Definition of Done for System Design

The system design is considered sufficiently defined when the implementation team can answer:

1. Where is each SRS requirement implemented?
2. What component owns each security decision?
3. What data enters and leaves each component?
4. How is evidence preserved?
5. How is replay prevented?
6. How are attacks isolated from baseline experiments?
7. How are benchmarks reproduced?
8. How can a new detector be added?
9. How can a judge observe the complete workflow?
10. Which technical details are intentionally deferred to mathematical/API/database specifications?

---

# 33. Final Architecture Summary

The final system is designed around the following pipeline:

```text
                       ┌─────────────────┐
                       │    User / API   │
                       └────────┬────────┘
                                ▼
                       ┌─────────────────┐
                       │ QDS Orchestrator│
                       └────────┬────────┘
                                ▼
                       ┌─────────────────┐
                       │ Quantum Engine  │
                       │ Bell / Teleport │
                       │ Pauli / Measure │
                       └────────┬────────┘
                                ▼
                       ┌─────────────────┐
                       │ Verification    │
                       │ Engine          │
                       └────────┬────────┘
                                ▼
                       ┌─────────────────┐
                       │ Statistical     │
                       │ Detection       │
                       └────────┬────────┘
                                ▼
                   ┌─────────────────────────┐
                   │ Threat / Evidence Engine│
                   └────────────┬────────────┘
                                ▼
                   ┌─────────────────────────┐
                   │ Alert + Incident + Audit│
                   └────────────┬────────────┘
                                ▼
                   ┌─────────────────────────┐
                   │ Dashboard + Reports     │
                   └─────────────────────────┘
```

The architectural focus is therefore not simply **simulating quantum operations**, but converting those operations into a **measurable, reproducible, explainable cybersecurity workflow**. This follows the supplied PS's emphasis on teleportation-based QDS, statistical measurement analysis, threshold-based threat identification, attack simulation, and performance/security evaluation. fileciteturn1file0L3-L4

---

# Appendix A — Terms

| Term | Meaning |
|---|---|
| QDS | Quantum Digital Signature |
| Bell State | Entangled two-qubit state used by the simulated protocol |
| Pauli Operation | Quantum operation used in state correction/manipulation |
| Projective Measurement | Measurement model used to obtain outcomes from a quantum state |
| Verification Event | A single signature verification attempt |
| Attack Scenario | Controlled simulation of malicious behaviour |
| Evidence | Measurable information supporting a security decision |
| Incident | Correlated collection of security alerts/events |
| Experiment | Reproducible configured execution of the system |

---

# Appendix B — Deferred Specifications

The following are deliberately delegated to later documents:

- Exact QDS mathematics
- Exact teleportation circuit/state representation
- Exact statistical tests
- Threshold calibration method
- Formal attack algorithms
- Detailed database schema and indexes
- Complete REST/OpenAPI specification
- UI wireframes
- Detailed test cases
- Deployment manifests
- Benchmark target values

This separation keeps the System Design stable while allowing the technical specifications to evolve independently.
