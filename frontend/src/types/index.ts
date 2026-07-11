export type Gender = "Male" | "Female";
export type YesNo = "Yes" | "No";
export type Dependents = "0" | "1" | "2" | "3+";
export type Education = "Graduate" | "Not Graduate";
export type PropertyArea = "Urban" | "Semiurban" | "Rural";

export interface LoanApplicationInput {
  applicant_name: string;
  age: number;
  gender: Gender;
  married: YesNo;
  dependents: Dependents;
  education: Education;
  self_employed: YesNo;
  applicant_income: number;
  coapplicant_income: number;
  loan_amount: number;
  loan_amount_term: number;
  credit_history: 0 | 1;
  property_area: PropertyArea;
  existing_debt: number;
  savings: number;
}

export interface ShapFactor {
  feature: string;
  impact: number;
  direction: "positive" | "negative";
  human_readable: string;
}

export interface RiskFactor {
  name: string;
  points: number;
  reason: string;
}

export interface PredictionResponse {
  application_id: string;
  decision: "Approved" | "Rejected";
  confidence: number;
  approval_probability: number;
  model_used: string;
  risk_score: number;
  risk_category: string;
  risk_factors: RiskFactor[];
  top_positive_factors: ShapFactor[];
  top_negative_factors: ShapFactor[];
  explanation_summary: string;
  recommendations: string[];
  created_at: string;
}

export interface RiskScoreResponse {
  score: number;
  category: string;
  factors: RiskFactor[];
}

export interface ModelMetrics {
  best_model: string;
  all_results: Record<
    string,
    { accuracy: number; precision: number; recall: number; f1_score: number; roc_auc: number }
  >;
  n_train: number;
  n_test: number;
}

export interface DashboardMetrics {
  total_applications: number;
  approved_count: number;
  rejected_count: number;
  approval_rate: number;
  average_loan_amount: number;
  average_risk_score: number;
  risk_distribution: Record<string, number>;
  model_metrics: ModelMetrics;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string | null;
  database: string;
}

export interface ApiError {
  detail: string;
}
