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
        ink: "#1b1b1b",
        muted: "#565c65",
        faint: "#71767a",
        border: "#dfe1e2",
        accent: "#205493",
        good: "#00a91c",
        warn: "#c05600",
        bad: "#b50909",
      },
    },
  },
  plugins: [],
};
