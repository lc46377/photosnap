CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE snaps (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  s3_key       TEXT NOT NULL,
  uploaded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
