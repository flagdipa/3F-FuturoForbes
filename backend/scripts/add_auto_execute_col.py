import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.database import engine

def migrate():
    with engine.connect() as connection:
        try:
            # Check if column exists (simple try/except for SQLite/MySQL agnostic approach mostly)
            # For MySQL specifically:
            print("Attempting to add 'auto_execute' column...")
            connection.execute(text("ALTER TABLE transacciones_programadas ADD COLUMN auto_execute BOOLEAN DEFAULT 1"))
            print("Column added successfully.")
        except Exception as e:
            print(f"Migration failed (might already exist): {e}")

if __name__ == "__main__":
    migrate()
