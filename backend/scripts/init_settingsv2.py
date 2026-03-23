import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.core.database import engine
from sqlmodel import Session, select
from backend.models import SystemConfig

def init_settings():
    with Session(engine) as session:
        # Default settings
        defaults = [
            ("app_name", "3F System"),
            ("company_name", "FuturoForbes"),
            ("currency_base", "USD"),
            ("theme_id", "3f-neon"),
            ("language", "es"),
            ("session_timeout", "30"),
            ("enable_discord_notifications", "false"),
            ("enable_email_notifications", "true"),
            ("security_mode", "standard"),
            ("api_v2_enabled", "true")
        ]
        
        for key, value in defaults:
            existing = session.exec(select(SystemConfig).where(SystemConfig.key == key)).first()
            if not existing:
                print(f"Adding default setting: {key} = {value}")
                config = SystemConfig(key=key, value=value)
                session.add(config)
        
        session.commit()
        print("Default settings initialized successfully.")

if __name__ == '__main__':
    init_settings()
