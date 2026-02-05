"""
Database Migration: Create user_layouts table
Run this script to create the table for storing GridStack layouts
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import SQLModel, create_engine
from backend.core.config import settings
from backend.models.models_layouts import UserLayout

def create_layouts_table():
    """Create user_layouts table"""
    engine = create_engine(settings.DATABASE_URL, echo=True)
   
    print("Creating user_layouts table...")
    SQLModel.metadata.create_all(engine, tables=[UserLayout.__table__])
    print("✅ user_layouts table created successfully!")

if __name__ == "__main__":
    try:
        create_layouts_table()
    except Exception as e:
        print(f"❌ Error creating table: {e}")
