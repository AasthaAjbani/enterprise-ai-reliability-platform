export interface HealingPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}


export interface HealingDegradation {
  f1_drop: number;
  recall_drop: number;
}


export interface HealingThresholds {
  warning_drop: number;
  critical_drop: number;
}


export interface HealingTrigger {
  status:
    | "HEALTHY"
    | "WARNING"
    | "CRITICAL";

  healing_required: boolean;

  reason: string;

  thresholds: HealingThresholds;

  baseline: HealingPerformance;

  production: HealingPerformance;

  degradation: HealingDegradation;
}


export interface HealingQualityGate {
  eligible: boolean;
  decision: string | null;

  f1_improvement: number | null;
  recall_improvement: number | null;
  precision_change: number | null;
}


export interface SelfHealingStatus {
  pipeline?: string;

  status:
    | "NOT_RUN"
    | "RUNNING"
    | "NO_HEALING_REQUIRED"
    | "COMPLETED_NO_PROMOTION"
    | "SELF_HEALED"
    | "FAILED";

  current_stage: string | null;

  started_at: string | null;
  updated_at: string | null;
  completed_at: string | null;

  duration_seconds?: number | null;

  healing_required: boolean | null;

  healing_trigger: HealingTrigger | null;

  quality_gate: HealingQualityGate | null;

  promotion_attempted: boolean;

  promotion_completed: boolean;

  verification_completed: boolean;

  champion_version: string | null;

  previous_champion_version: string | null;

  rollback_available: boolean;

  failure_stage: string | null;

  error: string | null;
}