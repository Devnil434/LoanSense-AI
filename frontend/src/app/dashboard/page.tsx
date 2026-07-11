"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, ApiRequestError } from "@/lib/api";
import type { DashboardMetrics } from "@/types";
import { formatCurrency } from "@/lib/utils";

const RISK_COLORS: Record<string, string> = {
  Excellent: "#3DDC97",
  "Low Risk": "#7FE0B4",
  "Moderate Risk": "#F2C14E",
  "High Risk": "#F2914E",
  "Very High Risk": "#F0616D",
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .metrics()
      .then(setMetrics)
      .catch((err) => setError(err instanceof ApiRequestError ? err.message : "Could not load dashboard metrics."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl space-y-6 px-6 py-16">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-5 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-24 text-center">
        <h1 className="text-2xl font-semibold text-mist-50">Dashboard unavailable</h1>
        <p className="mt-3 text-sm text-mist-300">
          {error ?? "No metrics found yet."} Make sure the backend is running and reachable.
        </p>
      </div>
    );
  }

  const approvalData = [
    { name: "Approved", value: metrics.approved_count, color: "#3DDC97" },
    { name: "Rejected", value: metrics.rejected_count, color: "#F0616D" },
  ];

  const riskData = Object.entries(metrics.risk_distribution).map(([name, value]) => ({
    name,
    value,
    color: RISK_COLORS[name] ?? "#F2C14E",
  }));

  const modelData = Object.entries(metrics.model_metrics.all_results).map(([name, m]) => ({
    name: name.replace(/_/g, " "),
    accuracy: m.accuracy,
    roc_auc: m.roc_auc,
    f1: m.f1_score,
  }));

  return (
    <div className="mx-auto max-w-6xl px-6 py-16">
      <div className="mb-10">
        <span className="label-eyebrow">Live analytics</span>
        <h1 className="mt-3 text-3xl font-semibold text-mist-50">Portfolio dashboard</h1>
        <p className="mt-2 text-sm text-mist-300">
          Aggregated across every loan application processed by LoanSense AI.
        </p>
      </div>

      <div className="mb-8 grid gap-5 sm:grid-cols-4">
        <StatCard label="Total applications" value={metrics.total_applications.toString()} />
        <StatCard label="Approval rate" value={`${metrics.approval_rate}%`} />
        <StatCard label="Avg. loan amount" value={formatCurrency(metrics.average_loan_amount * 1000)} />
        <StatCard label="Avg. risk score" value={metrics.average_risk_score.toString()} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-mist-300">
            Approvals vs rejections
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={approvalData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
                {approvalData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#111726", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-mist-300">Risk distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={riskData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
                {riskData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#111726", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="lg:col-span-2">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-mist-300">
            Model performance comparison
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={modelData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" stroke="#7C879F" fontSize={12} />
              <YAxis stroke="#7C879F" fontSize={12} domain={[0, 1]} />
              <Tooltip contentStyle={{ background: "#111726", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8 }} />
              <Legend />
              <Bar dataKey="accuracy" fill="#E8AC2E" radius={[4, 4, 0, 0]} />
              <Bar dataKey="roc_auc" fill="#3DDC97" radius={[4, 4, 0, 0]} />
              <Bar dataKey="f1" fill="#7C879F" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="mt-3 text-xs text-mist-500">
            Best model in production: <span className="font-mono text-gold-400">{metrics.model_metrics.best_model.replace(/_/g, " ")}</span>{" "}
            — trained on {metrics.model_metrics.n_train} samples, evaluated on {metrics.model_metrics.n_test} held-out samples.
          </p>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="py-5">
      <span className="label-eyebrow">{label}</span>
      <p className="mt-2 font-mono text-2xl text-mist-50">{value}</p>
    </Card>
  );
}
