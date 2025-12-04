/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './theme/templates/theme/**/*.html',
    './**/templates/**/*.html',
    './templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: true,
  },
}
