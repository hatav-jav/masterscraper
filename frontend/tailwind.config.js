/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        primary: {
          DEFAULT: '#0066FF',
          hover: '#0052CC',
          light: '#60A5FA',
        },
        accent: '#00D4AA',
        surface: {
          DEFAULT: '#161B22',
          elevated: '#1C2128',
        },
        border: '#30363D',
        dark: {
          bg: '#0D1117',
          text: '#F0F6FC',
          muted: '#8B949E',
          dim: '#6E7681',
        }
      },
    },
  },
  plugins: [],
}
