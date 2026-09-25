# Enterprise AI Reliability Platform — Demo Flow

This document describes the recommended live demonstration sequence for the Enterprise AI Reliability Platform.

The goal of the demo is to show that the project is not only an ML classifier, but a complete reliability system that can:

```text
Monitor
Detect degradation
Diagnose reliability issues
Trigger recovery
Train a challenger
Validate it safely
Promote a new champion
Verify deployment
Preserve rollback
Continue monitoring
```

---

# Demo Duration

Recommended duration:

```text
5–7 minutes
```

---

# Demo Story

The demonstration follows this scenario:

```text
V2 is the active production champion
        ↓
A new production batch arrives
        ↓
The production distribution changes
        ↓
V2 performance degrades severely
        ↓
The system detects CRITICAL degradation
        ↓
Self-healing is triggered
        ↓
V3 challenger is trained
        ↓
V2 and V3 are evaluated fairly
        ↓
V3 passes the quality gate
        ↓
V3 becomes the new champion
        ↓
Deployment is verified
        ↓
V2 remains available for rollback
        ↓
Monitoring continues
```

---

# Step 1 — Open the Production Dashboard

Open:

```text
https://enterprise-ai-reliability-platform.netlify.app/dashboard
```

Explain:

> This is the central AI reliability dashboard.  
> It monitors multiple reliability dimensions instead of only displaying model accuracy.

Show:

```text
Overall Reliability
Data Drift
Model Performance
Anomalies
Root Cause
```

---

# Step 2 — Explain the Current Overall Status

The dashboard currently shows:

```text
SYSTEM RELIABILITY IS CRITICAL
```

Explain:

> The overall system is critical because significant production-data drift still exists.

Important distinction:

```text
Overall Reliability     CRITICAL
Model Performance       HEALTHY
```

Explain:

> The model has recovered successfully, but the system does not hide unresolved data-distribution problems.

This is intentional.

---

# Step 3 — Show Data Drift

Open:

```text
/drift
```

Show that different features have different drift levels:

```text
LOW
MODERATE
HIGH
```

Important examples from the current production batch:

```text
previous_transactions              HIGH
failed_transactions_last_24h       HIGH
payment_method                     HIGH

transaction_hour                   MODERATE
device_type                        MODERATE
```

Explain:

> Numerical drift is detected using the Kolmogorov-Smirnov test.

> Categorical drift is measured using Total Variation Distance.

---

# Step 4 — Show Root Cause Analysis

Open:

```text
/root-cause
```

Show:

```text
Top Root Cause:
previous_transactions
```

Explain:

> The system combines feature drift with model feature importance to prioritize likely reliability contributors.

The heuristic is:

```text
Drift Score
    ×
Model Importance
    ×
100
```

Important clarification:

> This is a diagnostic prioritization heuristic and not proof of causal relationships.

---

# Step 5 — Show Model Performance

Open:

```text
/performance
```

Show:

```text
Status: HEALTHY
```

Current V3 monitoring baseline:

```text
Accuracy    87.13%
Precision   16.83%
Recall      13.49%
F1          14.98%
```

The current monitoring evaluation reproduces the accepted V3 baseline.

Therefore:

```text
Performance Drop = 0
```

Explain:

> After promotion, the new champion receives its own accepted performance baseline.

> Future degradation is measured against the active champion rather than against an outdated model.

---

# Step 6 — Show Anomaly Detection

Open:

```text
/anomalies
```

Current batch:

```text
Total Transactions     5000
Detected Anomalies      207
Anomaly Rate           4.14%
Status                 HEALTHY
```

Explain:

> Isolation Forest is used to detect unusual transaction patterns independently from the fraud classifier.

---

# Step 7 — Show the Self-Healing Lifecycle

Return to:

```text
/dashboard
```

Scroll to:

```text
SELF-HEALING LIFECYCLE
```

Show:

```text
Active Champion       V3
Previous Champion     V2
Rollback              AVAILABLE
Recovery Time         22.87s
```

Then show the four completed stages:

```text
01 Degradation detected
02 Challenger qualified
03 Champion promoted
04 Deployment verified
```

---

# Step 8 — Explain the Trigger Evidence

Show:

```text
Trigger Evidence
```

Before degradation, V2 had the accepted baseline:

| Metric | V2 Accepted Baseline |
|---|---:|
| Accuracy | 88.87% |
| Precision | 23.48% |
| Recall | 25.47% |
| F1 | 24.43% |

When Batch 2 arrived:

| Metric | V2 on New Production Batch |
|---|---:|
| Accuracy | 90.46% |
| Precision | 8.70% |
| Recall | 1.43% |
| F1 | 2.45% |

Explain:

> Accuracy alone looks acceptable.

But:

```text
Recall:
25.47% → 1.43%

F1:
24.43% → 2.45%
```

This caused:

```text
CRITICAL
```

Explain:

> This is why the system does not use accuracy alone for an imbalanced fraud problem.

---

# Step 9 — Explain Challenger Training

When healing was triggered:

```text
Historical Reference Training Data
+
70% of Recent Production Batch
```

were used to train V3.

The remaining:

```text
30%
```

was kept untouched for validation.

Explain:

> The validation data was never used to train the challenger.

---

# Step 10 — Show Champion vs Challenger Evaluation

The same untouched validation set was used to evaluate both models.

| Metric | V2 | V3 |
|---|---:|---:|
| Accuracy | 90.20% | 87.13% |
| Precision | 11.11% | 16.83% |
| Recall | 2.38% | 13.49% |
| F1 | 3.92% | 14.98% |

Explain:

> V3 slightly reduced overall accuracy but substantially improved the metrics that matter for minority-class fraud detection.

Quality-gate improvements:

```text
F1 improvement        +11.06 percentage points
Recall improvement    +11.11 percentage points
Precision change       +5.72 percentage points
```

---

# Step 11 — Explain the Promotion Gate

Promotion rules:

```text
Minimum F1 improvement       >= 0.05
Minimum Recall improvement   >= 0.00
Maximum Precision drop       <= 0.02
```

V3 passed all conditions.

Therefore:

```text
CHALLENGER_ELIGIBLE_FOR_PROMOTION
```

---

# Step 12 — Explain MLflow Model Lifecycle

The registered model is:

```text
FraudDetectionModel
```

Model lifecycle:

```text
V2
Champion before recovery

V3
Challenger

After successful validation:

champion          → V3
previous_champion → V2
```

Explain:

> Model aliases make the deployment lifecycle explicit and allow the system to preserve the previous version.

---

# Step 13 — Explain Deployment Verification

After promotion, the platform verifies:

```text
Correct model version promoted
Correct artifact deployed
Expected metrics reproduced
Previous model preserved
Rollback available
```

Artifact hashes are used to confirm that:

```text
Active Model Artifact
=
Validated Challenger Artifact
```

---

# Step 14 — Show Rollback Capability

Show:

```text
Previous Champion     V2
Rollback Available    YES
```

Explain:

> The previous model is preserved instead of being deleted.

> If the new champion fails operational checks later, the system has a known previous model available for recovery.

---

# Step 15 — Final Demo Message

End the demo with:

> The purpose of this project is not just to train a machine learning model.

> It demonstrates how an AI system can detect degradation, diagnose reliability signals, retrain safely, compare models fairly, promote a better version, verify deployment, preserve rollback, and continue monitoring after recovery.

---

# Screenshot Checklist

Store screenshots inside:

```text
docs/screenshots/
```

Recommended screenshots:

```text
01-home.png
02-dashboard-overview.png
03-performance.png
04-drift.png
05-anomalies.png
06-root-cause.png
07-self-healing-lifecycle.png
08-trigger-evidence.png
09-promotion-validation.png
10-api-docs.png
```

---

# Screenshot 01 — Home Page

Capture:

```text
/
```

Include:

- Project title
- Landing-page design
- Navigation

Save as:

```text
docs/screenshots/01-home.png
```

---

# Screenshot 02 — Dashboard Overview

Capture:

```text
/dashboard
```

Include:

```text
SYSTEM RELIABILITY IS CRITICAL
Data Drift
Performance
Anomalies
Root Cause
```

Save as:

```text
docs/screenshots/02-dashboard-overview.png
```

---

# Screenshot 03 — Performance

Capture:

```text
/performance
```

Show V3:

```text
Status HEALTHY
F1 14.98%
Recall 13.49%
```

Save as:

```text
docs/screenshots/03-performance.png
```

---

# Screenshot 04 — Drift

Capture:

```text
/drift
```

Include multiple:

```text
HIGH
MODERATE
LOW
```

features.

Save as:

```text
docs/screenshots/04-drift.png
```

---

# Screenshot 05 — Anomalies

Capture:

```text
/anomalies
```

Include:

```text
207 anomalies
4.14%
HEALTHY
```

Save as:

```text
docs/screenshots/05-anomalies.png
```

---

# Screenshot 06 — Root Cause

Capture:

```text
/root-cause
```

Show:

```text
previous_transactions
HIGH PRIORITY
```

Save as:

```text
docs/screenshots/06-root-cause.png
```

---

# Screenshot 07 — Self-Healing Lifecycle

Capture the dashboard section showing:

```text
Active Champion V3
Previous Champion V2
Rollback AVAILABLE
Recovery Time 22.87s
```

and:

```text
Degradation detected
Challenger qualified
Champion promoted
Deployment verified
```

Save as:

```text
docs/screenshots/07-self-healing-lifecycle.png
```

---

# Screenshot 08 — Trigger Evidence

Capture:

```text
F1
24.43% → 2.45%

Recall
25.47% → 1.43%
```

Save as:

```text
docs/screenshots/08-trigger-evidence.png
```

---

# Screenshot 09 — Promotion Validation

Capture:

```text
V2 F1      3.92%
V3 F1     14.98%

V2 Recall  2.38%
V3 Recall 13.49%
```

Save as:

```text
docs/screenshots/09-promotion-validation.png
```

---

# Screenshot 10 — FastAPI Documentation

Open:

```text
https://enterprise-ai-reliability-platform.onrender.com/docs
```

Capture the available REST endpoints.

Save as:

```text
docs/screenshots/10-api-docs.png
```

---

# Important Presentation Note

Do not say:

```text
The system fixed all problems automatically.
```

Instead say:

```text
The self-healing pipeline recovered model performance,
while continued monitoring still detects unresolved
production-data drift.
```

This accurately represents the current system.