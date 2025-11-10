# 🔧 Fix Database Migration - Quick Guide

## Problem
You're seeing the error: `ERROR: column "is_admin" of relation "user" does not exist`

This means the database columns haven't been created yet. The automatic migration might not have run.

## ✅ Solution: Run Manual Migration

### Step 1: Go to Neon DB Console
1. Open: https://console.neon.tech
2. Log in to your account
3. Select your project

### Step 2: Open SQL Editor
1. Click on **"SQL Editor"** in the left sidebar
2. Click **"New Query"** or open a new tab

### Step 3: Run the Migration SQL
Copy and paste this entire SQL script into the SQL Editor:

```sql
-- Add is_admin column to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Add last_login column to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create login_history table
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);
```

### Step 4: Click "Run"
Click the **"Run"** button (or press `Ctrl+Enter`)

You should see:
- ✅ Success messages for each command
- ✅ Or "already exists" messages (which is fine)

### Step 5: Set Yourself as Admin
After the migration is complete, run this query (replace `YOUR_USERNAME` with your actual username):

```sql
UPDATE "user" 
SET is_admin = TRUE 
WHERE username = 'YOUR_USERNAME';
```

**Example:**
```sql
UPDATE "user" 
SET is_admin = TRUE 
WHERE username = 'theakshatkhandelwal';
```

### Step 6: Verify Admin Status
Check if you're now an admin:

```sql
SELECT id, username, email, is_admin, last_login 
FROM "user" 
WHERE username = 'YOUR_USERNAME';
```

You should see `is_admin = true` (or `t` in PostgreSQL).

## 🚀 After Migration

1. **Restart your application** (if running locally) or wait for Vercel to redeploy
2. **Log out** and **log back in**
3. **Visit**: https://unitest.in/admin/users
4. You should now see the admin dashboard!

## 🔍 Verify Migration Worked

Run these queries to verify:

```sql
-- Check if is_admin column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name = 'is_admin';

-- Check if login_history table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'login_history';

-- Check all columns in user table
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user' 
ORDER BY ordinal_position;
```

## ❌ If You Still Get Errors

### Error: "relation 'user' does not exist"
- Make sure you're connected to the correct database
- Check that your `DATABASE_URL` environment variable is correct

### Error: "permission denied"
- Make sure you're using the correct database credentials
- Check that you have admin/owner access to the database

### Error: "column already exists"
- That's fine! It means the column was already added
- You can skip that command and continue

## 📝 Alternative: Use the Migration File

You can also use the `migrate_admin_and_login.sql` file:

1. Open the file in your editor
2. Copy all the SQL commands
3. Paste into Neon DB SQL Editor
4. Run it

## 🎯 Quick Fix (Copy-Paste Ready)

Here's the complete SQL to run in one go:

```sql
-- Complete Migration Script
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);

-- Set yourself as admin (replace 'YOUR_USERNAME')
UPDATE "user" SET is_admin = TRUE WHERE username = 'YOUR_USERNAME';
```

---

**After running this migration, everything should work!** ✅

