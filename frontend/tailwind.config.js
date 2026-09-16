/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#090D16",
          card: "#111827",
          border: "#1F2937",
          muted: "#374151",
          highlight: "#1E293B",
          accent: "#3B82F6",
          danger: "#EF4444",
          warning: "#F59E0B",
          success: "#10B981",
          cyan: "#06B6D4"
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
