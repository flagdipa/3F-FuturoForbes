-- Migration 006: Add Investments/Stocks (MySQL VERSION)
-- Phase 2 - Medium Priority
-- Created: 2026-02-01
--
-- This migration adds support for tracking stock holdings and price history

CREATE TABLE IF NOT EXISTS inversiones (
    id_inversion INT AUTO_INCREMENT PRIMARY KEY,
    id_cuenta INTEGER NOT NULL,
    nombre_inversion VARCHAR(255) NOT NULL,
    simbolo VARCHAR(20) NOT NULL,
    tipo_inversion VARCHAR(50) DEFAULT 'Stock', -- Stock, Fund, Crypto, etc.
    cantidad DECIMAL(20, 8) NOT NULL,
    precio_compra DECIMAL(20, 8) NOT NULL,
    precio_actual DECIMAL(20, 8) NOT NULL,
    comision DECIMAL(20, 8) DEFAULT 0,
    notas TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_inv_cuenta FOREIGN KEY (id_cuenta) REFERENCES lista_cuentas (id_cuenta) ON DELETE CASCADE,
    INDEX idx_inv_simbolo (simbolo),
    INDEX idx_inv_nombre (nombre_inversion),
    INDEX idx_inv_activo (activo)
);

CREATE TABLE IF NOT EXISTS historial_inversiones (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_inversion INT NOT NULL,
    fecha DATE NOT NULL,
    precio DECIMAL(20, 8) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_inv FOREIGN KEY (id_inversion) REFERENCES inversiones (id_inversion) ON DELETE CASCADE,
    INDEX idx_hist_inv_fecha (id_inversion, fecha)
);

-- Rollback script
-- DROP TABLE IF EXISTS historial_inversiones;
-- DROP TABLE IF EXISTS inversiones;