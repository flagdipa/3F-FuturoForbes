-- Migration 003: Add Currency History
-- Phase 1 - High Priority
-- Created: 2026-02-01
--
-- This migration adds historical exchange rates for accurate multi-currency conversions

CREATE TABLE IF NOT EXISTS historial_divisas (
    id_historial SERIAL PRIMARY KEY,
    id_divisa INTEGER NOT NULL,
    fecha_tasa DATE NOT NULL,
    tasa_valor DECIMAL(20, 8) NOT NULL,
    tipo_actualizacion INTEGER DEFAULT 0, -- 0=Manual, 1=Automatic
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_divisa, fecha_tasa),
    CONSTRAINT fk_historial_divisa FOREIGN KEY (id_divisa) REFERENCES divisas (id_divisa) ON DELETE CASCADE
);

-- Indexes for fast lookups
CREATE INDEX idx_historial_divisa ON historial_divisas (id_divisa);

CREATE INDEX idx_historial_fecha ON historial_divisas (fecha_tasa DESC);

CREATE INDEX idx_historial_divisa_fecha ON historial_divisas (id_divisa, fecha_tasa DESC);

-- Comments for documentation
COMMENT ON
TABLE historial_divisas IS 'Historical exchange rates for accurate currency conversions';

COMMENT ON COLUMN historial_divisas.tipo_actualizacion IS '0=Manual entry, 1=Automatic API update';

-- Rollback script
-- DROP TABLE IF EXISTS historial_divisas;