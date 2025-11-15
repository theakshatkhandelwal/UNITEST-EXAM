# Fix Qtype Column Size Error

## Problem
When creating quizzes with subjective questions, you get this error:
```
Error: value too long for type character varying(10)
```

This happens because the `qtype` column in the `quiz_question` table is `VARCHAR(10)`, but `'subjective'` is 10 characters, which can exceed the limit.

## Solution

### Option 1: Run Migration Route (Easiest)
1. Visit: `https://your-domain.com/dev/migrate_db`
2. The migration will automatically fix the column size
3. You should see: "✅ Updated qtype column to VARCHAR(20)"

### Option 2: Run SQL Directly in Neon DB
1. Go to your Neon DB dashboard
2. Open the SQL Editor
3. Run this SQL command:

```sql
ALTER TABLE quiz_question ALTER COLUMN qtype TYPE VARCHAR(20);
```

4. Verify it worked:
```sql
SELECT column_name, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'quiz_question' AND column_name = 'qtype';
```

Should show: `qtype | 20`

### Option 3: Use the SQL File
1. Open `fix_qtype_column.sql` in this repository
2. Copy the SQL command
3. Run it in your Neon DB SQL Editor

## After Migration

Once the migration is complete:
- ✅ You can create quizzes with subjective questions
- ✅ The `qtype` column will accept: 'mcq', 'subjective', 'coding'
- ✅ No more "value too long" errors

## Verification

After running the migration, try creating a quiz with subjective questions again. It should work without errors.

## Notes

- The model already defines `qtype` as `String(20)`, so this just syncs the database
- This is a safe operation - it only increases the column size
- No data will be lost
- The migration is idempotent (safe to run multiple times)

