-- 🗄️ SCHEMA DE BASE DE DATOS DEFINITIVO — Sistema 3F (Futuro Forbes)
-- Compatibilidad: SQLite, PostgreSQL, MySQL
-- Versión: 2.0 (Double-Entry & Multi-User)

-- 1. USUARIOS Y PREFERENCIAS
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    theme_id TEXT DEFAULT '3f-neon',
    language TEXT DEFAULT 'es',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 2. DIVISAS Y TASAS DE CAMBIO
CREATE TABLE currencies (
    code TEXT PRIMARY KEY, -- ISO 4217 (ARS, USD, BTC)
    name TEXT NOT NULL,
    symbol TEXT,
    decimal_places INTEGER DEFAULT 2,
    is_base BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_currency TEXT REFERENCES currencies (code),
    to_currency TEXT REFERENCES currencies (code),
    rate DECIMAL(20, 8) NOT NULL,
    provider TEXT, -- 'dolar_hoy', 'criptoya', etc.
    rate_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. CUENTAS (Jerárquicas)
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    parent_id INTEGER NULL REFERENCES accounts (id),
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'ASSET', 'LIABILITY', 'EQUITY', 'INCOME', 'EXPENSE'
    currency_code TEXT REFERENCES currencies (code),
    account_number TEXT,
    institution_name TEXT,
    initial_balance DECIMAL(20, 8) DEFAULT 0,
    current_balance DECIMAL(20, 8) DEFAULT 0,
    color TEXT,
    icon TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 4. CATEGORÍAS (Jerárquicas)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    parent_id INTEGER NULL REFERENCES categories (id),
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'INCOME', 'EXPENSE'
    color TEXT,
    icon TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 5. BENEFICIARIOS (Payees)
CREATE TABLE payees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    default_category_id INTEGER REFERENCES categories (id),
    address TEXT,
    website TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 6. TRANSACCIONES Y SPLITS (Double-Entry)
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    date TIMESTAMP NOT NULL,
    description TEXT,
    payee_id INTEGER REFERENCES payees (id),
    status TEXT DEFAULT 'PENDING', -- 'PENDING', 'RECONCILED', 'VOID'
    reference_number TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE TABLE transaction_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER REFERENCES transactions (id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts (id),
    category_id INTEGER REFERENCES categories (id),
    amount DECIMAL(20, 8) NOT NULL, -- Positivo (Debe), Negativo (Haber)
    currency_code TEXT REFERENCES currencies (code),
    currency_amount DECIMAL(20, 8), -- Monto en la divisa original si es distinta a la de la cuenta
    memo TEXT,
    reconciled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. ETIQUETAS (Tags)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_tags (
    transaction_id INTEGER REFERENCES transactions (id),
    tag_id INTEGER REFERENCES tags (id),
    PRIMARY KEY (transaction_id, tag_id)
);

-- 8. PRESUPUESTOS
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    category_id INTEGER REFERENCES categories (id),
    amount DECIMAL(20, 8) NOT NULL,
    period TEXT DEFAULT 'MONTHLY', -- 'MONTHLY', 'YEARLY'
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 9. METAS DE AHORRO
CREATE TABLE saving_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    target_amount DECIMAL(20, 8) NOT NULL,
    current_amount DECIMAL(20, 8) DEFAULT 0,
    target_date DATE,
    currency_code TEXT REFERENCES currencies (code),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 10. ACTIVOS (Assets)
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    type TEXT, -- 'Real Estate', 'Vehicle', 'Collection', etc.
    purchase_date DATE,
    purchase_price DECIMAL(20, 8),
    currency_code TEXT REFERENCES currencies (code),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE TABLE asset_valuations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER REFERENCES assets (id) ON DELETE CASCADE,
    valuation_date DATE NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. INVERSIONES (Stocks / Crypto)
CREATE TABLE investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'STOCK', 'CRYPTO', 'BOND', 'ETF'
    currency_code TEXT REFERENCES currencies (code),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE TABLE investment_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investment_id INTEGER REFERENCES investments (id) ON DELETE CASCADE,
    price_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(20, 8) NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE investment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    investment_id INTEGER REFERENCES investments (id),
    account_id INTEGER REFERENCES accounts (id), -- Cuenta desde donde sale/entra dinero
    date TIMESTAMP NOT NULL,
    type TEXT NOT NULL, -- 'BUY', 'SELL', 'DIVIDEND', 'SPLIT'
    quantity DECIMAL(20, 8) NOT NULL,
    price_per_unit DECIMAL(20, 8) NOT NULL,
    commission DECIMAL(20, 8) DEFAULT 0,
    taxes DECIMAL(20, 8) DEFAULT 0,
    total_amount DECIMAL(20, 8) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. SISTEMA DE PLUGINS
CREATE TABLE plugins (
    id TEXT PRIMARY KEY, -- 'telegram_bot', 'dolar_hoy', etc.
    name TEXT NOT NULL,
    version TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    config_json TEXT, -- Configuración serializada
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. METADATOS PERSONALIZADOS (KVP Slots)
CREATE TABLE custom_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    entity_type TEXT NOT NULL, -- 'ACCOUNT', 'TRANSACTION', 'CATEGORY', etc.
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- 'STRING', 'NUMBER', 'DATE', 'BOOLEAN'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE custom_field_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER REFERENCES custom_fields (id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL, -- ID de la fila en la tabla entity_type
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. AUDITORÍA Y NOTIFICACIONES
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    action TEXT NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE', 'AUTH'
    entity_type TEXT,
    entity_id INTEGER,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users (id),
    type TEXT NOT NULL,
    title TEXT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL
);

-- ÍNDICES ESTRATÉGICOS
CREATE INDEX idx_transactions_user_date ON transactions (user_id, date);

CREATE INDEX idx_splits_transaction ON transaction_splits (transaction_id);

CREATE INDEX idx_splits_account ON transaction_splits (account_id);

CREATE INDEX idx_accounts_user_parent ON accounts (user_id, parent_id);

CREATE INDEX idx_categories_user_parent ON categories (user_id, parent_id);

CREATE INDEX idx_investment_prices_date ON investment_prices (investment_id, price_date);

-- DIAGRAMA ERD (Mermaid format for docs)
/*
erDiagram
users ||--o{ accounts : owns
users ||--o{ categories : owns
users ||--o{ transactions : owns
users ||--o{ budgets : sets
users ||--o{ saving_goals : sets
accounts ||--o{ transaction_splits : has
transactions ||--o{ transaction_splits : composed_by
categories ||--o{ transaction_splits : linked_to
transactions }|--|| payees : related_to
transactions ||--o{ tags : labeled_with
investments ||--o{ investment_prices : tracks
investments ||--o{ investment_transactions : history
assets ||--o{ asset_valuations : history
*/