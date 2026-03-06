"""
Verificador de requisitos del sistema para la instalación de 3F
"""
import sys
import os
import importlib.util
from typing import Dict, List
from pathlib import Path


def check_python_version() -> Dict[str, any]:
    """
    Verifica que la versión de Python sea >= 3.9
    """
    current_version = sys.version_info
    required_version = (3, 9)
    
    version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
    required_str = f"{required_version[0]}.{required_version[1]}"
    
    is_valid = current_version >= required_version
    
    return {
        "requirement": "Python Version",
        "status": "ok" if is_valid else "error",
        "current": version_str,
        "required": f">= {required_str}",
        "message": "Python version is compatible" if is_valid else f"Python {required_str}+ is required"
    }


def check_database_drivers() -> Dict[str, any]:
    """
    Verifica la disponibilidad de drivers de base de datos
    """
    drivers = {
        "pymysql": False,
        "psycopg2": False
    }
    
    if importlib.util.find_spec("pymysql") is not None:
        drivers["pymysql"] = True
    if importlib.util.find_spec("psycopg2") is not None:
        drivers["psycopg2"] = True
    
    has_any_driver = drivers["pymysql"] or drivers["psycopg2"]
    
    available = []
    if drivers["pymysql"]:
        available.append("MySQL (pymysql)")
    if drivers["psycopg2"]:
        available.append("PostgreSQL (psycopg2)")
    
    return {
        "requirement": "Database Drivers",
        "status": "ok" if has_any_driver else "error",
        "current": ", ".join(available) if available else "None",
        "required": "pymysql or psycopg2",
        "message": "Database drivers available" if has_any_driver else "No database drivers found",
        "details": drivers
    }


def check_write_permissions() -> Dict[str, any]:
    """
    Verifica permisos de escritura en directorios críticos
    """
    root_path = Path.cwd()
    critical_dirs = [
        root_path,
        root_path / "uploads",
        root_path / "attachments",
        root_path / "logs",
        root_path / "backups"
    ]
    
    permissions_ok = True
    issues = []
    
    for dir_path in critical_dirs:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                permissions_ok = False
                issues.append(f"Cannot create {dir_path.name}")
                continue
        
        test_file = dir_path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            permissions_ok = False
            issues.append(f"No write permission in {dir_path.name}")
    
    return {
        "requirement": "Write Permissions",
        "status": "ok" if permissions_ok else "error",
        "current": "All directories writable" if permissions_ok else f"Issues: {', '.join(issues)}",
        "required": "Write access to core directories",
        "message": "All required directories are writable" if permissions_ok else "Some directories are not writable",
        "details": {"issues": issues} if issues else {}
    }


def check_required_packages() -> Dict[str, any]:
    """
    Verifica que los paquetes Python necesarios estén instalados
    """
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "sqlmodel": "sqlmodel",
        "pydantic": "pydantic",
        "bcrypt": "bcrypt",
        "python-jose": "jose",
        "python-multipart": "multipart",
        "jinja2": "jinja2",
        "python-dotenv": "dotenv"
    }
    
    missing = []
    installed = []
    for package_name, import_name in required_packages.items():
        if importlib.util.find_spec(import_name) is not None:
            installed.append(package_name)
        else:
            missing.append(package_name)
    
    all_installed = len(missing) == 0
    return {
        "requirement": "Required Packages",
        "status": "ok" if all_installed else "error",
        "current": f"{len(installed)}/{len(required_packages)} installed",
        "required": "All required Python packages",
        "message": "All packages installed" if all_installed else f"Missing: {', '.join(missing)}",
        "details": {"installed": installed, "missing": missing}
    }


def get_system_info() -> Dict[str, str]:
    import platform
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "architecture": platform.machine()
    }


def run_all_checks() -> Dict[str, any]:
    checks = [
        check_python_version(),
        check_database_drivers(),
        check_write_permissions(),
        check_required_packages()
    ]
    all_passed = all(check["status"] == "ok" for check in checks)
    return {
        "all_passed": all_passed,
        "checks": checks,
        "system_info": get_system_info()
    }
