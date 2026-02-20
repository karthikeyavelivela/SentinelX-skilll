/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
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
                    950: '#1e1b4b',
                },
                cyber: {
                    green: '#00ff88',
                    red: '#ff4444',
                    amber: '#ffbb33',
                    blue: '#00bbff',
                    purple: '#aa66ff',
                },
                surface: {
                    dark: '#0a0e1a',
                    card: '#111827',
                    hover: '#1f2937',
                    border: '#1e293b',
                }
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            animation: {
                'pulse-slow': 'pulse 3s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(99, 102, 241, 0.3)' },
                    '100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.6)' },
                }
            }
        },
    },
    plugins: [],
};
