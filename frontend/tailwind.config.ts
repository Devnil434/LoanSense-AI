import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#070A12",
          900: "#0B0F1A",
          800: "#111726",
          700: "#182036",
          600: "#212B47",
        },
        mist: {
          50: "#F7F8FC",
          100: "#EDEFF6",
          300: "#B9C0D4",
          500: "#7C879F",
        },
        gold: {
          400: "#F2C14E",
          500: "#E8AC2E",
          600: "#C98F1B",
        },
        signal: {
          approve: "#3DDC97",
          reject: "#F0616D",
          warn: "#F2C14E",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 20% 20%, rgba(232,172,46,0.08), transparent 40%), radial-gradient(circle at 80% 0%, rgba(61,220,151,0.06), transparent 35%)",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0,0,0,0.35)",
        "glass-inset": "inset 0 1px 0 0 rgba(255,255,255,0.06)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "dash-in": {
          "0%": { strokeDashoffset: "var(--dash-start)" },
          "100%": { strokeDashoffset: "var(--dash-end)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out forwards",
        "dash-in": "dash-in 1.1s cubic-bezier(0.22, 1, 0.36, 1) forwards",
      },
    },
  },
  plugins: [],
};

export default config;
