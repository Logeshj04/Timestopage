/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        industrial: {
          navy: "#1B3A4B",
          slate: "#2F4858",
          accent: "#C45C26",
          mist: "#F4F6F8",
        },
      },
    },
  },
  corePlugins: {
    preflight: false,
  },
};
