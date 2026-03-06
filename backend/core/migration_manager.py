import logging
import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import OperationalError

logger = logging.getLogger("migration_manager")

class MigrationManager:
    """
    Custom migration manager for 3F.
    Supports multi-database dialects (SQLite, PostgreSQL, MySQL).
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine: Engine = create_engine(db_url)
        self.dialect = self.engine.dialect.name
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """Creates the migration log table if it doesn't exist."""
        with self.engine.connect() as conn:
            if self.dialect == 'sqlite':
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS migration_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS migration_log (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            conn.commit()

    def get_applied_migrations(self) -> List[str]:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM migration_log ORDER BY id ASC"))
            return [row[0] for row in result]

    def run_migrations(self, migrations_dir: str):
        """Discover and run pending migrations."""
        applied = self.get_applied_migrations()
        files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py'])

        for filename in files:
            version = filename.split('_')[0]
            if version not in applied:
                self._apply_migration(migrations_dir, filename, version)

    def _apply_migration(self, dir_path: str, filename: str, version: str):
        logger.info(f"Applying migration: {filename}")
        
        # Import the migration module dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location(version, os.path.join(dir_path, filename))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with self.engine.begin() as conn:
            try:
                # Call the 'up' function in the migration file
                module.up(conn, self.dialect)
                
                # Log the migration
                conn.execute(
                    text("INSERT INTO migration_log (version) VALUES (:v)"),
                    {"v": version}
                )
                logger.info(f"Successfully applied {version}")
            except Exception as e:
                logger.error(f"Failed to apply migration {version}: {e}")
                raise

    def rollback(self, version: str, migrations_dir: str):
        """Rollback a specific migration."""
        # Logic for rollback (calling module.down)
        pass
