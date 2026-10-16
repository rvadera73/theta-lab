/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Design tokens matching the existing dashboard's established palette
      // (composite-scores.html etc.) -- real-application colors, not a
      // generic/default Tailwind look, so the new SPA and any not-yet-
      // migrated legacy page read as the same product during the transition.
      colors: {
        // Dark-first palette, matched directly against a real reference
        // (Robinhood Legend screenshot, 2026-10-16) rather than guessed --
        // deep navy surfaces, not pure black; P&L green/red reserved
        // strictly for gain/loss, never reused for generic categories.
        surface: "#0b0e14",
        panel: "#11151d",
        panelAlt: "#161b25",
        border: "#232936",
        ink: "#e8eaed",
        muted: "#8b93a3",
        faint: "#5c6578",
        accent: "#f7941d",
        up: "#1ec47c",
        down: "#ff5a5f",
      },
    },
  },
  plugins: [],
};
