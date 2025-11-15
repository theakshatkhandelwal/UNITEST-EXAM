# 🔧 Reset Password Migration - Quick Fix

## Problem
You're seeing the error: `column user.reset_token does not exist`

This means the database columns for password reset haven't been created yet.

## ✅ Solution: Run Migration

### Option 1: Use Migration Route (Easiest)

1. **Visit this URL in your browser:**
   ```
   https://your-website.vercel.app/dev/migrate_db
   ```
   (Replace `your-website.vercel.app` with your actual domain)

2. **The migration will run automatically** and add the missing columns.

3. **You should see success messages** like:
   - ✅ Added reset_token column
   - ✅ Added reset_token_expiry column

### Option 2: Run SQL Directly in Neon DB (If Option 1 doesn't work)

1. **Go to Neon DB Console:**
   - Open: https://console.neon.tech
   - Log in and select your project

2. **Open SQL Editor:**
   - Click **"SQL Editor"** in the left sidebar
   - Click **"New Query"**

3. **Copy and paste this SQL:**
   ```sql
   -- Add reset_token column
   ALTER TABLE "user" ADD COLUMN IF NOT EXISTS reset_token VARCHAR(100) UNIQUE;
   
   -- Add reset_token_expiry column
   ALTER TABLE "user" ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP;
   ```

4. **Click "Run"** (or press `Ctrl+Enter`)

5. **Verify the columns were added:**
   ```sql
   SELECT column_name, data_type, is_nullable
   FROM information_schema.columns
   WHERE table_name = 'user' 
   AND column_name IN ('reset_token', 'reset_token_expiry');
   ```

   You should see both columns listed.

### Option 3: Wait for Auto-Migration

The `init_db()` function should automatically add these columns when the app starts. If you just deployed, wait a few minutes and try again. The columns will be added on the next app restart.

## ✅ After Migration

Once the migration is complete:
- The "Forgot Password?" feature will work
- Users can request password reset links
- Reset tokens will be stored and validated

## 🔍 Troubleshooting

**If you still see errors:**
1. Check that you're connected to the correct database
2. Verify the SQL ran successfully in Neon DB
3. Try refreshing the page or restarting the app
4. Check Vercel logs for any migration errors

