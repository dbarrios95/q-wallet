/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0B1F3A", // Azul profundo
          light: "#173A6B",
          dark: "#061222",
        },
        accent: {
          DEFAULT: "#00A86B", // Verde quetzal
          light: "#00D688",
          dark: "#007A4E",
        },
        surface: {
          light: "#F8FAFC",
          cardLight: "#FFFFFF",
          dark: "#0B1424",
          cardDark: "#111C33",
        },
        state: {
          success: "#10B981",
          warning: "#F59E0B",
          error: "#EF4444",
          info: "#3B82F6",
        },
      },
      fontFamily: {
        inter: ["Inter_400Regular", "sans-serif"],
        "inter-medium": ["Inter_500Medium", "sans-serif"],
        "inter-semibold": ["Inter_600SemiBold", "sans-serif"],
        "inter-bold": ["Inter_700Bold", "sans-serif"],
      },
    },
  },
  plugins: [],
};
