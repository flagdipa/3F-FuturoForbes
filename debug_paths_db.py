
import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = os.path.abspath("c:/xampp/htdocs/3F")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"CWD: {os.getcwd()}")
print(f"Project Root: {project_root}")

LANG_DIR = "frontend/static/js"
abs_lang_dir = os.path.abspath(LANG_DIR)
print(f"LANG_DIR relative: {LANG_DIR}")
print(f"LANG_DIR absolute: {abs_lang_dir}")
print(f"Exists: {os.path.exists(abs_lang_dir)}")

if os.path.exists(abs_lang_dir):
    print("Listing contents:")
    try:
        print(os.listdir(abs_lang_dir))
    except Exception as e:
        print(f"Error listing: {e}")

# Try reading the file
json_path = os.path.join(LANG_DIR, "lang-es.json")
print(f"Trying to read: {json_path}")
try:
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print("Success! JSON loaded.")
        print(f"Keys: {list(data.keys())[:3]}")
except Exception as e:
    print(f"Error reading JSON: {e}")

# Test DB Connection and User
print("\n--- DB TEST ---")
try:
    from backend.core.database import engine
    from sqlmodel import Session, select
    from backend.models.models import Usuario
    from sqlalchemy import text
    
    with Session(engine) as session:
        print("DB Connection OK")
        users = session.exec(select(Usuario)).all()
        print(f"Users found: {len(users)}")
        for u in users:
            print(f"User: {u.email} (ID: {u.id_usuario})")
            
except Exception as e:
    print(f"DB Error: {e}")
