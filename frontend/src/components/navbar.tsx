import Link from "next/link";
import { Landmark } from "lucide-react";

const LINKS = [
  { href: "/application", label: "Apply" },
  { href: "/dashboard", label: "Dashboard" },
];

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-ink-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2 font-display text-lg font-semibold text-mist-50">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gold-500/15 text-gold-400">
            <Landmark className="h-4 w-4" />
          </span>
          LoanSense <span className="text-gold-400">AI</span>
        </Link>
        <nav className="flex items-center gap-6">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-mist-300 transition hover:text-mist-50"
            >
              {link.label}
            </Link>
          ))}
          <Link href="/application" className="btn-primary !px-5 !py-2 text-xs">
            New Application
          </Link>
        </nav>
      </div>
    </header>
  );
}
