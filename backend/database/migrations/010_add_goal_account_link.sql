-- Migration 010: Link goals to accounts for automatic balance tracking

ALTER TABLE metas_ahorro ADD COLUMN id_cuenta INT DEFAULT NULL;

ALTER TABLE metas_ahorro
ADD FOREIGN KEY (id_cuenta) REFERENCES lista_cuentas (id_cuenta);