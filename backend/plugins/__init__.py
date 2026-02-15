"""
Plugins package - Sistema de plugins para 3F
"""
from .base import BasePlugin
from backend.core.plugin_manager import plugin_manager

__all__ = ["BasePlugin", "plugin_manager"]
