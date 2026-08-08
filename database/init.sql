-- User Management API - database initialization script
-- Run this with a MySQL client, e.g.:
--   mysql -u root -p < database/init.sql

CREATE DATABASE IF NOT EXISTS users
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE users;

CREATE TABLE IF NOT EXISTS users (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role  VARCHAR(50)  NOT NULL,
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- Optional: a dedicated database for the automated test suite.
-- Keep this separate from `users` - pytest creates/drops tables here on every run.
CREATE DATABASE IF NOT EXISTS users_test
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
