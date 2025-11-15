-- Add reset_token and reset_token_expiry columns to user table
-- This migration adds support for password reset functionality

-- Add reset_token column (VARCHAR(100), unique, nullable)
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS reset_token VARCHAR(100) UNIQUE;

-- Add reset_token_expiry column (TIMESTAMP, nullable)
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP;

-- Verify the columns were added
-- Run this query to check:
-- SELECT column_name, data_type, is_nullable, character_maximum_length
-- FROM information_schema.columns
-- WHERE table_name = 'user' AND column_name IN ('reset_token', 'reset_token_expiry');

