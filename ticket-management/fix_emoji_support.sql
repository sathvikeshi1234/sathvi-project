-- SQL script to fix emoji support in MySQL database
-- Run this in MySQL to update character set to utf8mb4

-- Update database character set
ALTER DATABASE ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Update tables character set
ALTER TABLE tickets_chatmessage CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE tickets_chatmessage MODIFY COLUMN text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Update other relevant tables if needed
ALTER TABLE users_user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE users_user MODIFY COLUMN first_name VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE users_user MODIFY COLUMN last_name VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
