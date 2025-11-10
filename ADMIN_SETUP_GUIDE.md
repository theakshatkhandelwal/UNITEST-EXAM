# 🔐 Admin Setup Guide - Restrict Admin Dashboard Access

This guide will help you set up admin-only access for the user statistics dashboard.

## 📋 Steps to Set Up Admin Access

### Step 1: Add Database Columns (Automatic)

The application will automatically add the required columns when it runs:
- `is_admin` (BOOLEAN) - Admin flag
- `last_login` (TIMESTAMP) - Last login time
- `login_history` table - Tracks all logins

### Step 2: Set Yourself as Admin in Neon DB

1. **Go to Neon DB Console**: https://console.neon.tech
2. **Select your project**
3. **Open SQL Editor**
4. **Run this SQL query** (replace `YOUR_USERNAME` with your actual username):

```sql
-- Set yourself as admin (replace 'YOUR_USERNAME' with your username)
UPDATE "user" 
SET is_admin = TRUE 
WHERE username = 'YOUR_USERNAME';
```

**Example:**
```sql
-- If your username is "akshat"
UPDATE "user" 
SET is_admin = TRUE 
WHERE username = 'akshat';
```

### Step 3: Verify Admin Status

Run this query to check if you're now an admin:

```sql
-- Check your admin status
SELECT id, username, email, is_admin, last_login 
FROM "user" 
WHERE username = 'YOUR_USERNAME';
```

You should see `is_admin = true` (or `t` in PostgreSQL).

### Step 4: Test Admin Access

1. **Log out** of your application (if logged in)
2. **Log back in** with your admin account
3. **Visit**: https://unitest.in/admin/users
4. You should now see the admin dashboard with login statistics!

## 🔒 Security Features

### Admin-Only Access
- Only users with `is_admin = TRUE` can access `/admin/users`
- Non-admin users will see: "Access denied: Administrator privileges required."
- They will be redirected to the dashboard

### Login Tracking
- Every login is recorded in the `login_history` table
- Tracks: login time, IP address, user agent
- Shows: total logins, logins by date, most active users, recent logins

## 📊 What You'll See in Admin Dashboard

### Signup Statistics
- Total Users
- Signups this month/week/today
- Users by role
- Recent signups
- Signups by date (last 30 days)

### Login Statistics (NEW!)
- **Total Logins** (all time) - Shows total login count and unique users
- **Logins Today/This Week/This Month**
- **Logins by Date** (last 30 days)
- **Most Active Users** (top 10 by login count)
- **Recent Logins** (last 20 with IP addresses)

## 🛠️ Manual Database Migration (If Needed)

If the automatic migration doesn't work, run these SQL commands in Neon DB:

```sql
-- Add is_admin column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Add last_login column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Create login_history table
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);
```

## 🎯 Setting Multiple Admins

To set multiple users as admins:

```sql
-- Set multiple users as admin by username
UPDATE "user" 
SET is_admin = TRUE 
WHERE username IN ('admin1', 'admin2', 'admin3');

-- Or set by email
UPDATE "user" 
SET is_admin = TRUE 
WHERE email IN ('admin1@example.com', 'admin2@example.com');
```

## ❌ Remove Admin Access

To remove admin access from a user:

```sql
-- Remove admin access
UPDATE "user" 
SET is_admin = FALSE 
WHERE username = 'USERNAME';
```

## 🔍 Check All Admins

To see all admin users:

```sql
-- List all admins
SELECT id, username, email, is_admin, created_at 
FROM "user" 
WHERE is_admin = TRUE;
```

## 📝 Notes

- **Admin status is permanent** until manually changed
- **Login tracking starts** after you deploy this update
- **Historical logins** won't be available (only new logins after deployment)
- **IP addresses** are tracked for security monitoring
- **User agents** are tracked to see what browsers/devices users use

## 🚨 Troubleshooting

### "Access denied" even though I'm admin
1. Check if `is_admin = TRUE` in the database
2. Log out and log back in
3. Clear your browser cache/cookies
4. Verify you're using the correct username

### Login statistics not showing
1. Make sure the `login_history` table exists
2. Try logging in again (this creates a login record)
3. Check if there are any errors in the application logs

### Database migration errors
1. Make sure you're connected to the correct database
2. Check that you have permission to alter tables
3. Run the SQL commands manually in Neon DB SQL Editor

## ✅ Verification Checklist

- [ ] `is_admin` column added to `user` table
- [ ] `last_login` column added to `user` table
- [ ] `login_history` table created
- [ ] Your username set to `is_admin = TRUE`
- [ ] Can access `/admin/users` route
- [ ] See login statistics in dashboard
- [ ] Non-admin users get "Access denied" message

---

**Need Help?** Check the application logs or contact support.

