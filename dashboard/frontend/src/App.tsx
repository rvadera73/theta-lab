import { HashRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import TodayPage from "./pages/Today";
import USPage from "./pages/US";
import IndiaPage from "./pages/India";
import WatchlistPage from "./pages/Watchlist";

// HashRouter deliberately -- see git history for why (gateway path-prefix
// robustness, confirmed real bug class already hit once).
//
// Real fix (2026-10-16, trader decision): Watchlist and Scores merged into
// one tab -- Scores was just the ranked view of the same symbols Watchlist
// manages, so two tabs for one dataset meant extra clicks for no reason.
// /composite-scores still redirects below for any old link/bookmark.
const TABS = [
  { to: "/today", label: "Today" },
  { to: "/us", label: "US" },
  { to: "/india", label: "India" },
  { to: "/watchlist", label: "Watchlist" },
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
            <Route path="/us" element={<USPage />} />
            <Route path="/india" element={<IndiaPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/composite-scores" element={<Navigate to="/watchlist" replace />} />
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
