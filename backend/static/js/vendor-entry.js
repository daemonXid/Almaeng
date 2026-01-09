/**
 * 📦 Vendor Bundle Entry Point
 * 
 * Bundles htmx, Alpine.js, and PGlite from node_modules
 * into backend/static/dist/vendor.js
 * 
 * Custom JS (storage.js, local-db/) remains separate.
 */

import htmx from 'htmx.org';
import Alpine from 'alpinejs';
// import { PGlite } from '@electric-sql/pglite';
import Lenis from 'lenis';
import { animate, scroll } from 'motion';
import Splitting from 'splitting';

// Make libraries globally available
window.htmx = htmx;
window.Alpine = Alpine;
// window.PGlite = PGlite;
window.Lenis = Lenis;
window.motion = { animate, scroll };
window.Splitting = Splitting;

// HTMX configuration
htmx.config.defaultSwapStyle = 'innerHTML';
htmx.config.defaultSettleDelay = 100;

// Initialize Splitting
Splitting();

// Start Alpine when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lenis (Smooth Scroll)
    const lenis = new Lenis({
        autoRaf: true,
    });
    window.lenis = lenis;

    Alpine.start();
});

console.log('😈 DAEMON-ONE Vendor Bundle Loaded');
