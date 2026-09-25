# Enterprise AI Reliability Platform

An end-to-end **AI reliability and self-healing platform** designed to monitor machine learning systems after deployment, detect reliability failures, diagnose likely causes, and automatically recover from severe model degradation through controlled retraining and champion–challenger promotion.

The project demonstrates a production-oriented ML reliability workflow using **FastAPI, Next.js, scikit-learn, MLflow, Render, and Netlify**.

---

## Live Application

### Dashboard

https://enterprise-ai-reliability-platform.netlify.app

### Backend API

https://enterprise-ai-reliability-platform.onrender.com

### GitHub Repository

https://github.com/AasthaAjbani/enterprise-ai-reliability-platform

---

# Project Overview

Machine learning models can perform well during development but degrade after deployment when real-world data changes.

Traditional ML applications often stop after:

```text
Train Model
    ↓
Evaluate Model
    ↓
Deploy Model
```

This project extends the lifecycle to:

```text
Train
  ↓
Deploy
  ↓
Monitor
  ↓
Detect Reliability Problems
  ↓
Diagnose
  ↓
Trigger Recovery
  ↓
Train Challenger
  ↓
Validate Challenger
  ↓
Promote New Champion
  ↓
Verify Deployment
  ↓
Continue Monitoring
```

The platform continuously evaluates several reliability dimensions:

- Data quality
- Data drift
- Model performance
- Transaction anomalies
- Feature-level root-cause signals
- Model deployment state
- Self-healing lifecycle state

---

# Key Features

## AI Reliability Dashboard

A modern dashboard presents the current state of the ML system, including:

- Overall reliability status
- Data drift severity
- Model performance
- Data quality
- Anomaly detection
- Root-cause indicators
- Champion model version
- Previous model version
- Rollback availability
- Self-healing lifecycle

---

## Data Drift Detection

The platform compares reference data against new production data.

### Numerical features

Drift is detected using the **Kolmogorov-Smirnov test**.

### Categorical features

Categorical distribution differences are evaluated using **Total Variation Distance**.

Each feature is classified as:

```text
LOW
MODERATE
HIGH
```

The system aggregates feature-level drift into an overall drift status:

```text
HEALTHY
WARNING
CRITICAL
```

---

## Data Quality Monitoring

Production data is automatically checked for:

- Missing columns
- Missing values
- Duplicate records
- Invalid numerical ranges
- Unexpected categorical values

The platform generates a data quality score and health status.

---

## Model Performance Monitoring

The active production model is evaluated using:

- Accuracy
- Precision
- Recall
- F1 score
- Confusion matrix

For promoted models, the monitoring service uses the model's **persisted accepted baseline**, rather than comparing against an outdated original model.

This makes monitoring version-aware.

---

# Self-Healing ML Pipeline

The main feature of the platform is its autonomous recovery workflow.

When severe model performance degradation is detected, the system can execute:

```text
Performance Degradation
        ↓
Healing Trigger
        ↓
Train Challenger
        ↓
Evaluate Champion vs Challenger
        ↓
Quality Gate
        ↓
Register Challenger
        ↓
Promote Challenger
        ↓
Verify Deployment
        ↓
Preserve Previous Champion
        ↓
Rollback Available
```

---

## Healing Trigger

The system monitors degradation in important fraud-classification metrics.

Thresholds:

```text
Warning degradation  = 5 percentage points
Critical degradation = 15 percentage points
```

Automatic healing occurs only when the status becomes:

```text
CRITICAL
```

This avoids unnecessary retraining for small fluctuations.

---

## Champion–Challenger Training

When healing is triggered:

1. Historical reference data is used as stable training context.
2. Recent production data is split into:
   - 70% recent training data
   - 30% untouched validation data
3. The challenger is trained using historical + recent training data.
4. Both the current champion and challenger are evaluated on the same untouched validation set.

This prevents the promotion decision from being based on training data.

---

# Quality Gate

A challenger is not promoted simply because retraining completed.

The challenger must satisfy predefined promotion rules.

Current rules:

```text
Minimum F1 improvement       >= 0.05
Minimum Recall improvement   >= 0.00
Maximum Precision drop       <= 0.02
```

All conditions must pass.

If the challenger fails the quality gate, the current champion remains active.

---

# Model Registry

MLflow is used to track the model lifecycle.

Registered model:

```text
FraudDetectionModel
```

Important aliases:

```text
champion
challenger
previous_champion
```

This creates a clear model lineage and allows rollback.

---

# Deployment Verification

Promotion is followed by a verification stage.

The platform confirms:

- The expected champion version was promoted
- The active model artifact matches the challenger artifact
- The deployed model reproduces expected validation metrics
- The previous champion remains available
- Rollback is possible

Artifact hashes are used to verify that the promoted model is the correct model.

---

# Self-Healing Demonstration

A controlled second production batch was generated to simulate concept drift that was not used to train the current V2 champion.

The active V2 model experienced severe degradation.

## Degradation Trigger

| Metric | V2 Accepted Baseline | New Production Batch |
|---|---:|---:|
| Accuracy | 88.87% | 90.46% |
| Precision | 23.48% | 8.70% |
| Recall | 25.47% | 1.43% |
| F1 | 24.43% | 2.45% |

The large recall and F1 degradation caused the system to enter:

```text
CRITICAL
```

and triggered self-healing.

---

# Challenger Evaluation

V2 and V3 were evaluated using the same untouched 30% validation split.

| Metric | V2 Champion | V3 Challenger |
|---|---:|---:|
| Accuracy | 90.20% | 87.13% |
| Precision | 11.11% | 16.83% |
| Recall | 2.38% | 13.49% |
| F1 | 3.92% | 14.98% |

Improvements:

```text
F1 improvement        +11.06 percentage points
Recall improvement    +11.11 percentage points
Precision change       +5.72 percentage points
```

The challenger passed the quality gate.

---

# Successful Recovery

The V3 challenger was promoted to production.

Final lifecycle state:

```text
Self-Healing Status     SELF_HEALED
Active Champion         V3
Previous Champion       V2
Promotion Completed     Yes
Verification Completed  Yes
Rollback Available      Yes
Recovery Time           22.87 seconds
```

---

# Post-Healing Monitoring

After promotion:

```text
Overall Reliability     CRITICAL
Data Quality            HEALTHY
Data Drift              CRITICAL
Model Performance       HEALTHY
Anomaly Detection       HEALTHY
```

This is intentional.

The self-healing process corrected the model performance degradation, but the underlying production distribution still contains significant drift.

The platform therefore does **not** incorrectly report the entire system as healthy after retraining.

This demonstrates the difference between:

```text
Model health
```

and:

```text
System reliability
```

---

# Root-Cause Analysis

The platform combines:

```text
Feature Drift Score
        ×
Model Feature Importance
        ×
100
```

to generate a root-cause priority score.

Example high-priority feature:

```text
previous_transactions
```

The result is intended as a **diagnostic heuristic**, not proof of causal relationships.

---

# Anomaly Detection

Transaction-level anomaly detection uses:

```text
Isolation Forest
```

with numerical feature standardization.

Current monitored production batch:

```text
Transactions       5000
Anomalies           207
Anomaly Rate       4.14%
Status             HEALTHY
```

---

# System Architecture

```text
                    ┌─────────────────────┐
                    │   Production Data   │
                    └──────────┬──────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │   Reliability Engine     │
                 └─────────────┬────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
 ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
 │ Data Quality   │   │ Data Drift     │   │ Anomaly        │
 │ Monitoring     │   │ Detection      │   │ Detection      │
 └────────────────┘   └────────────────┘   └────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Model Performance  │
                    │ Monitoring         │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Healing Trigger    │
                    └──────────┬─────────┘
                               │
                    CRITICAL degradation
                               │
                               ▼
                    ┌────────────────────┐
                    │ Challenger Trainer │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Quality Gate       │
                    └──────────┬─────────┘
                               │
                             PASS
                               │
                               ▼
                    ┌────────────────────┐
                    │ MLflow Registry    │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Champion Promotion │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Deployment Verify  │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Rollback Available │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ FastAPI Backend    │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Next.js Dashboard  │
                    └────────────────────┘
```

---

# Technology Stack

## Machine Learning

- Python
- scikit-learn
- Pandas
- NumPy
- Joblib

## Reliability & MLOps

- MLflow
- Champion–challenger model lifecycle
- Model versioning
- Artifact hash verification
- Reliability snapshots
- Automated retraining
- Promotion quality gates
- Rollback support

## Backend

- FastAPI
- Uvicorn
- REST APIs

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Lucide React

## Deployment

- Render — backend
- Netlify — frontend
- GitHub — version control

---

# Project Structure

```text
enterprise-ai-reliability-platform/
│
├── app/
│   ├── api/
│   ├── monitoring/
│   ├── services/
│   └── main.py
│
├── data/
│   ├── reference/
│   └── production/
│
├── models/
│   ├── fraud_model.joblib
│   ├── baseline_metrics.json
│   ├── challenger_comparison.json
│   ├── deployment_state.json
│   ├── self_healing_state.json
│   └── reliability_snapshot.json
│
├── scripts/
│   ├── train_fraud_model.py
│   ├── train_challenger_model.py
│   ├── generate_unseen_production_batch.py
│   ├── register_challenger_mlflow.py
│   ├── promote_challenger.py
│   ├── verify_promotion.py
│   ├── run_self_healing_pipeline.py
│   └── generate_reliability_snapshot.py
│
├── frontend/
│   └── legacy Streamlit monitoring interface
│
├── web/
│   ├── src/
│   ├── package.json
│   └── next.config.ts
│
├── requirements.txt
├── netlify.toml
└── README.md
```

---

# API Endpoints

## Health Check

```http
GET /health
```

---

## Complete Reliability Report

```http
GET /api/reliability
```

Returns:

- Overall system health
- Data quality
- Data drift
- Model performance
- Anomaly detection
- Root causes
- Recommendation

---

## Data Quality

```http
GET /api/data-quality
```

---

## Drift Monitoring

```http
GET /api/drift
```

---

## Performance Monitoring

```http
GET /api/performance
```

---

## Anomaly Monitoring

```http
GET /api/anomalies
```

---

## Root-Cause Analysis

```http
GET /api/root-causes
```

---

## Deployment State

```http
GET /api/deployment
```

Returns information about:

```text
Current champion
Previous champion
Rollback state
Quality gate decision
Validation metrics
```

---

## Self-Healing State

```http
GET /api/self-healing
```

Returns the autonomous recovery lifecycle state.

---

# Local Installation

## 1. Clone the repository

```powershell
git clone https://github.com/AasthaAjbani/enterprise-ai-reliability-platform.git

cd enterprise-ai-reliability-platform
```

---

## 2. Create a Python virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Start the FastAPI backend

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open another terminal.

```powershell
cd web
```

Install dependencies:

```powershell
npm install
```

Create:

```text
web/.env.local
```

with:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Start the application:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:3000
```

Dashboard:

```text
http://localhost:3000/dashboard
```

---

# Running the Self-Healing Pipeline

Activate the Python environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Select the production batch:

```powershell
$env:HEALING_PRODUCTION_DATA="data/production/transactions_production_batch_2.csv"
```

Run:

```powershell
python -m scripts.run_self_healing_pipeline
```

The pipeline performs:

```text
1. Reliability trigger evaluation
2. Challenger training
3. Champion vs challenger comparison
4. Promotion quality gate
5. MLflow registration
6. Champion promotion
7. Deployment verification
8. Rollback preservation
```

---

# Generate Reliability Snapshot

Production API requests use a precomputed reliability snapshot to avoid expensive ML computation on every request.

Generate it using:

```powershell
python -m scripts.generate_reliability_snapshot
```

Generated file:

```text
models/reliability_snapshot.json
```

The API can then serve the monitoring dashboard using the lightweight snapshot.

---

# Deployment Architecture

## Frontend

Hosted on:

```text
Netlify
```

Environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://enterprise-ai-reliability-platform.onrender.com
```

---

## Backend

Hosted on:

```text
Render
```

Production CORS configuration allows requests from the deployed Netlify frontend.

---

# Design Decisions

## Why use F1 and Recall?

The project uses fraud classification, which is an imbalanced classification problem.

Accuracy alone can therefore be misleading.

For example, a model could predict most transactions as legitimate and still achieve high accuracy while failing to identify fraudulent transactions.

For this reason, the promotion gate emphasizes:

```text
Recall
F1 score
```

while still controlling precision loss.

---

## Why can V3 have lower accuracy but still be promoted?

V3 achieved slightly lower overall accuracy but substantially improved:

- Fraud recall
- F1 score
- Precision

Because detecting fraud is the minority-class objective, those improvements are more important than a small reduction in overall accuracy.

Promotion is therefore determined using predefined reliability criteria rather than accuracy alone.

---

## Why is the system still CRITICAL after self-healing?

The model performance recovered successfully.

However, significant data distribution drift remains present in production data.

Therefore:

```text
Model Performance = HEALTHY

but

Overall Reliability = CRITICAL
```

The platform keeps these concepts separate rather than assuming successful retraining fixes every reliability issue.

---

# Limitations

This project is an engineering and ML reliability demonstration rather than a live financial production system.

Current limitations include:

- Synthetic fraud datasets
- Controlled concept-drift scenarios
- MLflow registry running locally during self-healing experiments
- Root-cause ranking is heuristic rather than causal inference
- Automated healing is demonstrated through controlled batch execution
- Real-time streaming monitoring is not implemented
- Production model approval does not include a human governance workflow

---

# Future Enhancements

Potential extensions include:

- Kafka-based streaming monitoring
- Cloud-based MLflow model registry
- Scheduled monitoring jobs
- Human approval before model promotion
- Automated rollback triggers
- Feature-store integration
- SHAP-based model explainability
- Advanced drift detectors
- Model fairness monitoring
- Notification integration using Slack or email
- Kubernetes deployment
- CI/CD model validation
- Multiple model support
- Authentication and role-based access control

---

# Project Goal

The objective of this project is not simply to train a machine learning model.

It is to demonstrate how an AI system can be engineered to:

```text
Detect failure
Understand reliability signals
Recover safely
Validate improvements
Preserve rollback
Continue monitoring
```

This represents the broader engineering requirements required for building dependable AI systems beyond model training alone.

---

# Author

**Aastha Ajbani**

B.Tech Computer Science / Data Science Project

GitHub:

https://github.com/AasthaAjbani