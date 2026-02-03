-- Migration 001: Add Tags System
-- Phase 1 - High Priority
-- Created: 2026-02-01
--
-- This migration adds the tags/etiquetas system for flexible classification

-- Create etiquetas table
CREATE TABLE IF NOT EXISTS etiquetas (
    id_etiqueta SERIAL PRIMARY KEY,
    nombre_etiqueta VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7), -- Hex color format #RRGGBB
    activo INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etiquetas_nombre ON etiquetas (nombre_etiqueta);

CREATE INDEX idx_etiquetas_activo ON etiquetas (activo);

-- Create junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS transacciones_etiquetas (
    id_transaccion INTEGER NOT NULL,
    id_etiqueta INTEGER NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_transaccion, id_etiqueta),
    CONSTRAINT fk_trans_etiq_trans FOREIGN KEY (id_transaccion) REFERENCES libro_transacciones (id_transaccion) ON DELETE CASCADE,
    CONSTRAINT fk_trans_etiq_tag FOREIGN KEY (id_etiqueta) REFERENCES etiquetas (id_etiqueta) ON DELETE CASCADE
);

CREATE INDEX idx_trans_etiq_trans ON transacciones_etiquetas (id_transaccion);

CREATE INDEX idx_trans_etiq_tag ON transacciones_etiquetas (id_etiqueta);

-- Seed default tags
INSERT INTO
    etiquetas (nombre_etiqueta, color)
VALUES ('Urgente', '#FF0000'),
    ('Revisado', '#00FF00'),
    ('Pendiente', '#FFA500'),
    ('Personal', '#0000FF'),
    ('Trabajo', '#800080'),
    ('Impuestos', '#FF1493'),
    ('Reembolso', '#00CED1') ON CONFLICT (nombre_etiqueta) DO NOTHING;

-- Rollback script
-- DROP TABLE IF EXISTS transacciones_etiquetas;
-- DROP TABLE IF EXISTS etiquetas;