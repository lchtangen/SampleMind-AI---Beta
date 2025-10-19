/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'cyber-primary': '#00f0ff',
        'cyber-secondary': '#ff00ff',
        'cyber-accent': '#00ffcc',
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(90deg, #00f0ff 0%, #ff00ff 50%, #00ffcc 100%)',
      },
    },
  },
  plugins: [],
}