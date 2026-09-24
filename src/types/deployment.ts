export type DeploymentStatusValue =
  | "PROMOTED"
  | "ROLLED_BACK"
  | "NOT_DEPLOYED";


export interface DeploymentMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  confusion_matrix?: number[][];
}


export interface PromotionCriteria {
  minimum_f1_improvement: number;
  minimum_recall_improvement: number;
  maximum_precision_drop: number;

  f1_pass: boolean;
  recall_pass: boolean;
  precision_pass: boolean;
}


export interface QualityGate {
  decision: string | null;
  eligible: boolean | null;

  f1_improvement: number | null;
  recall_improvement: number | null;
  precision_change: number | null;

  criteria: PromotionCriteria | null;
}


export interface DeploymentValidation {
  strategy: string | null;
  validation_fraction: number | null;

  previous_model: DeploymentMetrics | null;
  promoted_model: DeploymentMetrics | null;
}


export interface DeploymentStatus {
  status: DeploymentStatusValue;

  registered_model: string;

  champion_version: string | null;

  previous_champion_version:
    | string
    | null;

  rollback_available: boolean;

  promoted_at: string | null;

  quality_gate: QualityGate | null;

  validation: DeploymentValidation | null;
}