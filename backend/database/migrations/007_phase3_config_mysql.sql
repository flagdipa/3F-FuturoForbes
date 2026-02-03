-- Migration 007: Phase 3 - Budget Years, Config, and Custom Fields (MySQL VERSION)
-- Created: 2026-02-01
--
-- Adds support for multi-year budgets, system settings, and extra fields
-- Using 'anio'/'anios' to avoid character encoding issues in shell/windows.

-- Clean up partially failed previous attempts
DROP TABLE IF EXISTS valores_campos_personalizados;

DROP TABLE IF EXISTS campos_personalizados;

DROP TABLE IF EXISTS configuraciones;

-- Procedure to safely drop the foreign key if it exists
SET
    @fk_exists = (
        SELECT COUNT(*)
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE
            CONSTRAINT_NAME = 'fk_pres_anio'
            AND TABLE_SCHEMA = DATABASE()
    );

SET
    @sql = IF(
        @fk_exists > 0,
        'ALTER TABLE tabla_presupuestos DROP FOREIGN KEY fk_pres_anio',
        'SELECT "No FK to drop"'
    );

PREPARE stmt FROM @sql;

EXECUTE stmt;

DEALLOCATE PREPARE stmt;

DROP TABLE IF EXISTS anios_presupuesto;

-- 1. Budget Years table
CREATE TABLE anios_presupuesto (
    id_anio_presupuesto INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    notas TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_anio_val (anio)
);

-- 2. Link existing budget table to years
ALTER TABLE tabla_presupuestos
MODIFY COLUMN id_año_presupuesto INT DEFAULT NULL;

-- Rename column to standardized id_anio_presupuesto if needed
SET
    @col_exists = (
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE
            TABLE_NAME = 'tabla_presupuestos'
            AND COLUMN_NAME = 'id_anio_presupuesto'
            AND TABLE_SCHEMA = DATABASE()
    );

SET
    @sql = IF(
        @col_exists = 0,
        'ALTER TABLE tabla_presupuestos CHANGE COLUMN id_año_presupuesto id_anio_presupuesto INT DEFAULT NULL',
        'SELECT "Column already renamed"'
    );

PREPARE stmt FROM @sql;

EXECUTE stmt;

DEALLOCATE PREPARE stmt;

ALTER TABLE tabla_presupuestos
ADD CONSTRAINT fk_pres_anio FOREIGN KEY (id_anio_presupuesto) REFERENCES anios_presupuesto (id_anio_presupuesto) ON DELETE SET NULL;

-- 3. System Configuration
CREATE TABLE configuraciones (
    clave VARCHAR(100) PRIMARY KEY,
    valor VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Custom Fields (EAV)
CREATE TABLE campos_personalizados (
    id_campo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_campo VARCHAR(100) NOT NULL,
    tipo_entidad VARCHAR(50) NOT NULL, -- 'Transaccion', 'Cuenta', etc.
    tipo_dato VARCHAR(20) NOT NULL, -- 'String', 'Number', etc.
    requerido TINYINT(1) DEFAULT 0,
    activo INTEGER DEFAULT 1
);

CREATE TABLE valores_campos_personalizados (
    id_valor INT AUTO_INCREMENT PRIMARY KEY,
    id_campo INT NOT NULL,
    id_entidad INT NOT NULL,
    valor TEXT NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_valor_campo FOREIGN KEY (id_campo) REFERENCES campos_personalizados (id_campo) ON DELETE CASCADE
);

-- Index for EAV queries
CREATE INDEX idx_valor_entidad ON valores_campos_personalizados (id_entidad);

CREATE INDEX idx_eav_lookup ON valores_campos_personalizados (id_campo, id_entidad);

-- Seed initial years
INSERT INTO
    anios_presupuesto (anio, nombre)
VALUES (2024, 'Presupuesto Base 2024'),
    (2025, 'Presupuesto Base 2025');