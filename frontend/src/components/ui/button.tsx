import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    const base =
      variant === "primary" ? "btn-primary" : variant === "secondary" ? "btn-secondary" : "inline-flex items-center gap-2 text-sm text-mist-300 hover:text-mist-50 transition";
    return <button ref={ref} className={cn(base, className)} {...props} />;
  }
);
Button.displayName = "Button";
