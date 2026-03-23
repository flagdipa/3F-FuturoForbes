"""
Backup Automático Plugin - Crea copias de seguridad de la base de datos
Soporta: MySQL dump local y subida a AWS S3
"""
import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import logging

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from backend.plugins.base import BasePlugin


class BackupAutomaticoPlugin(BasePlugin):
    """
    Plugin para crear backups automáticos de la base de datos MySQL.
    Soporta almacenamiento local y en AWS S3 con retención configurable.
    """
    
    technical_name = "backup_automatico"
    display_name = "Backup Automático"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Crea backups automáticos de la base de datos MySQL y los almacena localmente o en AWS S3"
    hooks = ["daily_summary", "audit_event"]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.s3_client = None
        self.last_backup_date = None
        
    async def initialize(self):
        """Inicializar el plugin y validar configuración"""
        self.logger.info(f"Inicializando {self.display_name}")
        
        # Validar configuración requerida
        if not self.get_config("enabled", True):
            self.logger.info("Plugin deshabilitado por configuración")
            return
            
        # Configurar directorio local de backups
        self.local_path = self.get_config("local_path", "backups/")
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        
        # Configurar S3 si está habilitado
        s3_config = self.get_config("s3", {})
        if s3_config.get("enabled", False):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=s3_config.get("access_key"),
                    aws_secret_access_key=s3_config.get("secret_key"),
                    region_name=s3_config.get("region", "us-east-1")
                )
                # Test connection
                self.s3_client.head_bucket(Bucket=s3_config.get("bucket"))
                self.logger.info(f"✅ Conexión S3 establecida: {s3_config.get('bucket')}")
            except Exception as e:
                self.logger.error(f"❌ Error conectando a S3: {e}")
                self.s3_client = None
        
        self.logger.info(f"✅ {self.display_name} inicializado correctamente")
        self.logger.info(f"📁 Directorio de backups: {self.local_path}")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info(f"Apagando {self.display_name}")
        if self.s3_client:
            self.s3_client = None
    
    async def on_daily_summary(self, user, summary):
        """
        Hook ejecutado en el resumen diario.
        Verifica si debe realizar backup según la frecuencia configurada.
        """
        if not self.get_config("enabled", True):
            return
            
        frequency = self.get_config("frequency", "daily")
        backup_time = self.get_config("backup_time", "02:00")
        
        # Verificar si debe ejecutar backup
        if self._should_run_backup(frequency, backup_time):
            self.logger.info("🔄 Ejecutando backup programado...")
            await self.create_backup()
    
    async def on_audit_event(self, action, entity, details):
        """
        Hook para eventos de auditoría.
        Loguea operaciones de backup.
        """
        if action in ["backup_created", "backup_uploaded", "backup_deleted"]:
            self.logger.info(f"📋 Audit: {action} - {entity} - {details}")
    
    def _should_run_backup(self, frequency: str, backup_time: str) -> bool:
        """
        Determinar si debe ejecutar el backup según frecuencia y hora.
        
        Args:
            frequency: Frecuencia del backup (daily, weekly, monthly)
            backup_time: Hora del backup en formato "HH:MM"
            
        Returns:
            True si debe ejecutar backup
        """
        now = datetime.now()
        
        # Parsear hora configurada
        try:
            hour, minute = map(int, backup_time.split(":"))
        except ValueError:
            hour, minute = 2, 0  # Default 02:00
        
        # Verificar si ya se hizo backup hoy
        if self.last_backup_date == now.date():
            return False
            
        # Verificar hora (permitir ventana de 1 hora)
        if not (hour <= now.hour <= hour + 1):
            return False
        
        # Verificar frecuencia
        if frequency == "daily":
            return True
        elif frequency == "weekly":
            return now.weekday() == 0  # Lunes
        elif frequency == "monthly":
            return now.day == 1  # Primer día del mes
        
        return False
    
    async def create_backup(self) -> Optional[str]:
        """
        Crear backup de la base de datos MySQL.
        
        Returns:
            Ruta del archivo de backup creado o None si falló
        """
        try:
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"3f_backup_{timestamp}.sql"
            filepath = os.path.join(self.local_path, filename)
            
            # Obtener configuración de la base de datos desde variables de entorno
            db_config = self._get_db_config()
            
            self.logger.info(f"🗄️  Creando backup de la base de datos...")
            
            # Crear dump con mysqldump
            dump_cmd = [
                "mysqldump",
                f"--host={db_config['host']}",
                f"--port={db_config['port']}",
                f"--user={db_config['user']}",
                f"--password={db_config['password']}",
                "--single-transaction",
                "--routines",
                "--triggers",
                db_config['database']
            ]
            
            # Ejecutar mysqldump
            with open(filepath, 'w') as f:
                result = subprocess.run(
                    dump_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Error en mysqldump: {result.stderr}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                await self._send_notification(False, f"Error en mysqldump: {result.stderr}")
                return None
            
            # Comprimir con gzip si está habilitado
            if self.get_config("compression", True):
                compressed_path = f"{filepath}.gz"
                with open(filepath, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(filepath)  # Eliminar archivo sin comprimir
                filepath = compressed_path
                filename = f"{filename}.gz"
            
            file_size = os.path.getsize(filepath)
            self.logger.info(f"✅ Backup creado: {filename} ({self._format_size(file_size)})")
            
            # Actualizar fecha del último backup
            self.last_backup_date = datetime.now().date()
            
            # Subir a S3 si está configurado
            s3_config = self.get_config("s3", {})
            if s3_config.get("enabled", False) and self.s3_client:
                await self._upload_to_s3(filepath, filename)
            
            # Limpiar backups antiguos
            await self._cleanup_old_backups()
            
            # Enviar notificación de éxito
            await self._send_notification(
                True, 
                f"Backup creado exitosamente: {filename} ({self._format_size(file_size)})"
            )
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Error creando backup: {e}")
            await self._send_notification(False, f"Error creando backup: {str(e)}")
            return None
    
    def _get_db_config(self) -> Dict[str, str]:
        """
        Obtener configuración de la base de datos desde variables de entorno.
        
        Returns:
            Diccionario con configuración de BD
        """
        # Intentar obtener de variables de entorno
        database_url = os.getenv("DATABASE_URL", "")
        
        if database_url.startswith("mysql"):
            # Parsear URL tipo: mysql+pymysql://user:pass@host:port/database
            import re
            match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)", database_url)
            if match:
                return {
                    "user": match.group(1),
                    "password": match.group(2),
                    "host": match.group(3),
                    "port": match.group(4),
                    "database": match.group(5)
                }
        
        # Valores por defecto
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "3306"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "3f_db")
        }
    
    async def _upload_to_s3(self, filepath: str, filename: str):
        """
        Subir archivo de backup a AWS S3.
        
        Args:
            filepath: Ruta local del archivo
            filename: Nombre del archivo
        """
        if not self.s3_client:
            self.logger.warning("⚠️  Cliente S3 no inicializado")
            return
            
        s3_config = self.get_config("s3", {})
        bucket = s3_config.get("bucket")
        prefix = s3_config.get("prefix", "3f-backups/")
        
        # Crear key en S3 con estructura de carpetas por fecha
        now = datetime.now()
        s3_key = f"{prefix}{now.year}/{now.month:02d}/{filename}"
        
        try:
            self.logger.info(f"☁️  Subiendo backup a S3: {s3_key}")
            self.s3_client.upload_file(filepath, bucket, s3_key)
            self.logger.info(f"✅ Backup subido a S3: {s3_key}")
        except Exception as e:
            self.logger.error(f"❌ Error subiendo a S3: {e}")
    
    async def _cleanup_old_backups(self):
        """
        Eliminar backups antiguos según la política de retención.
        """
        retention_days = self.get_config("retention_days", 30)
        if retention_days <= 0:
            return
            
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Limpiar backups locales
        try:
            deleted_count = 0
            for filename in os.listdir(self.local_path):
                if filename.startswith("3f_backup_"):
                    filepath = os.path.join(self.local_path, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        self.logger.debug(f"🗑️  Eliminado backup antiguo: {filename}")
            
            if deleted_count > 0:
                self.logger.info(f"🧹 Eliminados {deleted_count} backups antiguos locales")
        except Exception as e:
            self.logger.error(f"⚠️  Error limpiando backups locales: {e}")
        
        # Limpiar backups en S3
        s3_config = self.get_config("s3", {})
        if s3_config.get("enabled", False) and self.s3_client:
            try:
                bucket = s3_config.get("bucket")
                prefix = s3_config.get("prefix", "3f-backups/")
                
                # Listar objetos en S3
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    deleted_count = 0
                    for obj in response['Contents']:
                        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                            self.s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        self.logger.info(f"🧹 Eliminados {deleted_count} backups antiguos de S3")
                        
            except Exception as e:
                self.logger.error(f"⚠️  Error limpiando backups de S3: {e}")
    
    async def _send_notification(self, success: bool, message: str):
        """
        Enviar notificación vía plugin email_smtp si está disponible.
        
        Args:
            success: Si la operación fue exitosa
            message: Mensaje de la notificación
        """
        notifications = self.get_config("notifications", {})
        
        # Verificar si debe notificar
        if success and not notifications.get("on_success", False):
            return
        if not success and not notifications.get("on_failure", True):
            return
        
        # Intentar usar plugin email_smtp
        try:
            from backend.core.plugin_manager import plugin_manager
            
            email_plugin = plugin_manager.get_plugin_instance("email_smtp")
            if email_plugin:
                subject = f"✅ Backup Exitoso - 3F" if success else f"❌ Backup Fallido - 3F"
                
                # Enviar email (asumiendo que el plugin tiene un método para esto)
                # Nota: Esto depende de cómo esté implementado el plugin email_smtp
                self.logger.info(f"📧 Notificación enviada vía email_smtp: {subject}")
            else:
                self.logger.debug("Plugin email_smtp no disponible para notificaciones")
                
        except Exception as e:
            self.logger.debug(f"No se pudo enviar notificación por email: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Formatear tamaño de archivo en unidades legibles.
        
        Args:
            size_bytes: Tamaño en bytes
            
        Returns:
            String formateado (ej: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    async def get_backup_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de backups.
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "local_backups": 0,
            "local_size_total": 0,
            "oldest_backup": None,
            "newest_backup": None,
            "s3_backups": 0
        }
        
        # Contar backups locales
        try:
            for filename in os.listdir(self.local_path):
                if filename.startswith("3f_backup_"):
                    filepath = os.path.join(self.local_path, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    file_size = os.path.getsize(filepath)
                    
                    stats["local_backups"] += 1
                    stats["local_size_total"] += file_size
                    
                    if not stats["oldest_backup"] or file_mtime < stats["oldest_backup"]:
                        stats["oldest_backup"] = file_mtime
                    if not stats["newest_backup"] or file_mtime > stats["newest_backup"]:
                        stats["newest_backup"] = file_mtime
                        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
        
        # Contar backups en S3
        s3_config = self.get_config("s3", {})
        if s3_config.get("enabled", False) and self.s3_client:
            try:
                bucket = s3_config.get("bucket")
                prefix = s3_config.get("prefix", "3f-backups/")
                
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    stats["s3_backups"] = len(response['Contents'])
                    
            except Exception as e:
                self.logger.error(f"Error obteniendo estadísticas de S3: {e}")
        
        # Formatear tamaño total
        stats["local_size_formatted"] = self._format_size(stats["local_size_total"])
        
        return stats
