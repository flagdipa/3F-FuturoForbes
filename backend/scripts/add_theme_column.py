"""
Add theme_preference column to usuarios table
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import create_engine, text
from backend.core.config import settings

def add_theme_column():
    """Add theme_preference column to usuarios table"""
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'usuarios' 
                AND COLUMN_NAME = 'theme_preference'
            """))
            exists = result.fetchone()[0] > 0
            
            if exists:
                print("✅ Column theme_preference already exists!")
            else:
                # Add column
                conn.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN theme_preference VARCHAR(50) DEFAULT 'dark_neon'
                """))
                conn.commit()
                print("✅ Column theme_preference added successfully!")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_theme_column()
