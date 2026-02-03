-- Migration 004: Add Recurring Transactions (MySQL VERSION)
-- Phase 2 - Medium Priority
-- Created: 2026-02-01
--
-- This migration adds support for scheduled and recurring transactions

-- DROP EXISTING TABLE IF IT EXISTS (Cleaning legacy/incompatible structure)
DROP TABLE IF EXISTS transacciones_programadas;

CREATE TABLE transacciones_programadas (
    id_recurrencia INT AUTO_INCREMENT PRIMARY KEY,

-- Transaction Data
id_cuenta INTEGER NOT NULL,
id_cuenta_destino INTEGER DEFAULT NULL,
id_beneficiario INTEGER NOT NULL,
id_categoria INTEGER DEFAULT NULL,
codigo_transaccion VARCHAR(20) NOT NULL, -- 'Withdrawal', 'Deposit', 'Transfer'
monto_transaccion DECIMAL(20, 8) NOT NULL,
notas TEXT,

-- Recurring Logic
frecuencia VARCHAR(20) NOT NULL, -- 'Daily', 'Weekly', 'Monthly', etc.
intervalo INTEGER DEFAULT 1,
dia_semana INTEGER DEFAULT NULL, -- 0-6 (Mon-Sun)
dia_mes INTEGER DEFAULT NULL, -- 1-31
fecha_inicio DATE NOT NULL,
proxima_fecha DATE NOT NULL,
fecha_fin DATE DEFAULT NULL,
limite_ejecuciones INTEGER DEFAULT -1, -- -1 for unlimited
ejecuciones_realizadas INTEGER DEFAULT 0,
activo INTEGER DEFAULT 1,
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

-- Foreign Keys
CONSTRAINT fk_recur_cuenta FOREIGN KEY (id_cuenta) 
        REFERENCES lista_cuentas(id_cuenta) ON DELETE CASCADE,
    CONSTRAINT fk_recur_cuenta_dest FOREIGN KEY (id_cuenta_destino) 
        REFERENCES lista_cuentas(id_cuenta) ON DELETE SET NULL,
    CONSTRAINT fk_recur_beneficiario FOREIGN KEY (id_beneficiario) 
        REFERENCES beneficiarios(id_beneficiario) ON DELETE CASCADE,
    CONSTRAINT fk_recur_categoria FOREIGN KEY (id_categoria) 
        REFERENCES categorias(id_categoria) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_recur_prox_fecha ON transacciones_programadas (proxima_fecha);

CREATE INDEX idx_recur_activo ON transacciones_programadas (activo);

CREATE INDEX idx_recur_cuenta ON transacciones_programadas (id_cuenta);

-- Rollback script
-- DROP TABLE IF EXISTS transacciones_programadas;