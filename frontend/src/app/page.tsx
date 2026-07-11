import Link from "next/link";
import { ArrowRight, ShieldCheck, Gauge, Sparkles, LineChart } from "lucide-react";
import { Card } from "@/components/ui/card";

const FEATURES = [
  {
    icon: Gauge,
    title: "0–100 Credit Risk Score",
    description:
      "A transparent, rule-based score built from income, debt, savings, credit history, and employment — independent of the ML model, and fully explainable.",
  },
  {
    icon: Sparkles,
    title: "Explainable AI",
    description:
      "Every decision comes with a SHAP-powered breakdown of the top factors that pushed the outcome toward approval or rejection.",
  },
  {
    icon: ShieldCheck,
    title: "Smart Recommendations",
    description:
      "Rule-based, actionable guidance — reduce the loan amount, shorten the term, or lower your debt-to-income ratio — tailored to each applicant.",
  },
  {
    icon: LineChart,
    title: "Live Analytics Dashboard",
    description:
      "Approval trends, risk distribution, and live model performance metrics across every application processed on the platform.",
  },
];

const WORKFLOW = [
  { step: "Submit", detail: "Applicant details go through validated, typed forms in under two minutes." },
  { step: "Score", detail: "XGBoost, Random Forest, and Logistic Regression are benchmarked; the strongest model decides." },
  { step: "Explain", detail: "SHAP values translate the model's reasoning into plain-language factors." },
  { step: "Recommend", detail: "If declined or high-risk, the applicant gets concrete next steps to improve their odds." },
];

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-24 pt-20 sm:pt-28">
        <div className="mx-auto max-w-4xl text-center">
          <span className="label-eyebrow inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1">
            Underwriting, made legible
          </span>
          <h1 className="mt-6 text-4xl font-semibold leading-tight text-mist-50 sm:text-6xl">
            Loan decisions your applicants can actually <span className="text-gold-400">understand</span>.
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base text-mist-300 sm:text-lg">
            LoanSense AI predicts loan approval, calculates a transparent 0–100 credit risk score, and explains
            every decision in plain language — built with the same rigor a real fintech underwriting desk expects.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link href="/application" className="btn-primary">
              Start an application <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/dashboard" className="btn-secondary">
              View live dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="mb-10 max-w-xl">
          <span className="label-eyebrow">What&apos;s under the hood</span>
          <h2 className="mt-3 text-2xl font-semibold text-mist-50 sm:text-3xl">
            Four systems, one decision.
          </h2>
        </div>
        <div className="grid gap-5 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <Card key={f.title} className="animate-fade-up">
              <f.icon className="h-5 w-5 text-gold-400" />
              <h3 className="mt-4 text-lg font-semibold text-mist-50">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-mist-300">{f.description}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="mb-10 max-w-xl">
          <span className="label-eyebrow">The pipeline</span>
          <h2 className="mt-3 text-2xl font-semibold text-mist-50 sm:text-3xl">From form to decision.</h2>
        </div>
        <div className="grid gap-5 sm:grid-cols-4">
          {WORKFLOW.map((w, i) => (
            <div key={w.step} className="glass-card p-5">
              <span className="font-mono text-xs text-gold-400">{String(i + 1).padStart(2, "0")}</span>
              <h3 className="mt-3 font-display text-base font-semibold text-mist-50">{w.step}</h3>
              <p className="mt-2 text-xs leading-relaxed text-mist-300">{w.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-4xl px-6 pb-28">
        <div className="glass-card flex flex-col items-center gap-6 p-10 text-center sm:p-14">
          <h2 className="text-2xl font-semibold text-mist-50 sm:text-3xl">
            See your risk score in under a minute.
          </h2>
          <p className="max-w-md text-sm text-mist-300">
            No signup required to try it — submit an application and get an instant, explainable decision.
          </p>
          <Link href="/application" className="btn-primary">
            Start an application <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
