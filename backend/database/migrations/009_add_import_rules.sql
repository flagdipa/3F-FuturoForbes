-- Migration 009: Create import rules table for auto-categorization
-- Rules match CSV description patterns to automatically assign categories and beneficiaries

CREATE TABLE reglas_importacion (
    id_regla INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    patron VARCHAR(255) NOT NULL,
    id_categoria INT DEFAULT NULL,
    id_beneficiario INT DEFAULT NULL,
    prioridad INT DEFAULT 0,
    activo TINYINT DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario),
    FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria),
    FOREIGN KEY (id_beneficiario) REFERENCES beneficiarios (id_beneficiario)
);