/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-black': '#0a0a0f',
        'cyber-panel': '#13131a',
        'cyber-border': '#1e1e2d',
        'cyber-blue': '#00f0ff',
        'cyber-green': '#39ff14',
      }
    },
  },
  plugins: [],
}
