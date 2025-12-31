/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'notion-bg': '#ffffff',
        'notion-sidebar': '#f7f6f3',
        'notion-hover': '#efefef',
        'notion-text': '#37352f',
        'notion-gray': '#9b9a97',
        'notion-border': '#e3e2de',
      }
    },
  },
  plugins: [],
}
