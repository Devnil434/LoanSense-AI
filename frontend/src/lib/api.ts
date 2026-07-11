import type {
  DashboardMetrics,
  HealthResponse,
  LoanApplicationInput,
  PredictionResponse,
  RiskScoreResponse,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

class ApiRequestError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiRequestError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let detail = "Something went wrong. Please try again.";
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // ignore JSON parse failure, use default message
    }
    throw new ApiRequestError(detail, res.status);
  }

  return res.json() as Promise<T>;
}

export const api = {
  predict: (payload: LoanApplicationInput) =>
    request<PredictionResponse>("/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  riskScore: (payload: LoanApplicationInput) =>
    request<RiskScoreResponse>("/risk-score", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  metrics: () => request<DashboardMetrics>("/metrics", { cache: "no-store" }),

  health: () => request<HealthResponse>("/health", { cache: "no-store" }),
};

export { ApiRequestError };
