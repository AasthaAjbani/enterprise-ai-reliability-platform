export interface MetricSet {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  confusion_matrix?: number[][];
}


export interface DeploymentQualityGate {
  decision: string;
  eligible: boolean;

  f1_improvement: number;
  recall_improvement: number;
  precision_change: number;

  criteria?: {
    minimum_f1_improvement: number;
    minimum_recall_improvement: number;
    maximum_precision_drop: number;

    f1_pass: boolean;
    recall_pass: boolean;
    precision_pass: boolean;
  };
}


export interface DeploymentValidation {
  strategy: string;
  validation_fraction: number;

  previous_model: MetricSet;
  promoted_model: MetricSet;
}


export interface DeploymentState {
  status: string;

  registered_model: string;

  champion_version: string;

  previous_champion_version:
    | string
    | null;

  rollback_available: boolean;

  promoted_at:
    | string
    | null;

  quality_gate:
    DeploymentQualityGate;

  validation:
    DeploymentValidation;
}