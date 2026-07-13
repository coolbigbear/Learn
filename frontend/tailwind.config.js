/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            h2: {
              marginTop: '2.25em',
              marginBottom: '0.8em',
            },
            h3: {
              marginTop: '1.5em',
              marginBottom: '0.6em',
            },
            h4: {
              marginTop: '1.25em',
              marginBottom: '0.5em',
            },
            p: {
              marginTop: 0,
              marginBottom: '1.75em',
              lineHeight: '1.75',
            },
            'p + ul, p + ol': {
              marginTop: '0.25em',
            },
            hr: {
              marginTop: '2.5em',
              marginBottom: '2.5em',
            },
            'li > p': {
              marginBottom: '0.5em',
            },
          },
        },
        sm: {
          css: {
            h2: {
              marginTop: '1.75em',
              marginBottom: '0.8em',
            },
            h3: {
              marginTop: '1.25em',
              marginBottom: '0.5em',
            },
            h4: {
              marginTop: '1em',
              marginBottom: '0.4em',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
