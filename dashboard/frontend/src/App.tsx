import { HashRouter, Routes, Route, NavLink } from "react-router-dom";
import TodayPage from "./pages/Today";
import PlaceholderPage from "./pages/Placeholder";

// HashRouter deliberately -- see git history for why (gateway path-prefix
// robustness, confirmed real bug class already hit once).
const TABS = [
  { to: "/today", label: "Today" },
  { to: "/us", label: "US" },
  { to: "/india", label: "India" },
  { to: "/watchlist", label: "Watchlist" },
  { to: "/composite-scores", label: "Scores" },
];

function NavTab({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex-1 md:flex-none text-center md:text-left px-3 py-2 md:py-1.5 rounded text-[13px] font-medium transition-colors ${
          isActive ? "bg-panelAlt text-ink" : "text-muted hover:text-ink"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

export default function App() {
  return (
    <HashRouter>
      <div className="min-h-screen bg-surface flex flex-col">
        {/* Desktop top bar -- matches a real reference (Robinhood Legend,
            2026-10-16): dark chrome, a market-status dot, icon-weight
            right-side controls, not plain text links alone. */}
        <header className="hidden md:flex items-center justify-between bg-panel border-b border-border px-5 py-2.5">
          <div className="flex items-center gap-6">
            <span className="w-2 h-2 rounded-sm bg-accent" />
            <strong className="text-ink text-[13px] tracking-wide">theta-lab</strong>
            <nav className="flex gap-1">
              {TABS.map((t) => (
                <NavTab key={t.to} {...t} />
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-4 text-[12px] text-muted">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-up" />
              Market hours
            </span>
            <span className="text-faint">Account A</span>
          </div>
        </header>

        {/* Mobile top bar */}
        <header className="md:hidden bg-panel border-b border-border px-4 py-3 text-center">
          <strong className="text-ink text-[13px]">theta-lab</strong>
        </header>

        <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 md:px-6 py-5 pb-20 md:pb-5">
          <Routes>
            <Route path="/" element={<TodayPage />} />
            <Route path="/today" element={<TodayPage />} />
            <Route path="/us" element={<PlaceholderPage name="US Markets" />} />
            <Route path="/india" element={<PlaceholderPage name="India Markets" />} />
            <Route path="/watchlist" element={<PlaceholderPage name="Watchlist" />} />
            <Route path="/composite-scores" element={<PlaceholderPage name="Composite Scores" />} />
          </Routes>
        </main>

        {/* Mobile bottom tab bar */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-panel border-t border-border flex">
          {TABS.map((t) => (
            <NavTab key={t.to} {...t} />
          ))}
        </nav>
      </div>
    </HashRouter>
  );
}
