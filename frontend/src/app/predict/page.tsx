"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, XCircle, TrendingUp, TrendingDown, Lightbulb, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { RiskGauge } from "@/components/ui/risk-gauge";
import { Skeleton } from "@/components/ui/skeleton";
import type { PredictionResponse } from "@/types";
import { formatPercent } from "@/lib/utils";

export default function PredictResultPage() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("loansense:lastPrediction");
    if (raw) {
      try {
        setResult(JSON.parse(raw));
      } catch {
        setResult(null);
      }
    }
    setLoaded(true);
  }, []);

  if (!loaded) {
    return (
      <div className="mx-auto max-w-4xl space-y-6 px-6 py-16">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-24 text-center">
        <h1 className="text-2xl font-semibold text-mist-50">No result to show yet.</h1>
        <p className="mt-3 text-sm text-mist-300">
          Submit a loan application to see the decision, risk score, and explanation here.
        </p>
        <Link href="/application" className="btn-primary mt-8 inline-flex">
          Start an application <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  const approved = result.decision === "Approved";

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <div className="mb-10 flex flex-col items-center text-center">
        <div
          className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold ${
            approved ? "bg-signal-approve/15 text-signal-approve" : "bg-signal-reject/15 text-signal-reject"
          }`}
        >
          {approved ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
          {result.decision}
        </div>
        <h1 className="mt-4 text-3xl font-semibold text-mist-50">
          {approved ? "This application is approved." : "This application was not approved."}
        </h1>
        <p className="mt-3 max-w-xl text-sm text-mist-300">{result.explanation_summary}</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="flex flex-col items-center justify-center py-10">
          <span className="label-eyebrow mb-4">Credit Risk Score</span>
          <RiskGauge score={result.risk_score} category={result.risk_category} />
        </Card>

        <Card className="flex flex-col justify-center gap-4">
          <div>
            <span className="label-eyebrow">Confidence</span>
            <p className="mt-1 font-mono text-2xl text-mist-50">{formatPercent(result.confidence)}</p>
          </div>
          <div>
            <span className="label-eyebrow">Approval probability</span>
            <p className="mt-1 font-mono text-2xl text-mist-50">{formatPercent(result.approval_probability)}</p>
          </div>
          <div>
            <span className="label-eyebrow">Model used</span>
            <p className="mt-1 font-mono text-sm text-mist-300">{result.model_used.replace(/_/g, " ")}</p>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-signal-approve" />
            <h3 className="text-sm font-semibold uppercase tracking-wide text-mist-300">Positive factors</h3>
          </div>
          <ul className="space-y-3">
            {result.top_positive_factors.map((f) => (
              <li key={f.feature} className="flex items-center justify-between text-sm">
                <span className="text-mist-300">{f.human_readable}</span>
                <span className="font-mono text-signal-approve">+{f.impact.toFixed(2)}</span>
              </li>
            ))}
            {result.top_positive_factors.length === 0 && (
              <li className="text-sm text-mist-500">No significant positive factors.</li>
            )}
          </ul>
        </Card>

        <Card>
          <div className="mb-4 flex items-center gap-2">
            <TrendingDown className="h-4 w-4 text-signal-reject" />
            <h3 className="text-sm font-semibold uppercase tracking-wide text-mist-300">Negative factors</h3>
          </div>
          <ul className="space-y-3">
            {result.top_negative_factors.map((f) => (
              <li key={f.feature} className="flex items-center justify-between text-sm">
                <span className="text-mist-300">{f.human_readable}</span>
                <span className="font-mono text-signal-reject">{f.impact.toFixed(2)}</span>
              </li>
            ))}
            {result.top_negative_factors.length === 0 && (
              <li className="text-sm text-mist-500">No significant negative factors.</li>
            )}
          </ul>
        </Card>
      </div>

      <Card className="mt-6">
        <div className="mb-4 flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-gold-400" />
          <h3 className="text-sm font-semibold uppercase tracking-wide text-mist-300">Smart recommendations</h3>
        </div>
        <ul className="space-y-2">
          {result.recommendations.map((r, i) => (
            <li key={i} className="flex gap-3 text-sm text-mist-300">
              <span className="font-mono text-gold-400">{String(i + 1).padStart(2, "0")}</span>
              {r}
            </li>
          ))}
        </ul>
      </Card>

      <Card className="mt-6">
        <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-mist-300">Risk score breakdown</h3>
        <div className="space-y-3">
          {result.risk_factors.map((f) => (
            <div key={f.name} className="flex items-center justify-between border-b border-white/[0.04] pb-3 last:border-0 last:pb-0">
              <div>
                <p className="text-sm text-mist-50">{f.name}</p>
                <p className="text-xs text-mist-500">{f.reason}</p>
              </div>
              <span className="font-mono text-sm text-gold-400">+{f.points}</span>
            </div>
          ))}
        </div>
      </Card>

      <div className="mt-10 flex justify-center gap-4">
        <Link href="/application" className="btn-secondary">
          Run another application
        </Link>
        <Link href="/dashboard" className="btn-primary">
          View dashboard <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
