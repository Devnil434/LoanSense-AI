"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { TextField, SelectField } from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { api, ApiRequestError } from "@/lib/api";
import { loanApplicationSchema, type LoanApplicationFormValues } from "@/lib/validation";

export default function ApplicationPage() {
  const router = useRouter();
  const { push } = useToast();
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoanApplicationFormValues>({
    resolver: zodResolver(loanApplicationSchema),
    defaultValues: {
      coapplicant_income: 0,
      existing_debt: 0,
      savings: 0,
      credit_history: 1 as unknown as 0 | 1,
    },
  });

  const onSubmit = async (values: LoanApplicationFormValues) => {
    setSubmitting(true);
    try {
      const result = await api.predict({
        ...values,
        credit_history: Number(values.credit_history) as 0 | 1,
      });
      sessionStorage.setItem("loansense:lastPrediction", JSON.stringify(result));
      push("Application processed successfully.", "success");
      router.push("/predict");
    } catch (err) {
      const message = err instanceof ApiRequestError ? err.message : "Could not reach the prediction service.";
      push(message, "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <div className="mb-10">
        <span className="label-eyebrow">New Application</span>
        <h1 className="mt-3 text-3xl font-semibold text-mist-50">Tell us about the applicant.</h1>
        <p className="mt-2 text-sm text-mist-300">
          All fields feed directly into both the approval model and the risk score engine.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <Card>
          <h2 className="mb-5 text-sm font-semibold uppercase tracking-wide text-mist-300">Applicant details</h2>
          <div className="grid gap-5 sm:grid-cols-2">
            <TextField
              label="Applicant name"
              placeholder="Jane Doe"
              {...register("applicant_name")}
              error={errors.applicant_name?.message}
            />
            <TextField
              label="Age"
              type="number"
              placeholder="30"
              {...register("age")}
              error={errors.age?.message}
            />
            <SelectField
              label="Gender"
              options={[{ label: "Male", value: "Male" }, { label: "Female", value: "Female" }]}
              {...register("gender")}
              error={errors.gender?.message}
            />
            <SelectField
              label="Marital status"
              options={[{ label: "Married", value: "Yes" }, { label: "Not married", value: "No" }]}
              {...register("married")}
              error={errors.married?.message}
            />
            <SelectField
              label="Dependents"
              options={["0", "1", "2", "3+"].map((v) => ({ label: v, value: v }))}
              {...register("dependents")}
              error={errors.dependents?.message}
            />
            <SelectField
              label="Education"
              options={[
                { label: "Graduate", value: "Graduate" },
                { label: "Not graduate", value: "Not Graduate" },
              ]}
              {...register("education")}
              error={errors.education?.message}
            />
            <SelectField
              label="Employment"
              options={[
                { label: "Self-employed", value: "Yes" },
                { label: "Salaried", value: "No" },
              ]}
              {...register("self_employed")}
              error={errors.self_employed?.message}
            />
            <SelectField
              label="Property area"
              options={[
                { label: "Urban", value: "Urban" },
                { label: "Semiurban", value: "Semiurban" },
                { label: "Rural", value: "Rural" },
              ]}
              {...register("property_area")}
              error={errors.property_area?.message}
            />
          </div>
        </Card>

        <Card>
          <h2 className="mb-5 text-sm font-semibold uppercase tracking-wide text-mist-300">
            Income &amp; loan details
          </h2>
          <div className="grid gap-5 sm:grid-cols-2">
            <TextField
              label="Annual income (₹)"
              type="number"
              placeholder="65000"
              {...register("applicant_income")}
              error={errors.applicant_income?.message}
            />
            <TextField
              label="Co-applicant income (₹)"
              type="number"
              placeholder="0"
              {...register("coapplicant_income")}
              error={errors.coapplicant_income?.message}
            />
            <TextField
              label="Loan amount (in thousands ₹)"
              type="number"
              placeholder="150"
              {...register("loan_amount")}
              error={errors.loan_amount?.message}
            />
            <TextField
              label="Loan term (months)"
              type="number"
              placeholder="360"
              {...register("loan_amount_term")}
              error={errors.loan_amount_term?.message}
            />
            <SelectField
              label="Credit history"
              options={[
                { label: "Good repayment history", value: "1" },
                { label: "No / poor credit history", value: "0" },
              ]}
              {...register("credit_history")}
              error={errors.credit_history?.message as string | undefined}
            />
            <TextField
              label="Existing debt (₹)"
              type="number"
              placeholder="5000"
              {...register("existing_debt")}
              error={errors.existing_debt?.message}
            />
            <TextField
              label="Savings balance (₹)"
              type="number"
              placeholder="20000"
              {...register("savings")}
              error={errors.savings?.message}
            />
          </div>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" disabled={submitting}>
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Processing…
              </>
            ) : (
              <>
                Get my decision <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
