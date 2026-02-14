"""
Utilidad para verificar el estado de instalación del sistema 3F
"""
from pathlib import Path
import os
from dotenv import load_dotenv


def is_installed() -> bool:
    """
    Verifica si el sistema está instalado correctamente
    
    Comprueba:
    - Existencia del archivo .env
    - Existencia del archivo .installed
    - Configuración válida en .env (DATABASE_URL y SECRET_KEY)
    
    Returns:
        True si el sistema está instalado, False en caso contrario
    """
    # Verificar archivo .installed (marca definitiva de instalación completa)
    installed_marker = Path(".installed")
    if not installed_marker.exists():
        return False
    
    # Verificar archivo .env
    env_path = Path(".env")
    if not env_path.exists():
        return False
    
    # Cargar variables de entorno
    try:
        load_dotenv()
        
        # Verificar variables críticas
        database_url = os.getenv("DATABASE_URL")
        secret_key = os.getenv("SECRET_KEY")
        
        if not database_url or not secret_key:
            return False
        
        # Verificar formato mínimo de DATABASE_URL
        if "://" not in database_url:
            return False
        
        return True
    
    except Exception:
        return False


def mark_as_installed() -> bool:
    """
    Marca el sistema como instalado creando el archivo .installed
    
    Returns:
        True si se creó el archivo correctamente, False en caso contrario
    """
    try:
        installed_marker = Path(".installed")
        
        # Escribir información de instalación
        from datetime import datetime
        install_info = f"""FuturoForbes 3F - Sistema Instalado
Fecha de Instalación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Wizard Version: 1.0.0

IMPORTANTE: No eliminar este archivo. El sistema lo usa para verificar que está instalado correctamente.
"""
        installed_marker.write_text(install_info, encoding='utf-8')
        
        return True
    
    except Exception as e:
        print(f"Error creating .installed file: {e}")
        return False


def is_install_folder_present() -> bool:
    """
    Verifica si la carpeta /install aún existe
    
    Después de una instalación exitosa, esta carpeta debería eliminarse
    por razones de seguridad.
    
    Returns:
        True si la carpeta existe, False en caso contrario
    """
    install_folder = Path("install")
    return install_folder.exists() and install_folder.is_dir()


def get_installation_info() -> dict:
    """
    Obtiene información sobre la instalación
    
    Returns:
        Dict con información de la instalación o None si no está instalado
    """
    if not is_installed():
        return None
    
    try:
        installed_marker = Path(".installed")
        info_text = installed_marker.read_text(encoding='utf-8')
        
        # Extraer fecha de instalación del contenido
        lines = info_text.split('\n')
        install_date = None
        for line in lines:
            if "Fecha de Instalación:" in line:
                install_date = line.split(":", 1)[1].strip()
                break
        
        return {
            "installed": True,
            "install_date": install_date,
            "env_exists": Path(".env").exists(),
            "install_folder_exists": is_install_folder_present()
        }
    
    except Exception:
        return {
            "installed": True,
            "install_date": "Unknown",
            "env_exists": Path(".env").exists(),
            "install_folder_exists": is_install_folder_present()
        }


def rename_install_folder() -> dict:
    """
    Renombra la carpeta /install con un sufijo aleatorio por seguridad.
    Similar al comportamiento de PrestaShop.
    """
    import secrets
    import shutil
    
    try:
        install_folder = Path("install")
        if not install_folder.exists():
            return {"success": True, "message": "No install folder to rename", "renamed": False}
            
        suffix = secrets.token_hex(4)
        new_name = f"install_{suffix}"
        install_folder.rename(new_name)
        
        return {
            "success": True, 
            "message": f"Folder renamed to {new_name}", 
            "new_name": new_name,
            "renamed": True
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
def is_install_blocked() -> bool:
    """
    Verifica si el acceso al sistema debe estar bloqueado por seguridad.
    
    Bloquea si:
    - El sistema está marcado como instalado
    - PERO la carpeta /install todavía existe
    """
    return is_installed() and is_install_folder_present()
