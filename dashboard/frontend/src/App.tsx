import { HashRouter, Routes, Route, NavLink } from "react-router-dom";
import TodayPage from "./pages/Today";
import PlaceholderPage from "./pages/Placeholder";

// HashRouter deliberately, not BrowserRouter: this app can be served behind
// an unknown path prefix (the existing dashboard is reachable through a
// shared gateway at a prefix like /theta-lab/ -- see today.html's own
// 2026-10-15 bug history, where an absolute vs. relative path mismatch
// broke it under exactly this kind of prefix). Hash-based routes
// (#/today) never depend on the server-side path at all, so this class of
// bug can't recur here regardless of what sits in front of the app.
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
        `flex-1 md:flex-none text-center md:text-left px-3 py-2 md:py-1.5 rounded-md text-sm font-medium transition-colors ${
          isActive ? "bg-accent text-white" : "text-ink hover:bg-gray-100"
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
      <div className="min-h-screen bg-[#f9f9f7] flex flex-col">
        {/* Desktop top bar */}
        <header className="hidden md:flex items-center justify-between bg-[#2e2e38] text-white px-6 py-3">
          <strong>theta-lab</strong>
          <nav className="flex gap-2">
            {TABS.map((t) => (
              <NavTab key={t.to} {...t} />
            ))}
          </nav>
        </header>

        {/* Mobile top bar (title only -- nav lives in the bottom bar) */}
        <header className="md:hidden bg-[#2e2e38] text-white px-4 py-3 text-center font-semibold">
          theta-lab
        </header>

        <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 md:px-8 py-6 pb-20 md:pb-6">
          <Routes>
            <Route path="/" element={<TodayPage />} />
            <Route path="/today" element={<TodayPage />} />
            <Route path="/us" element={<PlaceholderPage name="US Markets" />} />
            <Route path="/india" element={<PlaceholderPage name="India Markets" />} />
            <Route path="/watchlist" element={<PlaceholderPage name="Watchlist" />} />
            <Route path="/composite-scores" element={<PlaceholderPage name="Composite Scores" />} />
          </Routes>
        </main>

        {/* Mobile bottom tab bar -- matches real trading-app conventions
            (Robinhood/Schwab mobile) rather than a top nav that eats
            vertical space on a small screen. */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-border flex">
          {TABS.map((t) => (
            <NavTab key={t.to} {...t} />
          ))}
        </nav>
      </div>
    </HashRouter>
  );
}
