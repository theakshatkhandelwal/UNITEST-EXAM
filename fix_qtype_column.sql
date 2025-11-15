-- Fix qtype column size in quiz_question table
-- This migration fixes the error: "value too long for type character varying(10)"
-- The qtype column needs to be VARCHAR(20) to support 'subjective' (10 chars) and other types

-- Check current column size and update if needed
-- For PostgreSQL/Neon DB:

ALTER TABLE quiz_question ALTER COLUMN qtype TYPE VARCHAR(20);

-- Verify the change
-- SELECT column_name, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'quiz_question' AND column_name = 'qtype';
-- Should show: qtype | 20

