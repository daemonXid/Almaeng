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
                // 😈 DAEMON-ONE Protocol Colors
                // ============================================
                'daemon': {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#f87171',
                    500: '#ef4444',
                    600: '#dc2626',
                    700: '#b91c1c',
                    800: '#991b1b',
                    900: '#7f1d1d',
                    950: '#450a0a',
                },
                // Protocol: Cyclops (Red) - 공격적/경고/스캔
                'cyclops': '#ff003c',
                'cyclops-dark': '#0a0a0f',
                // Protocol: Blueprint (Cyan) - 정밀/재활/수치
                'tactical': '#06b6d4',
                // Protocol: Terminal (Green) - 시스템/개발자
                'terminal': '#22c55e',
                // Protocol: Hologram (Blue) - 현대적/대시보드
                'holo': '#3b82f6',
            },
            fontFamily: {
                sans: ['Rajdhani', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
                mono: ['Share Tech Mono', 'JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
                header: ['Orbitron', 'sans-serif'],
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
