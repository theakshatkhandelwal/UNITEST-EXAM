# 🗄️ NeonDB Migration Guide

## How to Run SQL Migration in NeonDB

### Step 1: Access NeonDB Dashboard

1. Go to [https://console.neon.tech](https://console.neon.tech)
2. Log in to your account
3. Select your project (the one connected to your UNITEST-EXAM app)

### Step 2: Open SQL Editor

1. In your NeonDB project dashboard, click on **"SQL Editor"** in the left sidebar
2. Or click the **"Query"** button at the top

### Step 3: Run Migration SQL

Copy and paste the following SQL commands into the SQL Editor, then click **"Run"**:

```sql
-- Add columns to quiz_question table
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS test_cases_json TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS language_constraints TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS time_limit_seconds INTEGER;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS memory_limit_mb INTEGER;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS sample_input TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS sample_output TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS starter_code TEXT;

-- Add columns to quiz_answer table
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS code_language VARCHAR(20);
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS test_results_json TEXT;
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS passed_test_cases INTEGER DEFAULT 0;
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS total_test_cases INTEGER DEFAULT 0;

-- Add columns to quiz_submission table (some may already exist)
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS review_unlocked_at TIMESTAMP;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS fullscreen_exit_flag BOOLEAN DEFAULT FALSE;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS answered_count INTEGER DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS question_count INTEGER DEFAULT 0;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS is_full_completion BOOLEAN DEFAULT FALSE;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS completed BOOLEAN DEFAULT FALSE;
```

### Step 4: Verify Migration

After running the SQL, you should see:
- ✅ Success message for each command
- Or "already exists" messages (which is fine - means columns were already added)

### Step 5: Test Your App

1. Go back to your app
2. Try creating a quiz again
3. The error should be gone!

---

## Alternative: Use Web Route

If you prefer, you can also visit:
```
https://your-app-url.vercel.app/run-migration
```

This will run the migration automatically (after I push the route update).

---

## Troubleshooting

### If you get "column already exists" errors:
- ✅ That's fine! It means the column was already added
- Just continue with the other commands

### If you get permission errors:
- Make sure you're logged into the correct NeonDB account
- Check that you have admin access to the project

### If migration still fails:
- Check the exact error message
- Make sure you're running the SQL in the correct database
- Verify your DATABASE_URL environment variable is correct

---

## Visual Guide

1. **NeonDB Dashboard** → Your Project
2. **Left Sidebar** → Click "SQL Editor"
3. **SQL Editor** → Paste the SQL commands above
4. **Click "Run"** → Wait for success messages
5. **Done!** → Try creating a quiz

---

**Need Help?** Check the error message in your app - it will tell you exactly which column is missing.

