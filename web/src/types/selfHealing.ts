export interface HealingMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}


export interface HealingTrigger {
  status: string;

  healing_required: boolean;

  reason: string;

  thresholds: {
    warning_drop: number;
    critical_drop: number;
  };

  baseline_metadata: {
    source: string;

    champion_version:
      | string
      | null;

    previous_champion_version:
      | string
      | null;

    validation_type: string;

    validation_fraction:
      | number
      | null;
  };

  baseline:
    HealingMetrics;

  production:
    HealingMetrics;

  degradation: {
    accuracy_drop: number;
    precision_drop: number;
    recall_drop: number;
    f1_drop: number;
  };

  evaluation: {
    dataset_path: string;
  };
}


export interface HealingQualityGate {
  eligible: boolean;

  decision: string;

  f1_improvement: number;

  recall_improvement: number;

  precision_change: number;
}


export interface SelfHealingState {
  pipeline: string;

  status: string;

  current_stage: string;

  started_at: string;

  updated_at: string;

  completed_at:
    | string
    | null;

  healing_trigger:
    | HealingTrigger
    | null;

  healing_required: boolean;

  quality_gate:
    | HealingQualityGate
    | null;

  promotion_attempted: boolean;

  promotion_completed: boolean;

  verification_completed: boolean;

  champion_version:
    | string
    | null;

  previous_champion_version:
    | string
    | null;

  rollback_available: boolean;

  failure_stage:
    | string
    | null;

  error:
    | string
    | null;

  duration_seconds:
    | number
    | null;
}