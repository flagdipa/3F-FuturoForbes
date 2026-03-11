
import asyncio
import logging
import sys
import os

# Add parent directory to path to simulate being in the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.plugin_manager import PluginManager
from backend.core.database import engine

async def test_plugins():
    logging.basicConfig(level=logging.INFO)
    pm = PluginManager(engine)
    
    plugins_to_test = ['criptoya_multi', 'cuentas_wallet']
    
    for pid in plugins_to_test:
        print(f"\n--- Testing plugin: {pid} ---")
        try:
            instance = pm.get_plugin_instance(pid)
            print(f"Instance created: {type(instance)}")
            
            # Simulate activation
            print("Activating...")
            await pm.activate_plugin(pid)
            print("Active plugins:", pm.active_plugins.keys())
            
        except Exception as e:
            print(f"FAIL: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_plugins())
