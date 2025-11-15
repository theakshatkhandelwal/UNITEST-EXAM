# Fix Qtype and Answer Column Size Error

## Problem
When creating quizzes with subjective questions, you get this error:
```
Error: value too long for type character varying(10)
```

This happens because:
1. The `qtype` column in the `quiz_question` table is `VARCHAR(10)`, but `'subjective'` is 10 characters
2. The `answer` column is `VARCHAR(10)`, but subjective answers can be very long (full paragraphs)

## Solution

### Option 1: Run Migration Route (Easiest)
1. Visit: `https://your-domain.com/dev/migrate_db`
2. The migration will automatically fix the column size
3. You should see: "✅ Updated qtype column to VARCHAR(20)"

### Option 2: Run SQL Directly in Neon DB
1. Go to your Neon DB dashboard
2. Open the SQL Editor
3. Run these SQL commands:

```sql
-- Fix qtype column
ALTER TABLE quiz_question ALTER COLUMN qtype TYPE VARCHAR(20);

-- Fix answer column (for long subjective answers)
ALTER TABLE quiz_question ALTER COLUMN answer TYPE TEXT;
```

4. Verify it worked:
```sql
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'quiz_question' AND column_name IN ('qtype', 'answer');
```

Should show:
- `qtype | character varying | 20`
- `answer | text | null`

### Option 3: Use the SQL File
1. Open `fix_qtype_column.sql` in this repository
2. Copy the SQL command
3. Run it in your Neon DB SQL Editor

## After Migration

Once the migration is complete:
- ✅ You can create quizzes with subjective questions
- ✅ The `qtype` column will accept: 'mcq', 'subjective', 'coding'
- ✅ The `answer` column can store long subjective answers (full paragraphs)
- ✅ No more "value too long" errors

## Verification

After running the migration, try creating a quiz with subjective questions again. It should work without errors.

## Notes

- The model already defines `qtype` as `String(20)`, so this just syncs the database
- This is a safe operation - it only increases the column size
- No data will be lost
- The migration is idempotent (safe to run multiple times)

