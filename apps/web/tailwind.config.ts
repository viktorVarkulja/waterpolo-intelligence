import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"] ,
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        slate: "#1f2937",
        surf: "#f8fafc",
        wave: "#0ea5a3",
        coral: "#f97316"
      }
    }
  },
  plugins: []
};

export default config;
