/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./backend/**/*.html",
        "./backend/**/*.py",
        "./backend/domains/**/static/js/**/*.js",
        "./backend/static/js/**/*.js",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // ============================================
                // 🔵 Toss Design System Colors
                // ============================================
                'brand': {
                    50: '#EFF6FF',
                    100: '#DBEAFE',
                    200: '#BFDBFE',
                    300: '#93C5FD',
                    400: '#60A5FA',
                    500: '#3182F6',  // Toss Primary Blue
                    600: '#0066FF',  // Toss Secondary Blue
                    700: '#1D4ED8',
                    800: '#1E40AF',
                    900: '#1E3A8A',
                    950: '#172554',
                },
                'toss': {
                    blue: '#3182F6',
                    'blue-dark': '#0066FF',
                    gray: '#8B95A1',
                    'gray-light': '#F4F4F4',
                    black: '#191F28',
                    white: '#FFFFFF',
                },
                // Accent colors
                'accent-green': '#00C471',
                'accent-red': '#F04452',
                'accent-yellow': '#FFD54F',
            },
            fontFamily: {
                sans: ['Pretendard', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
            },
            animation: {
                // Base animations
                'float': 'float 3s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                // DAEMON Protocol animations
                'scan-line': 'scan 3s linear infinite',
                'scan-vertical': 'scan-v 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite',
                'glitch': 'glitch 1s linear infinite',
                'flicker': 'flicker 0.15s infinite',
                'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(239, 68, 68, 0.5)' },
                    '100%': { boxShadow: '0 0 20px rgba(239, 68, 68, 0.8)' },
                },
                // Horizontal scan (Terminal style)
                scan: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                },
                // Vertical scan (Cyclops laser)
                'scan-v': {
                    '0%': { top: '0%', opacity: '0' },
                    '10%': { opacity: '1' },
                    '90%': { opacity: '1' },
                    '100%': { top: '100%', opacity: '0' },
                },
                glitch: {
                    '2%, 64%': { transform: 'translate(2px,0) skew(0deg)' },
                    '4%, 60%': { transform: 'translate(-2px,0) skew(0deg)' },
                    '62%': { transform: 'translate(0,0) skew(5deg)' },
                },
                flicker: {
                    '0%': { opacity: '0.9' },
                    '50%': { opacity: '1' },
                    '100%': { opacity: '0.8' },
                },
            },
            backdropBlur: {
                xs: '2px',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'grid-pattern': 'linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px)',
            },
            backgroundSize: {
                'grid-20': '20px 20px',
                'grid-40': '40px 40px',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
    ],
}
