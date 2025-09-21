-- Add password column to users table
-- Run this in your Supabase SQL Editor

ALTER TABLE users ADD COLUMN password VARCHAR(255);

-- Add a comment to document this column
COMMENT ON COLUMN users.password IS 'User password (should be hashed in production)';
