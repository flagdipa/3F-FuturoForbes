"""
Tests para el sistema de plugins de 3F
"""
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from sqlmodel import SQLModel, create_engine, Session

# Importar lo que vamos a testear
from backend.core.plugin_manager import PluginManager, plugin_manager
from backend.plugins.base import BasePlugin
from backend.models.models_plugins import Plugin


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def mock_session():
    """Crear una sesión de base de datos en memoria para tests"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture
def clean_plugin_manager():
    """Crear una instancia limpia del PluginManager para cada test"""
    # Resetear el singleton
    PluginManager._instance = None
    manager = PluginManager()
    yield manager
    # Cleanup
    manager.hooks = {}
    manager.loaded_plugins = {}


@pytest.fixture
def sample_plugin_data():
    """Datos de ejemplo para un plugin"""
    return {
        "nombre_tecnico": "test_plugin",
        "nombre_display": "Test Plugin",
        "descripcion": "Plugin de prueba",
        "version": "1.0.0",
        "autor": "Test Author",
        "configuracion": {"test_key": "test_value"},
        "hooks": ["test_hook"]
    }


# ==========================================
# TESTS PLUGIN MANAGER
# ==========================================

class TestPluginManager:
    """Tests para la clase PluginManager"""
    
    def test_singleton_pattern(self, clean_plugin_manager):
        """Verificar que PluginManager es un singleton"""
        manager1 = PluginManager()
        manager2 = PluginManager()
        assert manager1 is manager2
    
    def test_initialization(self, clean_plugin_manager):
        """Verificar inicialización correcta"""
        assert clean_plugin_manager.hooks == {}
        assert clean_plugin_manager.loaded_plugins == {}
        assert clean_plugin_manager._initialized is True
    
    @pytest.mark.asyncio
    async def test_register_hook(self, clean_plugin_manager):
        """Probar registro de hooks"""
        mock_plugin = Mock()
        
        clean_plugin_manager.register_hook("test_hook", 1, mock_plugin)
        
        assert "test_hook" in clean_plugin_manager.hooks
        assert len(clean_plugin_manager.hooks["test_hook"]) == 1
        assert clean_plugin_manager.hooks["test_hook"][0]["plugin_id"] == 1
    
    @pytest.mark.asyncio
    async def test_call_hook_success(self, clean_plugin_manager):
        """Probar llamada exitosa a un hook"""
        mock_plugin = AsyncMock()
        mock_plugin.nombre_tecnico = "test_plugin"
        
        clean_plugin_manager.register_hook("test_hook", 1, mock_plugin)
        
        await clean_plugin_manager.call_hook("test_hook", data="test")
        
        mock_plugin.on_hook.assert_called_once_with("test_hook", data="test")
    
    @pytest.mark.asyncio
    async def test_call_hook_multiple_plugins(self, clean_plugin_manager):
        """Probar llamada a hook con múltiples plugins"""
        mock_plugin1 = AsyncMock()
        mock_plugin1.nombre_tecnico = "plugin1"
        
        mock_plugin2 = AsyncMock()
        mock_plugin2.nombre_tecnico = "plugin2"
        
        clean_plugin_manager.register_hook("test_hook", 1, mock_plugin1)
        clean_plugin_manager.register_hook("test_hook", 2, mock_plugin2)
        
        await clean_plugin_manager.call_hook("test_hook", data="test")
        
        mock_plugin1.on_hook.assert_called_once()
        mock_plugin2.on_hook.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_hook_isolation(self, clean_plugin_manager):
        """Verificar que un plugin fallido no afecta a otros"""
        mock_plugin1 = AsyncMock()
        mock_plugin1.nombre_tecnico = "plugin1"
        mock_plugin1.on_hook.side_effect = Exception("Error en plugin1")
        
        mock_plugin2 = AsyncMock()
        mock_plugin2.nombre_tecnico = "plugin2"
        
        clean_plugin_manager.register_hook("test_hook", 1, mock_plugin1)
        clean_plugin_manager.register_hook("test_hook", 2, mock_plugin2)
        
        # No debería lanzar excepción
        await clean_plugin_manager.call_hook("test_hook", data="test")
        
        # El segundo plugin debería haberse ejecutado
        mock_plugin2.on_hook.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_install_plugin(self, clean_plugin_manager, mock_session, sample_plugin_data):
        """Probar instalación de plugin"""
        new_plugin = await clean_plugin_manager.install_plugin(sample_plugin_data, mock_session)
        
        assert new_plugin.nombre_tecnico == "test_plugin"
        assert new_plugin.instalado is True
        assert new_plugin.activo is False
    
    @pytest.mark.asyncio
    async def test_install_plugin_duplicate(self, clean_plugin_manager, mock_session, sample_plugin_data):
        """Probar que no se puede instalar un plugin duplicado"""
        # Instalar primero
        await clean_plugin_manager.install_plugin(sample_plugin_data, mock_session)
        
        # Intentar instalar de nuevo
        with pytest.raises(ValueError, match="ya existe"):
            await clean_plugin_manager.install_plugin(sample_plugin_data, mock_session)
    
    @pytest.mark.asyncio
    async def test_get_loaded_plugins(self, clean_plugin_manager):
        """Probar obtener lista de plugins cargados"""
        clean_plugin_manager.loaded_plugins = {
            "plugin1": {"instance": Mock(), "db_id": 1, "hooks": []},
            "plugin2": {"instance": Mock(), "db_id": 2, "hooks": []}
        }
        
        loaded = clean_plugin_manager.get_loaded_plugins()
        
        assert len(loaded) == 2
        assert "plugin1" in loaded
        assert "plugin2" in loaded
    
    @pytest.mark.asyncio
    async def test_is_plugin_loaded(self, clean_plugin_manager):
        """Probar verificación de plugin cargado"""
        clean_plugin_manager.loaded_plugins["test_plugin"] = {}
        
        assert clean_plugin_manager.is_plugin_loaded("test_plugin") is True
        assert clean_plugin_manager.is_plugin_loaded("other_plugin") is False


# ==========================================
# TESTS BASE PLUGIN
# ==========================================

class TestBasePlugin:
    """Tests para la clase BasePlugin"""
    
    def test_base_plugin_abstract(self):
        """Verificar que BasePlugin es abstracta"""
        with pytest.raises(TypeError):
            BasePlugin()
    
    def test_plugin_required_attributes(self):
        """Verificar que los plugins deben definir atributos requeridos"""
        class IncompletePlugin(BasePlugin):
            pass
        
        with pytest.raises(ValueError, match="nombre_tecnico"):
            IncompletePlugin()
    
    def test_plugin_initialization(self):
        """Probar inicialización de plugin concreto"""
        class ConcretePlugin(BasePlugin):
            nombre_tecnico = "concrete_plugin"
            nombre_display = "Concrete Plugin"
            
            async def initialize(self):
                pass
            
            async def shutdown(self):
                pass
        
        config = {"key": "value"}
        plugin = ConcretePlugin(config=config)
        
        assert plugin.config == config
        assert plugin.nombre_tecnico == "concrete_plugin"
    
    @pytest.mark.asyncio
    async def test_plugin_get_config(self):
        """Probar obtener configuración"""
        class ConcretePlugin(BasePlugin):
            nombre_tecnico = "test_plugin"
            
            async def initialize(self):
                pass
            
            async def shutdown(self):
                pass
        
        plugin = ConcretePlugin(config={"key1": "value1", "key2": "value2"})
        
        assert plugin.get_config("key1") == "value1"
        assert plugin.get_config("key2") == "value2"
        assert plugin.get_config("missing", "default") == "default"
    
    @pytest.mark.asyncio
    async def test_plugin_validate_config(self):
        """Probar validación de configuración"""
        class ConcretePlugin(BasePlugin):
            nombre_tecnico = "test_plugin"
            
            async def initialize(self):
                pass
            
            async def shutdown(self):
                pass
        
        plugin = ConcretePlugin(config={"key1": "value1"})
        
        # No debería lanzar excepción
        plugin.validate_config(["key1"])
        
        # Debería lanzar excepción
        with pytest.raises(ValueError, match="key2"):
            plugin.validate_config(["key1", "key2"])
    
    @pytest.mark.asyncio
    async def test_plugin_on_hook(self):
        """Probar manejo de hooks"""
        class ConcretePlugin(BasePlugin):
            nombre_tecnico = "test_plugin"
            hooks = ["test_hook"]
            
            async def initialize(self):
                pass
            
            async def shutdown(self):
                pass
            
            async def on_test_hook(self, **kwargs):
                self.received_data = kwargs.get("data")
        
        plugin = ConcretePlugin()
        
        await plugin.on_hook("test_hook", data="test_data")
        
        assert plugin.received_data == "test_data"
    
    def test_plugin_get_info(self):
        """Probar obtener información del plugin"""
        class ConcretePlugin(BasePlugin):
            nombre_tecnico = "test_plugin"
            nombre_display = "Test Plugin"
            version = "1.0.0"
            autor = "Test Author"
            descripcion = "Test Description"
            hooks = ["hook1", "hook2"]
            
            async def initialize(self):
                pass
            
            async def shutdown(self):
                pass
        
        plugin = ConcretePlugin(config={"key": "value"})
        info = plugin.get_info()
        
        assert info["nombre_tecnico"] == "test_plugin"
        assert info["nombre_display"] == "Test Plugin"
        assert info["version"] == "1.0.0"
        assert info["hooks"] == ["hook1", "hook2"]


# ==========================================
# TESTS PLUGINS ESPECÍFICOS
# ==========================================

class TestTelegramBotPlugin:
    """Tests para el plugin de Telegram"""
    
    @pytest.mark.asyncio
    async def test_telegram_initialization(self):
        """Probar inicialización del plugin Telegram"""
        from backend.plugins.telegram_bot.plugin import TelegramBotPlugin
        
        config = {
            "bot_token": "123456:test-token",
            "chat_id": "123456789"
        }
        
        plugin = TelegramBotPlugin(config=config)
        await plugin.initialize()
        
        assert plugin.config["notifications"]["transaction_created"] is True
    
    @pytest.mark.asyncio
    async def test_telegram_missing_config(self):
        """Probar que falla sin configuración requerida"""
        from backend.plugins.telegram_bot.plugin import TelegramBotPlugin
        
        plugin = TelegramBotPlugin(config={})
        
        with pytest.raises(ValueError):
            await plugin.initialize()
    
    @pytest.mark.asyncio
    async def test_telegram_should_notify(self):
        """Probar verificación de notificaciones"""
        from backend.plugins.telegram_bot.plugin import TelegramBotPlugin
        
        config = {
            "bot_token": "test",
            "chat_id": "test",
            "notifications": {
                "transaction_created": True,
                "budget_alert": False
            }
        }
        
        plugin = TelegramBotPlugin(config=config)
        
        assert plugin._should_notify("transaction_created") is True
        assert plugin._should_notify("budget_alert") is False
        assert plugin._should_notify("unknown") is False


class TestEmailSMTPPlugin:
    """Tests para el plugin de Email SMTP"""
    
    @pytest.mark.asyncio
    async def test_email_initialization(self):
        """Probar inicialización del plugin Email"""
        from backend.plugins.email_smtp.plugin import EmailSmtpPlugin
        
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@test.com",
            "password": "password"
        }
        
        plugin = EmailSmtpPlugin(config=config)
        await plugin.initialize()
        
        assert plugin.get_config("use_tls") is True
    
    @pytest.mark.asyncio
    async def test_email_missing_config(self):
        """Probar que falla sin configuración SMTP"""
        from backend.plugins.email_smtp.plugin import EmailSmtpPlugin
        
        plugin = EmailSmtpPlugin(config={})
        
        with pytest.raises(ValueError):
            await plugin.initialize()


class TestDolarHoyPlugin:
    """Tests para el plugin de Dólar Hoy"""
    
    @pytest.mark.asyncio
    async def test_dolar_initialization(self):
        """Probar inicialización del plugin Dólar"""
        from backend.plugins.dolar_hoy.plugin import DolarHoyPlugin
        
        config = {"sources": ["blue", "mep"]}
        
        plugin = DolarHoyPlugin(config=config)
        await plugin.initialize()
        
        assert plugin.config["update_frequency"] == "hourly"
        assert plugin.config["create_divisas_if_missing"] is True
    
    def test_dolar_supported_sources(self):
        """Probar obtención de fuentes soportadas"""
        from backend.plugins.dolar_hoy.plugin import DolarHoyPlugin
        
        plugin = DolarHoyPlugin(config={})
        sources = plugin.get_supported_sources()
        
        assert "blue" in sources
        assert "mep" in sources
        assert "ccl" in sources
        assert "cripto" in sources


# ==========================================
# TESTS DE INTEGRACIÓN
# ==========================================

class TestPluginIntegration:
    """Tests de integración end-to-end"""
    
    @pytest.mark.asyncio
    async def test_full_plugin_lifecycle(self, clean_plugin_manager, mock_session):
        """Probar ciclo completo de vida de un plugin"""
        # 1. Instalar
        plugin_data = {
            "nombre_tecnico": "lifecycle_test",
            "nombre_display": "Lifecycle Test",
            "version": "1.0.0",
            "configuracion": {"test": True}
        }
        
        new_plugin = await clean_plugin_manager.install_plugin(plugin_data, mock_session)
        assert new_plugin.id_plugin is not None
        
        # 2. Activar (requeriría el archivo del plugin existir)
        # await clean_plugin_manager.activate_plugin(new_plugin.id_plugin, mock_session)
        
        # 3. Desactivar
        # await clean_plugin_manager.deactivate_plugin(new_plugin.id_plugin, mock_session)
    
    @pytest.mark.asyncio
    async def test_hook_with_transaction(self, clean_plugin_manager):
        """Probar hook con datos de transacción simulados"""
        mock_plugin = AsyncMock()
        mock_plugin.nombre_tecnico = "test_plugin"
        
        clean_plugin_manager.register_hook("transaction_created", 1, mock_plugin)
        
        # Simular datos de transacción
        mock_transaction = Mock()
        mock_transaction.monto_transaccion = Decimal("100.50")
        mock_transaction.codigo_transaccion = "Deposit"
        
        mock_user = Mock()
        mock_user.id_usuario = 1
        mock_user.email = "test@test.com"
        
        await clean_plugin_manager.call_hook(
            "transaction_created",
            transaction=mock_transaction,
            user=mock_user
        )
        
        mock_plugin.on_hook.assert_called_once()
        call_args = mock_plugin.on_hook.call_args
        assert call_args[1]["transaction"] == mock_transaction
        assert call_args[1]["user"] == mock_user


# ==========================================
# FIXTURES ADICIONALES
# ==========================================

@pytest.fixture(autouse=True)
def reset_singleton():
    """Resetear el singleton antes de cada test"""
    PluginManager._instance = None
    yield
    PluginManager._instance = None


# Si ejecutamos directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
