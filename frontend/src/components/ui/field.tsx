import { forwardRef } from "react";
import type { InputHTMLAttributes, SelectHTMLAttributes } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, id, ...props }, ref) => {
    const fieldId = id ?? props.name;
    return (
      <div>
        <label htmlFor={fieldId} className="field-label">
          {label}
        </label>
        <input id={fieldId} ref={ref} className="field-input" {...props} />
        {error && <p className="field-error">{error}</p>}
      </div>
    );
  }
);
TextField.displayName = "TextField";

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  error?: string;
  options: { label: string; value: string }[];
}

export const SelectField = forwardRef<HTMLSelectElement, SelectFieldProps>(
  ({ label, error, options, id, ...props }, ref) => {
    const fieldId = id ?? props.name;
    return (
      <div>
        <label htmlFor={fieldId} className="field-label">
          {label}
        </label>
        <select id={fieldId} ref={ref} className="field-input" {...props}>
          <option value="" disabled>
            Select…
          </option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {error && <p className="field-error">{error}</p>}
      </div>
    );
  }
);
SelectField.displayName = "SelectField";
