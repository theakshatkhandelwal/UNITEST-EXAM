-- Migration SQL to add violation flag columns to quiz_submission table
-- Run this in NeonDB SQL Editor if columns don't exist

-- Add Alt+Tab violation flag
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS alt_tab_flag BOOLEAN DEFAULT FALSE;

-- Add Win+Shift+S violation flag (Windows Snipping Tool)
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS win_shift_s_flag BOOLEAN DEFAULT FALSE;

-- Add Win+PrintScreen violation flag
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS win_prtscn_flag BOOLEAN DEFAULT FALSE;

-- Add PrintScreen violation flag
ALTER TABLE quiz_submission ADD COLUMN IF NOT EXISTS prtscn_flag BOOLEAN DEFAULT FALSE;

