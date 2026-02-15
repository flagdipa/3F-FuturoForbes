"""
Telegram Bot Plugin - Envía notificaciones por Telegram
"""
import aiohttp
from typing import Dict, Any
from backend.plugins.base import BasePlugin


class TelegramBotPlugin(BasePlugin):
    """
    Plugin para enviar notificaciones por Telegram.
    Requiere un bot token y chat_id configurados.
    """
    
    nombre_tecnico = "telegram_bot"
    nombre_display = "Bot de Telegram"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Envía notificaciones por Telegram cuando ocurren eventos importantes"
    hooks = ["transaction_created", "budget_alert", "goal_reached", "daily_summary"]
    
    async def initialize(self):
        """Inicializar el plugin y validar configuración"""
        self.logger.info(f"Inicializando {self.nombre_display}")
        
        # Validar configuración requerida
        self.validate_config(["bot_token", "chat_id"])
        
        # Verificar que las notificaciones estén configuradas
        if not self.get_config("notifications"):
            self.logger.warning("No hay notificaciones configuradas, usando defaults")
            self.config["notifications"] = {
                "transaction_created": True,
                "budget_alert": True,
                "goal_reached": True,
                "daily_summary": False
            }
        
        self.logger.info(f"✅ {self.nombre_display} inicializado correctamente")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info(f"Apagando {self.nombre_display}")
    
    async def on_transaction_created(self, transaction, user):
        """
        Enviar notificación cuando se crea una transacción.
        
        Args:
            transaction: Objeto transacción creada
            user: Usuario que creó la transacción
        """
        if not self._should_notify("transaction_created"):
            return
        
        # Formatear mensaje
        tipo = "💰 Ingreso" if transaction.codigo_transaccion == "Deposit" else "💸 Gasto"
        monto = getattr(transaction, 'monto_transaccion', 0)
        cuenta = getattr(transaction.cuenta, 'nombre_cuenta', 'Cuenta') if hasattr(transaction, 'cuenta') else 'Cuenta'
        categoria = getattr(transaction.categoria, 'nombre_categoria', 'Sin categoría') if hasattr(transaction, 'categoria') else 'Sin categoría'
        
        message = f"""
<b>{tipo}</b>

💵 Monto: ${monto}
🏦 Cuenta: {cuenta}
📁 Categoría: {categoria}
📝 Notas: {getattr(transaction, 'notas', 'N/A')[:50]}...

<i>3F - Futuro Forbes</i>
        """.strip()
        
        await self._send_message(message)
    
    async def on_budget_alert(self, budget, percentage):
        """
        Enviar alerta cuando se excede el presupuesto.
        
        Args:
            budget: Presupuesto excedido
            percentage: Porcentaje de uso
        """
        if not self._should_notify("budget_alert"):
            return
        
        categoria = getattr(budget.categoria, 'nombre_categoria', 'Sin categoría') if hasattr(budget, 'categoria') else 'Sin categoría'
        monto = getattr(budget, 'monto', 0)
        
        message = f"""
⚠️ <b>¡Alerta de Presupuesto!</b>

📁 Categoría: {categoria}
💵 Presupuesto: ${monto}
📊 Uso: {percentage:.1f}%

<i>Has excedido tu presupuesto mensual</i>

3F - Futuro Forbes
        """.strip()
        
        await self._send_message(message)
    
    async def on_goal_reached(self, goal, amount):
        """
        Enviar notificación cuando se alcanza una meta.
        
        Args:
            goal: Meta alcanzada
            amount: Monto actual
        """
        if not self._should_notify("goal_reached"):
            return
        
        nombre = getattr(goal, 'nombre_meta', 'Meta')
        objetivo = getattr(goal, 'monto_objetivo', 0)
        
        message = f"""
🎉 <b>¡Meta Alcanzada!</b>

🎯 Meta: {nombre}
💵 Objetivo: ${objetivo}
💰 Actual: ${amount}

<i>¡Felicitaciones! Has alcanzado tu meta de ahorro</i>

3F - Futuro Forbes
        """.strip()
        
        await self._send_message(message)
    
    async def on_daily_summary(self, user, summary):
        """
        Enviar resumen diario.
        
        Args:
            user: Usuario
            summary: Resumen del día
        """
        if not self._should_notify("daily_summary"):
            return
        
        total_ingresos = summary.get('total_ingresos', 0)
        total_egresos = summary.get('total_egresos', 0)
        balance = total_ingresos - total_egresos
        
        message = f"""
📊 <b>Resumen Diario</b>

💰 Ingresos: ${total_ingresos}
💸 Gastos: ${total_egresos}
📈 Balance: ${balance}

<i>3F - Futuro Forbes</i>
        """.strip()
        
        await self._send_message(message)
    
    def _should_notify(self, notification_type: str) -> bool:
        """
        Verificar si se debe enviar una notificación.
        
        Args:
            notification_type: Tipo de notificación
            
        Returns:
            True si se debe notificar
        """
        notifications = self.get_config("notifications", {})
        return notifications.get(notification_type, False)
    
    async def _send_message(self, text: str):
        """
        Enviar mensaje por Telegram.
        
        Args:
            text: Texto del mensaje (puede incluir HTML)
        """
        token = self.get_config("bot_token")
        chat_id = self.get_config("chat_id")
        
        if not token or not chat_id:
            self.logger.error("Bot token o chat_id no configurados")
            return
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }) as response:
                    if response.status == 200:
                        self.logger.debug(f"Mensaje enviado correctamente a Telegram")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Error enviando mensaje a Telegram: {error_text}")
        except Exception as e:
            self.logger.error(f"Error de conexión con Telegram: {e}")
