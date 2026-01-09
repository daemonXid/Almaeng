-- PGlite Initial Schema
-- This file is for documentation and manual execution if needed.
-- The schema is auto-created in index.js

-- Drafts table for auto-save functionality
CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sync queue for offline-first pattern
CREATE TABLE IF NOT EXISTS sync_queue (
    id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    synced BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_drafts_module ON drafts(module);
CREATE INDEX IF NOT EXISTS idx_drafts_updated ON drafts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_pending ON sync_queue(synced) WHERE synced = FALSE;
