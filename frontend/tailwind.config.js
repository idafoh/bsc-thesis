/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        emotion: {
          happiness: '#FFD700',
          sadness: '#4169E1',
          anger: '#DC143C',
          fear: '#8B008B',
          disgust: '#228B22',
          surprise: '#FF8C00',
          neutral: '#808080',
        },
      },
    },
  },
  plugins: [],
}
