-- Migration SQL for Admin Access and Login Tracking
-- Run this in Neon DB SQL Editor to add the required columns and tables

-- Step 1: Add is_admin column to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Step 2: Add last_login column to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Step 3: Create login_history table
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- Step 4: Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_login_time ON login_history(login_time);

-- Step 5: Verify the columns were added (optional - check the results)
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name IN ('is_admin', 'last_login');

-- Step 6: Verify login_history table was created (optional)
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'login_history';

-- After running this migration, you can set yourself as admin:
-- UPDATE "user" SET is_admin = TRUE WHERE username = 'YOUR_USERNAME';

