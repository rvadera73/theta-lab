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
        // Light theme (2026-10-16, trader correction -- dark rejected on
        // sight). Cool neutral gray surfaces, not stark white. up/down
        // (and the severity dots in ItemsTable/DetailViewer) reuse the
        // good/critical pair from the dataviz skill's validated status
        // palette (contrast-checked via validate_palette.js earlier this
        // session) -- not re-picked from scratch.
        surface: "#f7f8fa",
        panel: "#ffffff",
        panelAlt: "#f1f3f6",
        border: "#e2e5ea",
        ink: "#1a1d24",
        muted: "#5b6472",
        faint: "#9aa1ad",
        accent: "#e2792a",
        up: "#0ca30c",
        down: "#d03b3b",
        warn: "#fab219",
      },
    },
  },
  plugins: [],
};
