-- Migration 003: Add Currency History (MySQL VERSION)
-- Phase 1 - High Priority
-- Created: 2026-02-01
--
-- This migration adds historical exchange rates for accurate multi-currency conversions

CREATE TABLE IF NOT EXISTS historial_divisas (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_divisa INTEGER NOT NULL,
    fecha_tasa DATE NOT NULL,
    tasa_valor DECIMAL(20, 8) NOT NULL,
    tipo_actualizacion INTEGER DEFAULT 0, -- 0=Manual, 1=Automatic
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_divisa_fecha (id_divisa, fecha_tasa),
    CONSTRAINT fk_historial_divisa FOREIGN KEY (id_divisa) REFERENCES divisas (id_divisa) ON DELETE CASCADE
);

-- Indexes for fast lookups
CREATE INDEX idx_historial_divisa ON historial_divisas (id_divisa);

CREATE INDEX idx_historial_fecha ON historial_divisas (fecha_tasa);

-- Rollback script
-- DROP TABLE IF EXISTS historial_divisas;