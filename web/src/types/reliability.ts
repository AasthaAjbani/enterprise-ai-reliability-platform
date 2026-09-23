export type ReliabilityStatus =
  | "HEALTHY"
  | "WARNING"
  | "CRITICAL";


export interface DataQuality {
  status: ReliabilityStatus;
  score: number;

  missing_columns: string[];

  missing_values: Record<
    string,
    number
  >;

  duplicates: number;

  numerical_issues: Record<
    string,
    number
  >;

  categorical_issues: Record<
    string,
    number
  >;
}


export interface DriftFeature {
  feature: string;

  feature_type:
    | "numerical"
    | "categorical";

  drift_level:
    | "LOW"
    | "MODERATE"
    | "HIGH";

  score: number;

  p_value:
    | number
    | null;
}


export interface DataDrift {
  status: ReliabilityStatus;

  features: DriftFeature[];
}


export interface PerformanceMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;

  confusion_matrix: number[][];
}


export interface PerformanceDrop {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}


export interface ModelPerformance {
  status: ReliabilityStatus;

  reference: PerformanceMetrics;

  production: PerformanceMetrics;

  performance_drop: PerformanceDrop;
}


export interface AnomalyTransaction {
  transaction_id: number;

  customer_age?: number;

  transaction_amount: number;

  transaction_hour: number;

  payment_method?: string;

  device_type?: string;

  customer_location?: string;

  account_age_days: number;

  previous_transactions?: number;

  failed_transactions_last_24h: number;

  is_international: number;

  anomaly_score: number;

  is_anomaly?: boolean;
}


export interface AnomalyDetection {
  status: ReliabilityStatus;

  total_transactions: number;

  anomaly_count: number;

  anomaly_percentage: number;

  top_anomalies:
    AnomalyTransaction[];
}


export interface RootCause {
  feature: string;

  feature_type: string;

  drift_level:
    | "LOW"
    | "MODERATE"
    | "HIGH";

  score: number;

  p_value:
    | number
    | null;

  model_importance: number;

  root_cause_score: number;

  root_cause_priority:
    | "LOW"
    | "MEDIUM"
    | "HIGH";
}


export interface ReliabilityReport {
  overall_status:
    ReliabilityStatus;

  data_quality:
    DataQuality;

  data_drift:
    DataDrift;

  model_performance:
    ModelPerformance;

  anomaly_detection:
    AnomalyDetection;

  root_causes:
    RootCause[];

  recommendation:
    string;
}