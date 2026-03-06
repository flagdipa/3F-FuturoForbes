from sqlalchemy import text

def up(conn, dialect):
    """
    Initial schema for 3F.
    Uses standard SQL with some dialect adaptations.
    """
    
    # We can split the big SQL file or just execute it if it's compatible
    # For now, let's create the core tables manually in the migration for better control
    
    # 1. Users
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
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
        )
    """))

    # 2. Currencies
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS currencies (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            symbol TEXT,
            decimal_places INTEGER DEFAULT 2,
            is_base BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """))

    # 3. Accounts
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            parent_id INTEGER NULL REFERENCES accounts(id),
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            currency_code TEXT REFERENCES currencies(code),
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
        )
    """))

    # 4. Categories
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            parent_id INTEGER NULL REFERENCES categories(id),
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            color TEXT,
            icon TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """))

    # 5. Transactions
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            date TIMESTAMP NOT NULL,
            description TEXT,
            payee_id INTEGER,
            status TEXT DEFAULT 'PENDING',
            reference_number TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """))

    # 6. Splits
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transaction_splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
            account_id INTEGER REFERENCES accounts(id),
            category_id INTEGER REFERENCES categories(id),
            amount DECIMAL(20, 8) NOT NULL,
            currency_code TEXT REFERENCES currencies(code),
            currency_amount DECIMAL(20, 8),
            memo TEXT,
            reconciled BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

def down(conn, dialect):
    conn.execute(text("DROP TABLE transaction_splits"))
    conn.execute(text("DROP TABLE transactions"))
    conn.execute(text("DROP TABLE categories"))
    conn.execute(text("DROP TABLE accounts"))
    conn.execute(text("DROP TABLE currencies"))
    conn.execute(text("DROP TABLE users"))
