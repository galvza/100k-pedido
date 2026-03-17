import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // UI colors
        primary: "#1A1A2E",
        secondary: "#E5E7EB",
        accent: "#2563EB",
        muted: "#6B7280",
        border: "#D1D5DB",
        surface: "#F9F9F7",
        // Chart series colors (flat, editorial, accessible)
        chart: {
          1: "#2563EB", // azul
          2: "#059669", // verde
          3: "#D97706", // âmbar
          4: "#DC2626", // vermelho
          5: "#7C3AED", // violeta
          6: "#0891B2", // ciano
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
      },
      fontSize: {
        "lead": ["1.125rem", { lineHeight: "1.75rem" }],
      },
      maxWidth: {
        prose: "72ch",
        content: "1200px",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
    },
  },
  plugins: [],
};

export default config;
