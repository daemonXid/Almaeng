/**
 * 🗄️ LocalStore - Lightweight Storage Wrapper
 * 
 * Primary storage for HATEOAS architecture.
 * Used for: theme settings, UI state, JWT tokens, simple caching.
 * 
 * Zen: Simple wrapper with JSON parsing error prevention.
 * 
 * @example
 * import { LocalStore, SessionStore } from '/static/js/core/storage.js';
 * 
 * LocalStore.set('theme', 'dark');
 * const theme = LocalStore.get('theme', 'light');
 */

// ============================================
// 📦 LocalStorage (Persistent)
// ============================================

export const LocalStore = {
    /**
     * Get item from localStorage with JSON parsing
     * @param {string} key 
     * @param {*} defaultValue 
     * @returns {*}
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    /**
     * Set item to localStorage with JSON stringify
     * @param {string} key 
     * @param {*} value 
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('[LocalStore] Failed to save:', e);
        }
    },

    /**
     * Remove item from localStorage
     * @param {string} key 
     */
    remove(key) {
        localStorage.removeItem(key);
    },

    /**
     * Clear all localStorage
     */
    clear() {
        localStorage.clear();
    },

    /**
     * Check if key exists
     * @param {string} key 
     * @returns {boolean}
     */
    has(key) {
        return localStorage.getItem(key) !== null;
    }
};

// ============================================
// 📋 SessionStorage (Tab-scoped)
// ============================================

export const SessionStore = {
    get(key, defaultValue = null) {
        try {
            const item = sessionStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    set(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('[SessionStore] Failed to save:', e);
        }
    },

    remove(key) {
        sessionStorage.removeItem(key);
    },

    clear() {
        sessionStorage.clear();
    }
};

// ============================================
// 🧠 MemoryStore (In-memory, fastest)
// ============================================

const memoryCache = new Map();

export const MemoryStore = {
    get(key, defaultValue = null) {
        return memoryCache.has(key) ? memoryCache.get(key) : defaultValue;
    },

    set(key, value) {
        memoryCache.set(key, value);
    },

    remove(key) {
        memoryCache.delete(key);
    },

    clear() {
        memoryCache.clear();
    },

    has(key) {
        return memoryCache.has(key);
    }
};

// ============================================
// 🎨 Theme Manager (Dark/Light mode)
// ============================================

export const ThemeStore = {
    STORAGE_KEY: 'daemon-one-theme',

    get() {
        return LocalStore.get(this.STORAGE_KEY, 'dark');
    },

    set(theme) {
        LocalStore.set(this.STORAGE_KEY, theme);
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.classList.toggle('dark', theme === 'dark');
    },

    toggle() {
        const current = this.get();
        this.set(current === 'dark' ? 'light' : 'dark');
        return this.get();
    },

    init() {
        const saved = this.get();
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.set(saved || (prefersDark ? 'dark' : 'light'));
    }
};

// ============================================
// 🔐 Auth Token Store (Memory-first for security)
// ============================================

export const AuthStore = {
    TOKEN_KEY: 'daemon-one-auth-token',

    // Store in memory first (more secure), fallback to localStorage
    _token: null,

    getToken() {
        return this._token || LocalStore.get(this.TOKEN_KEY);
    },

    setToken(token, persist = false) {
        this._token = token;
        if (persist) {
            LocalStore.set(this.TOKEN_KEY, token);
        }
    },

    clearToken() {
        this._token = null;
        LocalStore.remove(this.TOKEN_KEY);
    },

    hasToken() {
        return !!this.getToken();
    }
};
