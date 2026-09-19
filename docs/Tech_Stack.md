# Tech Stack — Quantum-Inspired Cyber Threat Detection

## Backend
- **Python 3.11+** — core application and simulation logic
- **FastAPI** — REST API layer
- **Pydantic** — request/response validation
- **NumPy** — numerical and statistical computation
- **SciPy** — statistical analysis and hypothesis/testing utilities
- **Qiskit** — quantum circuit/state simulation
- **SQLAlchemy** — database ORM

## Database
- **PostgreSQL** — signatures, verification events, experiments, alerts, audit logs

## Frontend
- **React + TypeScript** — web dashboard
- **Vite** — frontend tooling
- **Tailwind CSS** — UI styling
- **Recharts** — security/measurement visualizations

## Security & Detection
- Deterministic rule/threshold engine
- Statistical anomaly analysis
- Attack simulation modules
- No AI/ML in the core detection pipeline

## DevOps
- **Docker** — containerization
- **Docker Compose** — local multi-service deployment
- **Git + GitHub** — version control and collaboration

## Architecture

```text
React + TypeScript
        ↓
     FastAPI
        ↓
┌───────────────────────┐
│ QDS / Quantum Engine  │
│ Detection Engine      │
│ Attack Simulator      │
│ Audit / Analytics     │
└───────────┬───────────┘
            ↓
       PostgreSQL
```

> This stack is the proposed implementation baseline derived from the SRS/System Design; exact libraries can be changed during implementation if benchmarking or compatibility requires it.
