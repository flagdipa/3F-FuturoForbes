-- Migration 008: Add profile fields to usuarios table
-- Adds nombre and apellido for user profile management

ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(100) DEFAULT NULL;

ALTER TABLE usuarios ADD COLUMN apellido VARCHAR(100) DEFAULT NULL;