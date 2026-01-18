/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './app/**/*.{js,jsx}',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "#E5E5E5",
        input: "#E5E5E5",
        ring: "#064E3B",
        background: "#FFFFFF",
        foreground: "#1C1917",
        primary: {
          DEFAULT: "#064E3B",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#F5F5F4",
          foreground: "#1C1917",
        },
        accent: {
          DEFAULT: "#0EA5E9",
          foreground: "#FFFFFF",
        },
        destructive: {
          DEFAULT: "#EF4444",
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: "#F5F5F4",
          foreground: "#78716C",
        },
        success: "#10B981",
        warning: "#F59E0B",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1C1917",
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: "#1C1917",
        },
      },
      fontFamily: {
        chivo: ['Chivo', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        lg: "1rem",
        md: "0.75rem",
        sm: "0.5rem",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}