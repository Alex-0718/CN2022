/** @type {import('tailwindcss').Config} */
module.exports = {
    prefix: 'tw-',
    content: ['./public/**/*.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
    important: true,
    theme: {
        extend: {
            colors: {
                primary: "#1976d2",
            }
        },
    },
    plugins: [],
}