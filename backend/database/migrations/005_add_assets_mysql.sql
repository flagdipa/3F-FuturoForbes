-- Migration 005: Add Assets Tracking (MySQL VERSION)
-- Phase 2 - Medium Priority
-- Created: 2026-02-01
--
-- This migration adds support for tracking physical assets and their history


CREATE TABLE IF NOT EXISTS activos (
    id_activo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_activo VARCHAR(255) NOT NULL,
    tipo_activo VARCHAR(100) NOT NULL,
    
    valor_inicial DECIMAL(20, 8) NOT NULL,
    valor_actual DECIMAL(20, 8) NOT NULL,
    
    fecha_compra DATE DEFAULT NULL,
    notas TEXT,

-- Variation logic
tasa_variacion DECIMAL(10, 4) DEFAULT 0,
    metodo_variacion VARCHAR(50) DEFAULT 'None', -- Linear, Percentage, None
    frecuencia_variacion VARCHAR(50) DEFAULT 'Yearly',
    
    activo INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_activo_nombre (nombre_activo),
    INDEX idx_activo_status (activo)
);

CREATE TABLE IF NOT EXISTS historial_activos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_activo INT NOT NULL,
    fecha DATE NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    notas TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_activo FOREIGN KEY (id_activo) REFERENCES activos (id_activo) ON DELETE CASCADE,
    INDEX idx_hist_activo_fecha (id_activo, fecha)
);

-- Rollback script
-- DROP TABLE IF EXISTS historial_activos;
-- DROP TABLE IF EXISTS activos;