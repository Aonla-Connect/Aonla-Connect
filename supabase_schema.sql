-- ═══════════════════════════════════════════════════════════
--   AONLA CONNECT — Supabase SQL Schema
--   Supabase ke SQL Editor mein yeh sab run karo ek baar
-- ═══════════════════════════════════════════════════════════

-- ── 1. USERS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         TEXT NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone        TEXT,
    avatar_url   TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. MAIN GROUP MESSAGES ──────────────────────────────────
-- Yeh "Aonla Connect" main group hai
-- user_id = 'ai' allowed hai AI messages ke liye
CREATE TABLE IF NOT EXISTS main_group_messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    TEXT NOT NULL,           -- UUID ya 'ai'
    content    TEXT NOT NULL DEFAULT '',
    media_url  TEXT,                    -- Cloudinary URL
    is_ai      BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Foreign key only for non-AI messages (soft reference)
-- Note: user_id is TEXT to allow 'ai' as special value

-- ── 3. PRIVATE MESSAGES ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS private_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content     TEXT NOT NULL DEFAULT '',
    media_url   TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS pm_sender_receiver ON private_messages(sender_id, receiver_id);
CREATE INDEX IF NOT EXISTS pm_receiver_sender ON private_messages(receiver_id, sender_id);

-- ── 4. GROUPS ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS groups (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 5. GROUP MEMBERS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS group_members (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id   UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_admin   BOOLEAN DEFAULT FALSE,
    joined_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(group_id, user_id)
);

CREATE INDEX IF NOT EXISTS gm_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS gm_user  ON group_members(user_id);

-- ── 6. GROUP MESSAGES ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS group_messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id   UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content    TEXT NOT NULL DEFAULT '',
    media_url  TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS gmsgs_group ON group_messages(group_id);

-- ═══════════════════════════════════════════════════════════
-- RLS (Row Level Security) — Basic Open Policies
-- Production mein zyada strict policies lagao
-- ═══════════════════════════════════════════════════════════

ALTER TABLE users                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE main_group_messages   ENABLE ROW LEVEL SECURITY;
ALTER TABLE private_messages      ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups                ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members         ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_messages        ENABLE ROW LEVEL SECURITY;

-- Allow all reads & writes via anon key (Streamlit backend ke liye)
-- Production mein: use service_role key + stricter policies

CREATE POLICY "allow_all_users"              ON users               FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_main_group"         ON main_group_messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_private"            ON private_messages    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_groups"             ON groups              FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_group_members"      ON group_members       FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_group_messages"     ON group_messages      FOR ALL USING (true) WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════
-- DONE! Ab Streamlit app chalao 🚀
-- ═══════════════════════════════════════════════════════════
