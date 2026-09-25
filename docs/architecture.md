# Enterprise AI Reliability Platform — System Architecture

## High-Level Architecture

```mermaid
flowchart TD

    A[Reference Dataset] --> D[Reliability Engine]
    B[Production Dataset] --> D
    C[Active Champion Model] --> D

    D --> E[Data Quality Monitor]
    D --> F[Data Drift Monitor]
    D --> G[Model Performance Monitor]
    D --> H[Anomaly Detection]
    D --> I[Root Cause Analysis]

    E --> J[Reliability Status]
    F --> J
    G --> J
    H --> J
    I --> J

    J --> K{Critical Model Degradation?}

    K -- No --> L[Continue Monitoring]

    K -- Yes --> M[Self-Healing Trigger]

    M --> N[Split Recent Production Data]

    N --> O[70% Recent Training Data]
    N --> P[30% Untouched Validation Data]

    Q[Historical Training Data] --> R[Challenger Training]
    O --> R

    R --> S[V3 Challenger Model]

    C --> T[Champion Evaluation]
    S --> U[Challenger Evaluation]
    P --> T
    P --> U

    T --> V[Promotion Quality Gate]
    U --> V

    V --> W{Quality Gate Passed?}

    W -- No --> X[Keep Existing Champion]

    W -- Yes --> Y[MLflow Model Registry]

    Y --> Z[Register Challenger]

    Z --> AA[Promote Challenger to Champion]

    AA --> AB[Archive Previous Champion]

    AB --> AC[Deployment Verification]

    AC --> AD[Artifact Hash Verification]
    AC --> AE[Metric Reproduction Check]
    AC --> AF[Rollback Validation]

    AD --> AG[Self-Healing Completed]
    AE --> AG
    AF --> AG

    AG --> AH[Persist Accepted Baseline]

    AH --> AI[Generate Reliability Snapshot]

    AI --> AJ[FastAPI Backend]

    AJ --> AK[Next.js Dashboard]

    AK --> L
```

---

# Reliability Monitoring Architecture

The platform monitors multiple dimensions independently.

```mermaid
flowchart LR

    A[Production Batch]

    A --> B[Data Quality]
    A --> C[Data Drift]
    A --> D[Model Performance]
    A --> E[Anomaly Detection]

    B --> F[HEALTHY / WARNING / CRITICAL]
    C --> F
    D --> F
    E --> F

    C --> G[Feature Drift Scores]
    H[Model Feature Importance] --> I[Root Cause Engine]
    G --> I

    I --> J[Root Cause Priority]

    F --> K[Overall Reliability Status]
    J --> K
```

The overall system status is determined from the individual monitoring subsystems.

A model can therefore be healthy while the overall AI system remains critical.

For example:

```text
Data Quality        HEALTHY
Data Drift          CRITICAL
Model Performance   HEALTHY
Anomaly Detection   HEALTHY

Overall Reliability CRITICAL
```

This prevents successful model retraining from hiding unresolved production-data problems.

---

# Self-Healing Architecture

```mermaid
flowchart TD

    A[Active Champion] --> B[Performance Monitor]
    C[Accepted Champion Baseline] --> B
    D[New Production Data] --> B

    B --> E{Performance Drop}

    E -- Below Threshold --> F[Continue Monitoring]

    E -- Warning --> G[Monitor Closely]

    E -- Critical --> H[Trigger Self-Healing]

    H --> I[Prepare Recent Training Data]

    J[Historical Training Data] --> K[Train Challenger]
    I --> K

    K --> L[Challenger Model]

    D --> M[Untouched Validation Split]

    A --> N[Evaluate Champion]
    L --> O[Evaluate Challenger]

    M --> N
    M --> O

    N --> P[Quality Gate]
    O --> P

    P --> Q{Eligible?}

    Q -- No --> R[Reject Challenger]

    Q -- Yes --> S[Register Challenger]

    S --> T[Promote Challenger]

    T --> U[Verify Deployment]

    U --> V[Save Previous Champion]

    V --> W[Rollback Available]

    W --> X[Persist New Accepted Baseline]

    X --> F
```

---

# Promotion Quality Gate

The challenger must pass all predefined conditions.

```text
F1 improvement        >= 0.05
Recall improvement    >= 0.00
Precision drop        <= 0.02
```

The gate is evaluated using the same untouched validation dataset for both models.

This ensures that the champion and challenger are compared fairly.

---

# Model Lifecycle

```mermaid
stateDiagram-v2

    [*] --> V1_Champion

    V1_Champion --> V2_Challenger: Retraining

    V2_Challenger --> V1_Champion: Quality Gate Failed

    V2_Challenger --> V2_Champion: Quality Gate Passed

    V2_Champion --> V3_Challenger: Critical Degradation

    V3_Challenger --> V2_Champion: Quality Gate Failed

    V3_Challenger --> V3_Champion: Quality Gate Passed

    V3_Champion --> V2_Champion: Rollback

    V3_Champion --> Monitoring

    Monitoring --> V3_Challenger: Future Degradation
```

---

# Current Demonstration Lifecycle

The completed demonstration followed this model lifecycle:

```text
V1
 ↓
Initial Champion

V2
 ↓
First promoted challenger
 ↓
Accepted V2 baseline persisted

Batch 2 arrives
 ↓
Critical F1 + Recall degradation detected
 ↓
V3 challenger trained
 ↓
V2 and V3 tested on same untouched validation set
 ↓
V3 passes quality gate
 ↓
V3 registered
 ↓
V3 promoted
 ↓
V2 archived
 ↓
Deployment verified
 ↓
V3 accepted baseline persisted
 ↓
Rollback to V2 remains available
```

---

# Backend Architecture

```mermaid
flowchart LR

    A[Next.js Frontend]

    A --> B[FastAPI]

    B --> C[/api/reliability]
    B --> D[/api/performance]
    B --> E[/api/drift]
    B --> F[/api/anomalies]
    B --> G[/api/root-causes]
    B --> H[/api/deployment]
    B --> I[/api/self-healing]

    C --> J[reliability_snapshot.json]

    H --> K[deployment_state.json]

    I --> L[self_healing_state.json]

    D --> M[Performance Monitor]
    E --> N[Drift Monitor]
    F --> O[Anomaly Detector]
    G --> P[Root Cause Service]
```

---

# Production Deployment Architecture

```mermaid
flowchart LR

    A[GitHub Repository]

    A --> B[Render]
    A --> C[Netlify]

    B --> D[FastAPI Backend]

    C --> E[Next.js Frontend]

    E -->|HTTPS REST API| D

    D --> F[Reliability Snapshot]
    D --> G[Deployment State]
    D --> H[Self-Healing State]

    E --> I[User Dashboard]
```

---

# Reliability Snapshot Architecture

Running all ML monitoring calculations on every API request would be expensive.

The platform therefore uses:

```text
ML Computation
      ↓
Reliability Report
      ↓
JSON Snapshot
      ↓
FastAPI
      ↓
Dashboard
```

The snapshot is generated using:

```powershell
python -m scripts.generate_reliability_snapshot
```

and stored as:

```text
models/reliability_snapshot.json
```

This allows the deployed backend to serve monitoring results without repeatedly loading heavy ML components.

---

# Main Components

| Component | Responsibility |
|---|---|
| Data Quality Monitor | Detect schema and data-quality problems |
| Drift Monitor | Detect numerical and categorical distribution changes |
| Performance Monitor | Evaluate champion model metrics |
| Anomaly Detector | Detect unusual production transactions |
| Root Cause Service | Prioritize drifted and influential features |
| Healing Trigger | Decide when automatic recovery is required |
| Challenger Trainer | Retrain using historical and recent data |
| Quality Gate | Decide whether challenger can be promoted |
| MLflow Registry | Maintain model version lineage |
| Promotion Service | Replace active champion |
| Verification Service | Validate promoted artifact and metrics |
| Baseline Service | Persist accepted champion performance |
| Snapshot Service | Serve lightweight monitoring results |
| FastAPI | Provide reliability APIs |
| Next.js | Present the reliability dashboard |

---

# Design Principle

The architecture intentionally separates:

```text
Data Reliability
Model Reliability
Operational Reliability
Recovery State
```

A successful self-healing event does not automatically mean the complete AI system is healthy.

This separation allows the system to report situations such as:

```text
Model recovered successfully
BUT
production data continues to drift
```

which is the current demonstrated system state.