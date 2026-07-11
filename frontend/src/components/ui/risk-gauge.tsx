"use client";

import { useMemo } from "react";

interface RiskGaugeProps {
  score: number; // 0-100
  category: string;
  size?: number;
}

const CATEGORY_COLOR: Record<string, string> = {
  Excellent: "#3DDC97",
  "Low Risk": "#7FE0B4",
  "Moderate Risk": "#F2C14E",
  "High Risk": "#F2914E",
  "Very High Risk": "#F0616D",
};

export function RiskGauge({ score, category, size = 220 }: RiskGaugeProps) {
  const stroke = 14;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.min(100, Math.max(0, score));
  const offset = useMemo(() => circumference * (1 - clamped / 100), [circumference, clamped]);
  const color = CATEGORY_COLOR[category] ?? "#F2C14E";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          style={{
            // @ts-expect-error -- custom CSS vars used by the dash-in keyframe
            "--dash-start": circumference,
            "--dash-end": offset,
          }}
          className="animate-dash-in"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-4xl font-semibold text-mist-50">{Math.round(clamped)}</span>
        <span className="label-eyebrow mt-1">of 100</span>
        <span className="mt-2 rounded-full px-3 py-1 text-xs font-semibold" style={{ backgroundColor: `${color}22`, color }}>
          {category}
        </span>
      </div>
    </div>
  );
}
