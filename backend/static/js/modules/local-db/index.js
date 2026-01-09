/**
 * 🔋 PGlite Module - Local-First SQL Database
 * 
 * ⚠️ LAZY LOADING ONLY - Do not import at top level!
 * 
 * This module is loaded ONLY when heavy features are needed:
 * - Diagram Editor
 * - Offline Mode
 * - Complex Data Filtering
 * 
 * @example
 * // ❌ WRONG: Top-level import (bloats main bundle)
 * import { getDB } from './modules/local-db';
 * 
 * // ✅ CORRECT: Dynamic import when needed
 * async function initEditor() {
 *   const { getDB } = await import('./modules/local-db/index.js');
 *   const db = await getDB();
 *   // Use db...
 * }
 */

let dbInstance = null;
let isInitializing = false;

/**
 * Get or create PGlite database instance (Singleton)
 * @returns {Promise<import('@electric-sql/pglite').PGlite>}
 */
export async function getDB() {
    // Return existing instance
    if (dbInstance) return dbInstance;

    // Prevent concurrent initialization
    if (isInitializing) {
        // Wait for initialization to complete
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                if (dbInstance) {
                    clearInterval(checkInterval);
                    resolve(dbInstance);
                }
            }, 50);
        });
    }

    isInitializing = true;
    console.log('🔋 Initializing PGlite Engine...');

    try {
        // Use global PGlite from vendor bundle
        if (!window.PGlite) {
            throw new Error('PGlite not loaded. Ensure vendor.js is included.');
        }

        dbInstance = new window.PGlite('idb://daemon-one-db');

        // Run initial schema
        await initSchema(dbInstance);

        console.log('✅ PGlite ready!');
        return dbInstance;
    } catch (error) {
        console.error('❌ PGlite initialization failed:', error);
        throw error;
    } finally {
        isInitializing = false;
    }
}

/**
 * Initialize database schema
 * @param {import('@electric-sql/pglite').PGlite} db 
 */
async function initSchema(db) {
    await db.query(`
    -- Drafts table for auto-save
    CREATE TABLE IF NOT EXISTS drafts (
      id TEXT PRIMARY KEY,
      module TEXT NOT NULL,
      data JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Sync queue for offline-first
    CREATE TABLE IF NOT EXISTS sync_queue (
      id SERIAL PRIMARY KEY,
      action TEXT NOT NULL,
      payload JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT NOW(),
      synced BOOLEAN DEFAULT FALSE
    );
  `);
}

/**
 * Close and cleanup database
 */
export async function closeDB() {
    if (dbInstance) {
        await dbInstance.close();
        dbInstance = null;
        console.log('🔌 PGlite closed.');
    }
}

/**
 * Check if database is initialized
 * @returns {boolean}
 */
export function isDBReady() {
    return dbInstance !== null;
}

// ============================================
// 📝 Draft Operations (Auto-save)
// ============================================

/**
 * Save draft to local DB
 * @param {string} id - Unique draft ID
 * @param {string} module - Module name (e.g., 'diagram-editor')
 * @param {object} data - Draft data
 */
export async function saveDraft(id, module, data) {
    const db = await getDB();
    await db.query(
        `INSERT INTO drafts (id, module, data, updated_at) 
     VALUES ($1, $2, $3, NOW())
     ON CONFLICT (id) DO UPDATE SET data = $3, updated_at = NOW()`,
        [id, module, JSON.stringify(data)]
    );
}

/**
 * Load draft from local DB
 * @param {string} id - Draft ID
 * @returns {Promise<object|null>}
 */
export async function loadDraft(id) {
    const db = await getDB();
    const result = await db.query(
        'SELECT data FROM drafts WHERE id = $1',
        [id]
    );
    return result.rows[0]?.data || null;
}

/**
 * Delete draft
 * @param {string} id - Draft ID
 */
export async function deleteDraft(id) {
    const db = await getDB();
    await db.query('DELETE FROM drafts WHERE id = $1', [id]);
}

/**
 * List all drafts for a module
 * @param {string} module - Module name
 * @returns {Promise<Array>}
 */
export async function listDrafts(module) {
    const db = await getDB();
    const result = await db.query(
        'SELECT id, data, updated_at FROM drafts WHERE module = $1 ORDER BY updated_at DESC',
        [module]
    );
    return result.rows;
}

// ============================================
// 🔄 Sync Queue (Offline-First)
// ============================================

/**
 * Add action to sync queue
 * @param {string} action - Action type
 * @param {object} payload - Action payload
 */
export async function queueSync(action, payload) {
    const db = await getDB();
    await db.query(
        'INSERT INTO sync_queue (action, payload) VALUES ($1, $2)',
        [action, JSON.stringify(payload)]
    );
}

/**
 * Get pending sync items
 * @returns {Promise<Array>}
 */
export async function getPendingSync() {
    const db = await getDB();
    const result = await db.query(
        'SELECT * FROM sync_queue WHERE synced = FALSE ORDER BY created_at'
    );
    return result.rows;
}

/**
 * Mark sync items as completed
 * @param {number[]} ids - Synced item IDs
 */
export async function markSynced(ids) {
    const db = await getDB();
    await db.query(
        'UPDATE sync_queue SET synced = TRUE WHERE id = ANY($1)',
        [ids]
    );
}
