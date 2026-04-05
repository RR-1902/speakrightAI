/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        shell: "#090412",
        ink: "#f7f1ff",
        violetGlow: "#b26bff",
        electric: "#8d6bff",
        orchid: "#d474ff",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ['"Plus Jakarta Sans"', "sans-serif"],
      },
      boxShadow: {
        glass: "0 24px 80px rgba(17, 8, 36, 0.45)",
        glow: "0 0 0 1px rgba(255,255,255,0.12), 0 16px 40px rgba(165, 90, 255, 0.28)",
        button: "0 14px 30px rgba(156, 96, 255, 0.45)",
      },
      backgroundImage: {
        aurora:
          "radial-gradient(circle at top left, rgba(199,130,255,0.32), transparent 32%), radial-gradient(circle at 85% 15%, rgba(116,105,255,0.28), transparent 26%), linear-gradient(135deg, #13051f 0%, #311257 48%, #6126a6 100%)",
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        pulseSoft: "pulseSoft 3.4s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.75", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.03)" },
        },
      },
    },
  },
  plugins: [],
};
