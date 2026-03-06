"""
Generador de configuración para la instalación de 3F
"""
import secrets
from pathlib import Path
from typing import Dict
from datetime import datetime


def generate_secret_key(length: int = 64) -> str:
    return secrets.token_hex(length // 2)


def validate_config(config: Dict[str, str]) -> Dict[str, any]:
    required = ["DATABASE_URL", "SECRET_KEY"]
    missing = [f for f in required if not config.get(f)]
    if missing:
        return {"valid": False, "error": f"Missing config: {', '.join(missing)}"}
    return {"valid": True}


def backup_existing_env():
    env_path = Path(".env")
    if env_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(f".env.backup_{timestamp}")
        env_path.rename(backup_path)
        return str(backup_path)
    return None


def create_env_file(config: Dict[str, str]) -> Dict[str, any]:
    try:
        env_content = f"""# Configuración 3F - Generada por el Wizard
# Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DATABASE_URL={config.get('DATABASE_URL')}
SECRET_KEY={config.get('SECRET_KEY')}
PORT={config.get('PORT', '8000')}
HOST={config.get('HOST', '0.0.0.0')}
DEBUG_MODE={config.get('DEBUG_MODE', 'False')}
"""
        Path(".env").write_text(env_content, encoding='utf-8')
        return {"success": True, "message": ".env file created successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error creating .env: {str(e)}"}
