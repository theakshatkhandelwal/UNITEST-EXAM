-- Fix qtype and answer columns in quiz_question table
-- This migration fixes the error: "value too long for type character varying(10)"
-- The qtype column needs to be VARCHAR(20) to support 'subjective' (10 chars) and other types
-- The answer column needs to be TEXT to support long subjective answers

-- For PostgreSQL/Neon DB:

-- Fix qtype column
ALTER TABLE quiz_question ALTER COLUMN qtype TYPE VARCHAR(20);

-- Fix answer column (change from VARCHAR(10) to TEXT for long subjective answers)
ALTER TABLE quiz_question ALTER COLUMN answer TYPE TEXT;

-- Verify the changes
-- SELECT column_name, data_type, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'quiz_question' AND column_name IN ('qtype', 'answer');
-- Should show:
-- qtype | character varying | 20
-- answer | text | null

