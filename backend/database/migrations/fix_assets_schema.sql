-- Migration to fix Assets table schema in System 3F
-- This aligns the DB table 'activos' with the SQLModel definition in models_advanced.py

-- 1. Backup or Drop existing table (if no critical data)
-- Since we are in development, we can drop and recreate or alter.
-- Let's drop it to ensure clean structure.

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS activos;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE activos (
    id_activo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_activo VARCHAR(255) NOT NULL,
    tipo_activo VARCHAR(255) NOT NULL,
    valor_inicial DECIMAL(20, 8) NOT NULL,
    valor_actual DECIMAL(20, 8) NOT NULL,
    fecha_compra DATE NULL,
    notas TEXT NULL,
    tasa_variacion DECIMAL(10, 4) DEFAULT 0.0000,
    metodo_variacion VARCHAR(50) DEFAULT 'None',
    frecuencia_variacion VARCHAR(50) DEFAULT 'Yearly',
    activo INT DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_activo_nombre (nombre_activo),
    INDEX idx_activo_status (activo)
) ENGINE = InnoDB;

-- Ensure historial_activos matches too
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS historial_activos;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE historial_activos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_activo INT NOT NULL,
    fecha DATE NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    notas TEXT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_activo) REFERENCES activos (id_activo) ON DELETE CASCADE,
    INDEX idx_historial_activo (id_activo),
    INDEX idx_historial_fecha (fecha)
) ENGINE = InnoDB;