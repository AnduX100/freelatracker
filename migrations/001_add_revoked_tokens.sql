-- Create revoked_tokens table for JWT revocation support.
-- Adjust types as needed for your DB engine.

-- PostgreSQL / MySQL compatible version:
CREATE TABLE IF NOT EXISTS revoked_tokens (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_revoked_tokens_jti ON revoked_tokens (jti);
CREATE INDEX IF NOT EXISTS idx_revoked_tokens_expires_at ON revoked_tokens (expires_at);

-- SQLite fallback (ignore errors if indexes already exist):
-- CREATE TABLE IF NOT EXISTS revoked_tokens (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     jti TEXT NOT NULL UNIQUE,
--     expires_at TEXT NOT NULL,
--     created_at TEXT NOT NULL DEFAULT (datetime('now'))
-- );
-- CREATE INDEX IF NOT EXISTS idx_revoked_tokens_jti ON revoked_tokens (jti);
-- CREATE INDEX IF NOT EXISTS idx_revoked_tokens_expires_at ON revoked_tokens (expires_at);
