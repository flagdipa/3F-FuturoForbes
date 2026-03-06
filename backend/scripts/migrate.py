import sys
import os
import argparse
from sqlalchemy import create_engine
from core.migration_manager import MigrationManager

# Include path to backend for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser(description="3F Database Migration Tool")
    parser.add_argument("command", choices=["up", "status", "rollback"], help="Command to execute")
    parser.add_argument("--db", default="sqlite:///3f_dev.db", help="Database URL")
    
    args = parser.parse_args()
    
    # In production, this would come from an environment variable
    db_url = os.getenv("DATABASE_URL", args.db)
    
    manager = MigrationManager(db_url)
    migrations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations")
    
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)

    if args.command == "up":
        print(f"Running migrations on {manager.dialect}...")
        manager.run_migrations(migrations_dir)
        print("Done.")
    elif args.command == "status":
        applied = manager.get_applied_migrations()
        print(f"Applied migrations: {len(applied)}")
        for m in applied:
            print(f" - {m}")
            
if __name__ == "__main__":
    main()
