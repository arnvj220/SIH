# Work Division — Quantum-Inspired Cyber Threat Detection

**Problem Statement:** 26141  
**Project:** Quantum-Inspired Cyber Threat Detection for Digital Signature Security  
**Team:** Rishi, Shubh, Arnav, Rachit

> This division is based on the SRS, System Design, and Tech Stack. Each member has a primary ownership area with defined dependencies and shared responsibilities.

---

## 1. Rishi — Quantum/QDS Simulation & Measurement Engine

### Primary Ownership
- Quantum/QDS simulation layer
- Quantum state operations
- Teleportation workflow
- Pauli operations
- Projective measurements
- Protocol-level simulation correctness

### Tasks

#### Quantum Operations
- Bell-state generation and representation
- Quantum teleportation workflow
- Pauli correction operations
- Pauli eigenstate preparation
- Quantum-state handling

#### Measurement Engine
- Projective measurement simulation
- Measurement outcome generation
- Measurement statistics required by verification
- Controlled/randomized simulation parameters
- Reproducible runs using configurable seeds

#### QDS Protocol
- Implement the selected teleportation-based QDS protocol flow
- Signature-generation primitives required by the protocol
- Expose clean interfaces for verification and detection modules

#### Testing & Documentation
- Unit tests for quantum operations
- Document state representation and protocol flow
- Document simulator interfaces and assumptions

### Deliverables
- Quantum Simulation Module
- Teleportation Module
- Pauli Operations Module
- Measurement Module
- QDS Protocol Simulation Layer
- Quantum-module tests and documentation

---

# 2. Shubh — Architecture, Verification & Statistical Detection

### Primary Ownership
- Overall technical architecture
- Verification engine
- Statistical detection engine
- Threshold/decision logic
- Benchmarking and security validation
- Requirement traceability

### Tasks

#### Architecture
- Maintain module boundaries and interfaces
- Define contracts between:
  - quantum engine
  - verification engine
  - attack engine
  - detection engine
  - integration layer
- Resolve architecture-level technical conflicts

#### Verification
- Implement signature verification workflow
- Connect measurement results to verification decisions
- Implement:
  - ACCEPT
  - REJECT
  - SUSPICIOUS
- Define verification evidence requirements

#### Detection Engine
- Statistical analysis of measurement outcomes
- Legitimate-baseline comparison
- Configurable detection thresholds
- Statistical deviation calculations
- Deterministic threat decisions
- Evidence generation for alerts

#### Benchmarking
- Define benchmark scenarios
- Measure:
  - detection rate
  - false-positive rate
  - false-negative rate
  - verification latency
  - simulation throughput
- Validate final security results

#### Project-Level
- Review architecture-sensitive pull requests
- Maintain SRS traceability
- Support final technical/demo validation

### Deliverables
- System Architecture Decisions
- Verification Engine
- Statistical Detection Engine
- Threshold/Decision Engine
- Benchmarking Module
- Requirement Traceability
- Security validation results

---

# 3. Rachit — Integration, API, Database & Application Assembly

### Primary Ownership
- End-to-end integration
- FastAPI backend
- PostgreSQL persistence
- Shared data contracts
- Frontend/backend integration
- Application assembly
- Integration support for verification and detection

### Tasks

#### API Layer
Implement core API areas:

```text
/signatures
/verification
/attacks
/experiments
/alerts
/events
/metrics
```

#### Module Integration
Connect:

```text
Quantum Engine
      ↓
QDS / Verification
      ↓
Detection Engine
      ↓
Attack Engine
      ↓
Audit / Analytics
      ↓
Frontend
```

#### Database
Implement persistence for:

- Signatures
- Verification events
- Measurements / derived metrics where required
- Attack scenarios
- Security alerts
- Experiments
- Audit events

#### Shared Data Contracts
Maintain schemas for:

- Signature
- Verification Event
- Measurement Result
- Attack Scenario
- Detection Result
- Security Alert
- Experiment Result

#### Application Assembly
- Connect all backend modules
- Handle API validation and errors
- Ensure events/results are persisted correctly
- Manage configuration and environment setup
- Integrate frontend with backend APIs

#### Verification/Detection Integration Support
- Connect verification outputs to the detection engine
- Ensure statistical evidence is available through APIs
- Help expose benchmark results and alerts through the application

### Deliverables
- FastAPI Backend
- API Routes
- PostgreSQL Integration
- Shared Data Schemas
- End-to-End Integration
- Frontend/API Integration
- Deployment/Environment Configuration

---

# 4. Arnav — Attack Simulation & Security Scenario Engine

### Primary Ownership
- Attack simulation
- Security scenarios
- Attack-specific test cases
- Attack parameter configuration

### Tasks

#### Forgery
- Signature/data modification scenarios
- Controlled forged inputs
- Configurable attack parameters

#### Replay
- Capture previously valid verification events
- Re-submit them as replay attempts
- Generate replay metadata

#### Impersonation
- Signer identity/context substitution
- Invalid authentication contexts
- Impersonation scenarios for testing

#### Channel Manipulation
- Controlled modifications to transmitted quantum/measurement-relevant data
- Configurable perturbation levels

#### Scenario Framework
Provide a common attack interface:

```text
Attack Scenario
      ↓
Input / Parameters
      ↓
Modified Verification Context
      ↓
System Under Test
      ↓
Expected Attack Class
```

#### Testing
Build attack-specific tests for:
- successful detection
- missed detection
- false positives
- parameter edge cases

### Deliverables
- Attack Simulation Engine
- Forgery Module
- Replay Module
- Impersonation Module
- Channel Manipulation Module
- Attack Scenario Configuration
- Attack Test Suite

---

# 5. Responsibility Matrix

| Module / Deliverable | Rishi | Shubh | Arnav | Rachit |
|---|---:|---:|---:|---:|
| System Architecture | Support | **Lead** |  | Support |
| Quantum Simulation | **Lead** | Support |  | Support |
| Bell States | **Lead** |  |  | Support |
| Teleportation | **Lead** |  |  | Support |
| Pauli Operations | **Lead** |  |  | Support |
| Measurements | **Lead** | Support |  | Support |
| QDS Verification | Support | **Lead** |  | **Integrate** |
| Statistical Detection | Support | **Lead** |  | **Integrate** |
| Threshold Engine | Support | **Lead** |  | **Integrate** |
| Forgery Simulation |  |  | **Lead** | Integrate |
| Replay Simulation |  |  | **Lead** | Integrate |
| Impersonation Simulation |  |  | **Lead** | Integrate |
| Channel Manipulation | Support | Support | **Lead** | Integrate |
| Attack Test Cases |  | Support | **Lead** | Integrate |
| FastAPI | Support | Support |  | **Lead** |
| Database |  | Support |  | **Lead** |
| Shared Schemas | Support | Support | Support | **Lead** |
| Integration | Support | Support | Support | **Lead** |
| Frontend/API Connection | Support | Support |  | **Lead** |
| Benchmarking |  | **Lead** | Support | Integrate |
| End-to-End Testing | Support | **Lead** | Support | **Lead** |
| Final Demo | Support | **Lead** | Support | **Lead** |

---

# 6. Work Distribution

| Member | Approx. Share | Main Focus |
|---|---:|---|
| **Rishi** | **25%** | Quantum/QDS simulation, teleportation, Pauli operations, measurements |
| **Shubh** | **25%** | Architecture, verification, statistical detection, benchmarking |
| **Rachit** | **30%** | Integration, APIs, database, application assembly + integration support |
| **Arnav** | **20%** | Attack simulation and security scenarios |

**Total: 100%**

---

# 7. Dependency Flow

```text
                    ┌──────────────────────┐
                    │ Quantum/QDS Engine   │
                    │       Rishi          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Verification +       │
                    │ Detection Engine     │
                    │       Shubh          │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌──────────────────┐          ┌──────────────────┐
       │ Attack Engine    │          │ Benchmarking     │
       │      Arnav       │          │      Shubh       │
       └────────┬─────────┘          └────────┬─────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Integration / API /  │
                    │ Database / Assembly  │
                    │       Rachit         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Frontend / Demo      │
                    └──────────────────────┘
```

---

# 8. Development Milestones

## Milestone 1 — Foundation

- Repository structure
- Shared schemas
- Initial quantum simulator
- Database skeleton
- Verification/detection interfaces
- Attack-engine interfaces

## Milestone 2 — Core Functionality

- Teleportation + Pauli operations
- Projective measurements
- QDS signature generation
- Signature verification
- Statistical detection
- Initial attack simulations

## Milestone 3 — Integration

- FastAPI routes
- PostgreSQL persistence
- Quantum → Verification → Detection pipeline
- Attack → Detection pipeline
- Frontend/backend integration

## Milestone 4 — Security Validation

- Complete attack suite
- Benchmark experiments
- False-positive/negative analysis
- Threshold calibration
- Audit/event validation

## Milestone 5 — SIH Demo

- Security dashboard
- Attack laboratory
- Incident/evidence view
- Benchmark screen
- Reproducible scenarios
- Full end-to-end testing

---

# 9. Git & Collaboration Rules

### Branching

```text
main
└── develop
     ├── feature/quantum-engine
     ├── feature/detection-engine
     ├── feature/attack-engine
     ├── feature/integration-api
     └── feature/frontend
```

### Rules

- No direct unreviewed changes to `main`.
- Keep feature branches focused.
- Document public interfaces.
- Communicate breaking schema/API changes before merging.
- Every module should include appropriate tests.
- Integration should be performed against stable interfaces rather than relying on direct access to another member's internal implementation.

---

# 10. Definition of Done

A module is complete when:

- Core functionality is implemented.
- Important paths have tests.
- Inputs and outputs are documented.
- Public interfaces are stable.
- Errors are handled.
- The module can be integrated without manual source changes.
- A reproducible test/demo case exists.

The complete system is considered ready when both flows work end-to-end:

```text
LEGITIMATE FLOW

Signature
   ↓
Quantum/QDS Simulation
   ↓
Verification
   ↓
Statistical Analysis
   ↓
ACCEPT / REJECT
   ↓
Audit Event
```

```text
ATTACK FLOW

Attack Scenario
   ↓
Modified Transaction
   ↓
Verification
   ↓
Statistical Analysis
   ↓
Detection
   ↓
Evidence
   ↓
Security Alert
```

---

# 11. Final Ownership Summary

| Member | Core Ownership |
|---|---|
| **Rishi** | Quantum/QDS simulation, teleportation, Pauli operations, measurements |
| **Shubh** | Architecture, verification, statistical detection, benchmarking |
| **Rachit** | Integration, APIs, database, application assembly, verification/detection integration |
| **Arnav** | Attack simulation and security scenarios |
