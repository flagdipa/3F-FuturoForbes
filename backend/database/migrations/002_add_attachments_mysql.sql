-- Migration 002: Add Attachments System (MySQL VERSION)
-- Phase 1 - High Priority
-- Created: 2026-02-01
--
-- This migration adds polymorphic attachments for any entity

CREATE TABLE IF NOT EXISTS adjuntos (
    id_adjunto INT AUTO_INCREMENT PRIMARY KEY,
    tipo_referencia VARCHAR(50) NOT NULL, -- 'Transaccion', 'Cuenta', 'Beneficiario', etc.
    id_referencia INTEGER NOT NULL,
    descripcion TEXT,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo TEXT NOT NULL,
    tipo_mime VARCHAR(100),
    tamaño_bytes INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

-- Composite index for quick lookups by entity
CREATE INDEX idx_adjuntos_ref ON adjuntos (
    tipo_referencia,
    id_referencia
);

CREATE INDEX idx_adjuntos_fecha ON adjuntos (fecha_creacion);

-- Rollback script
-- DROP TABLE IF EXISTS adjuntos;