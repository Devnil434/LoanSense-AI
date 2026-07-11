import { z } from "zod";

export const loanApplicationSchema = z.object({
  applicant_name: z.string().min(2, "Enter the applicant's full name").max(120),
  age: z.coerce.number().int().min(18, "Applicant must be at least 18").max(100),
  gender: z.enum(["Male", "Female"], { required_error: "Select a gender" }),
  married: z.enum(["Yes", "No"], { required_error: "Select marital status" }),
  dependents: z.enum(["0", "1", "2", "3+"], { required_error: "Select number of dependents" }),
  education: z.enum(["Graduate", "Not Graduate"], { required_error: "Select education level" }),
  self_employed: z.enum(["Yes", "No"], { required_error: "Select employment type" }),
  applicant_income: z.coerce.number().positive("Income must be greater than 0"),
  coapplicant_income: z.coerce.number().min(0, "Cannot be negative").default(0),
  loan_amount: z.coerce.number().positive("Enter the requested loan amount (in thousands)"),
  loan_amount_term: z.coerce.number().int().positive("Enter the loan term in months"),
  credit_history: z.coerce.number().refine((v) => v === 0 || v === 1) as unknown as z.ZodType<0 | 1>,
  property_area: z.enum(["Urban", "Semiurban", "Rural"], { required_error: "Select a property area" }),
  existing_debt: z.coerce.number().min(0, "Cannot be negative").default(0),
  savings: z.coerce.number().min(0, "Cannot be negative").default(0),
});

export type LoanApplicationFormValues = z.infer<typeof loanApplicationSchema>;
