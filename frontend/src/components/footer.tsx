export function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-xs text-mist-500 sm:flex-row">
        <p>© {new Date().getFullYear()} LoanSense AI — a portfolio FinTech MVP. Not a real lender.</p>
        <p className="font-mono">v1.0.0</p>
      </div>
    </footer>
  );
}
