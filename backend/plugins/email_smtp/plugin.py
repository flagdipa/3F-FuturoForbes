"""
Email SMTP Plugin - Envía notificaciones por email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from backend.plugins.base import BasePlugin


class EmailSmtpPlugin(BasePlugin):
    """
    Plugin para enviar notificaciones por email usando SMTP.
    Compatible con Gmail, Outlook, SendGrid, Mailgun, etc.
    """
    
    nombre_tecnico = "email_smtp"
    nombre_display = "Email SMTP"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Envía notificaciones por email usando SMTP"
    hooks = ["transaction_created", "budget_alert", "goal_reached", "login_attempt"]
    
    async def initialize(self):
        """Inicializar el plugin y validar configuración"""
        self.logger.info(f"Inicializando {self.nombre_display}")
        
        # Validar configuración requerida
        self.validate_config(["smtp_host", "smtp_port", "username", "password"])
        
        # Configurar defaults
        if "use_tls" not in self.config:
            self.config["use_tls"] = True
        
        if "from_email" not in self.config:
            self.config["from_email"] = self.config["username"]
        
        if not self.get_config("notifications"):
            self.config["notifications"] = {
                "transaction_created": True,
                "budget_alert": True,
                "goal_reached": True,
                "login_attempt": True
            }
        
        self.logger.info(f"✅ {self.nombre_display} inicializado correctamente")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info(f"Apagando {self.nombre_display}")
    
    async def on_transaction_created(self, transaction, user):
        """Notificar cuando se crea una transacción"""
        if not self._should_notify("transaction_created"):
            return
        
        tipo = "Ingreso" if transaction.codigo_transaccion == "Deposit" else "Gasto"
        monto = getattr(transaction, 'monto_transaccion', 0)
        
        subject = f"[{tipo}] Nueva transacción de ${monto}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #667eea;">Nueva Transacción</h2>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Tipo:</strong> {tipo}</p>
                <p><strong>Monto:</strong> ${monto}</p>
                <p><strong>Cuenta:</strong> {getattr(transaction.cuenta, 'nombre_cuenta', 'N/A') if hasattr(transaction, 'cuenta') else 'N/A'}</p>
                <p><strong>Categoría:</strong> {getattr(transaction.categoria, 'nombre_categoria', 'Sin categoría') if hasattr(transaction, 'categoria') else 'Sin categoría'}</p>
                <p><strong>Notas:</strong> {getattr(transaction, 'notas', 'N/A')}</p>
            </div>
            
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático de 3F - Futuro Forbes
            </p>
        </body>
        </html>
        """
        
        await self._send_email(subject, body)
    
    async def on_budget_alert(self, budget, percentage):
        """Notificar cuando se excede el presupuesto"""
        if not self._should_notify("budget_alert"):
            return
        
        categoria = getattr(budget.categoria, 'nombre_categoria', 'Sin categoría') if hasattr(budget, 'categoria') else 'Sin categoría'
        
        subject = f"⚠️ Alerta: Has excedido tu presupuesto de {categoria}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #dc3545;">⚠️ Alerta de Presupuesto</h2>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p><strong>Categoría:</strong> {categoria}</p>
                <p><strong>Presupuesto:</strong> ${getattr(budget, 'monto', 0)}</p>
                <p><strong>Uso actual:</strong> {percentage:.1f}%</p>
                <p><strong>Estado:</strong> <span style="color: #dc3545; font-weight: bold;">EXCEDIDO</span></p>
            </div>
            
            <p>Te recomendamos revisar tus gastos en esta categoría para mantener tu presupuesto mensual.</p>
            
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático de 3F - Futuro Forbes
            </p>
        </body>
        </html>
        """
        
        await self._send_email(subject, body)
    
    async def on_goal_reached(self, goal, amount):
        """Notificar cuando se alcanza una meta"""
        if not self._should_notify("goal_reached"):
            return
        
        nombre = getattr(goal, 'nombre_meta', 'Meta')
        objetivo = getattr(goal, 'monto_objetivo', 0)
        
        subject = f"🎉 ¡Felicitaciones! Has alcanzado tu meta: {nombre}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #28a745;">🎉 ¡Meta Alcanzada!</h2>
            
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <p><strong>Meta:</strong> {nombre}</p>
                <p><strong>Monto objetivo:</strong> ${objetivo}</p>
                <p><strong>Monto actual:</strong> ${amount}</p>
                <p><strong>Progreso:</strong> 100% ✓</p>
            </div>
            
            <p>¡Excelente trabajo! Has logrado tu meta de ahorro. Sigue así para alcanzar tus próximos objetivos financieros.</p>
            
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático de 3F - Futuro Forbes
            </p>
        </body>
        </html>
        """
        
        await self._send_email(subject, body)
    
    async def on_login_attempt(self, user, ip, success):
        """Notificar intentos de login desde nuevas IPs"""
        if not self._should_notify("login_attempt"):
            return
        
        # Solo notificar logins exitosos desde IPs nuevas o fallidos
        if success:
            # Aquí se podría verificar si es una IP conocida
            return
        
        subject = "🚨 Alerta de Seguridad: Intento de acceso fallido"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #dc3545;">🚨 Alerta de Seguridad</h2>
            
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <p><strong>Evento:</strong> Intento de login fallido</p>
                <p><strong>Usuario:</strong> {getattr(user, 'email', 'N/A')}</p>
                <p><strong>IP:</strong> {ip}</p>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Estado:</strong> <span style="color: #dc3545; font-weight: bold;">FALLIDO</span></p>
            </div>
            
            <p>Si no fuiste tú quien intentó acceder, te recomendamos cambiar tu contraseña inmediatamente.</p>
            
            <p style="color: #666; font-size: 12px;">
                Este es un mensaje automático de 3F - Futuro Forbes
            </p>
        </body>
        </html>
        """
        
        await self._send_email(subject, body)
    
    def _should_notify(self, notification_type: str) -> bool:
        """Verificar si se debe enviar una notificación"""
        notifications = self.get_config("notifications", {})
        return notifications.get(notification_type, False)
    
    async def _send_email(self, subject: str, body: str):
        """
        Enviar email usando SMTP.
        
        Args:
            subject: Asunto del email
            body: Cuerpo HTML del email
        """
        smtp_host = self.get_config("smtp_host")
        smtp_port = self.get_config("smtp_port")
        username = self.get_config("username")
        password = self.get_config("password")
        use_tls = self.get_config("use_tls", True)
        from_email = self.get_config("from_email", username)
        to_email = self.get_config("to_email", username)
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adjuntar cuerpo HTML
            msg.attach(MIMEText(body, 'html'))
            
            # Conectar y enviar
            server = smtplib.SMTP(smtp_host, smtp_port)
            
            if use_tls:
                server.starttls()
            
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            self.logger.debug(f"Email enviado: {subject}")
            
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            raise


# Import necesario para el hook de login
from datetime import datetime
