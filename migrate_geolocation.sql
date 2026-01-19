-- Migration SQL for Geolocation Tracking
-- Run this in Neon DB SQL Editor to add location columns to login_history table

-- Step 1: Add geolocation columns to login_history table
ALTER TABLE login_history ADD COLUMN IF NOT EXISTS latitude FLOAT;
ALTER TABLE login_history ADD COLUMN IF NOT EXISTS longitude FLOAT;
ALTER TABLE login_history ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE login_history ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE login_history ADD COLUMN IF NOT EXISTS region VARCHAR(100);

-- Step 2: Verify the columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'login_history' 
AND column_name IN ('latitude', 'longitude', 'city', 'country', 'region');

-- Step 3: View sample data with new columns
SELECT 
    lh.id,
    u.username,
    lh.ip_address,
    lh.login_time,
    lh.latitude,
    lh.longitude,
    lh.city,
    lh.country,
    lh.region
FROM login_history lh
JOIN "user" u ON lh.user_id = u.id
ORDER BY lh.login_time DESC
LIMIT 10;
