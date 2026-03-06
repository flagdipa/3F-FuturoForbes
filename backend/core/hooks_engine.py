import asyncio
import logging
import functools
from typing import Dict, List, Any, Callable, Optional, Union
from inspect import iscoroutinefunction

logger = logging.getLogger("hooks_engine")

class HookListener:
    def __init__(self, callback: Callable, priority: int = 10, plugin_id: Optional[str] = None):
        self.callback = callback
        self.priority = priority
        self.plugin_id = plugin_id

    def __repr__(self):
        return f"<HookListener {self.callback.__name__} priority={self.priority}>"

class HooksEngine:
    """
    Central engine for managing hooks and events in 3F.
    Supports priorities and async dispatch.
    """
    _instance = None
    _listeners: Dict[str, List[HookListener]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HooksEngine, cls).__new__(cls)
            cls._listeners = {}
        return cls._instance

    def register(self, hook_name: str, callback: Callable, priority: int = 10, plugin_id: Optional[str] = None):
        """Register a new listener for a hook."""
        if hook_name not in self._listeners:
            self._listeners[hook_name] = []
        
        listener = HookListener(callback, priority, plugin_id)
        self._listeners[hook_name].append(listener)
        
        # Sort by priority (lower number = higher priority)
        self._listeners[hook_name].sort(key=lambda x: x.priority)
        logger.debug(f"Registered hook '{hook_name}': {callback.__name__} (Priority: {priority})")

    async def dispatch(self, hook_name: str, **kwargs) -> List[Any]:
        """
        Dispatch a hook and return the results from all listeners.
        Execution is sequential based on priority.
        """
        results = []
        if hook_name not in self._listeners:
            return results

        logger.debug(f"Dispatching hook '{hook_name}' with {len(self._listeners[hook_name])} listeners.")

        for listener in self._listeners[hook_name]:
            try:
                if iscoroutinefunction(listener.callback):
                    res = await listener.callback(**kwargs)
                else:
                    res = listener.callback(**kwargs)
                results.append(res)
            except Exception as e:
                logger.error(f"Error in hook listener '{hook_name}' -> {listener.callback.__name__}: {e}")
        
        return results

# --- DECORATORS ---

def hook_listener(hook_name: str, priority: int = 10):
    """Decorator to register a function as a hook listener."""
    def decorator(func):
        # The actual registration usually happens during plugin loading
        # but we mark the function with metadata here.
        func._hook_name = hook_name
        func._hook_priority = priority
        return func
    return decorator

def hook_dispatch(hook_name: str):
    """
    Decorator to wrap a core function and dispatch a hook before and after.
    Example:
    @hook_dispatch("TransactionCreated")
    def create_transaction(...): ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            engine = HooksEngine()
            
            # Action Before
            await engine.dispatch(f"before_{hook_name}", **kwargs)
            
            # Execute original function (must be async)
            if iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Action After
            kwargs['result'] = result
            await engine.dispatch(f"after_{hook_name}", **kwargs)
            
            return result
        return wrapper
    return decorator

# --- GLOBAL UTILS ---

async def dispatch_hook(hook_name: str, **kwargs):
    """Global utility to dispatch a hook."""
    return await HooksEngine().dispatch(hook_name, **kwargs)

def register_hook(hook_name: str, callback: Callable, priority: int = 10, plugin_id: Optional[str] = None):
    """Global utility to register a hook."""
    HooksEngine().register(hook_name, callback, priority, plugin_id)
