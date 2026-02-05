"""
Theme System - Preset Definitions
4 beautiful themes for the FuturoForbes application
"""

THEMES = {
    "dark_neon": {
        "id": "dark_neon",
        "name": "Dark Neon (Default)",
        "description": "Tema oscuro futurista con acentos neon cyan y magenta",
        "variables": {
            # Backgrounds
            "--3f-bg": "#0a0e27",
            "--3f-bg-card": "rgba(7, 30, 38, 0.4)",
            "--3f-bg-hover": "rgba(37, 150, 190, 0.1)",
            
            # Primary colors
            "--3f-primary": "#00f3ff",  # Cyan neon
            "--3f-primary-glow": "rgba(0, 243, 255, 0.5)",
            "--3f-secondary": "#ff00ff",  # Magenta
            "--3f-accent": "#00ff88",  # Green accent
            
            # Text
            "--3f-text": "#e0f7fa",
            "--3f-text-dim": "#80deea",
            "--3f-text-muted": "#546e7a",
            
            # Borders
            "--3f-border": "rgba(0, 243, 255, 0.3)",
            "--3f-border-hover": "rgba(0, 243, 255, 0.6)",
            
            # Status
            "--3f-success": "#00ff88",
            "--3f-warning": "#ffeb3b",
            "--3f-danger": "#ff1744",
            "--3f-info": "#00e5ff"
        }
    },
    
    "light": {
        "id": "light",
        "name": "Light Professional",
        "description": "Tema claro profesional con acentos azules",
        "variables": {
            # Backgrounds
            "--3f-bg": "#f5f7fa",
            "--3f-bg-card": "#ffffff",
            "--3f-bg-hover": "rgba(33, 150, 243, 0.05)",
            
            # Primary colors
            "--3f-primary": "#2196f3",  # Material Blue
            "--3f-primary-glow": "rgba(33, 150, 243, 0.3)",
            "--3f-secondary": "#673ab7",  # Purple
            "--3f-accent": "#00bcd4",  # Cyan
            
            # Text
            "--3f-text": "#263238",
            "--3f-text-dim": "#546e7a",
            "--3f-text-muted": "#90a4ae",
            
            # Borders
            "--3f-border": "rgba(0, 0, 0, 0.12)",
            "--3f-border-hover": "rgba(33, 150, 243, 0.5)",
            
            # Status
            "--3f-success": "#4caf50",
            "--3f-warning": "#ff9800",
            "--3f-danger": "#f44336",
            "--3f-info": "#03a9f4"
        }
    },
    
    "matrix": {
        "id": "matrix",
        "name": "Matrix Green",
        "description": "Tema inspirado en Matrix con verdes fosforescentes",
        "variables": {
            # Backgrounds
            "--3f-bg": "#000000",
            "--3f-bg-card": "rgba(0, 20, 0, 0.6)",
            "--3f-bg-hover": "rgba(0, 255, 65, 0.1)",
            
            # Primary colors
            "--3f-primary": "#00ff41",  # Matrix green
            "--3f-primary-glow": "rgba(0, 255, 65, 0.6)",
            "--3f-secondary": "#39ff14",  # Neon green
            "--3f-accent": "#0dff00",  # Bright green
            
            # Text
            "--3f-text": "#00ff41",
            "--3f-text-dim": "#00cc33",
            "--3f-text-muted": "#006622",
            
            # Borders
            "--3f-border": "rgba(0, 255, 65, 0.3)",
            "--3f-border-hover": "rgba(0, 255, 65, 0.7)",
            
            # Status
            "--3f-success": "#00ff41",
            "--3f-warning": "#ffff00",
            "--3f-danger": "#ff0000",
            "--3f-info": "#00ffff"
        }
    },
    
    "cyberpunk": {
        "id": "cyberpunk",
        "name": "Cyberpunk Purple",
        "description": "Tema cyberpunk con púrpuras y amarillos neón",
        "variables": {
            # Backgrounds
            "--3f-bg": "#1a0033",
            "--3f-bg-card": "rgba(75, 0, 130, 0.3)",
            "--3f-bg-hover": "rgba(148, 0, 211, 0.15)",
            
            # Primary colors
            "--3f-primary": "#da00ff",  # Bright purple
            "--3f-primary-glow": "rgba(218, 0, 255, 0.5)",
            "--3f-secondary": "#ffea00",  # Electric yellow
            "--3f-accent": "#ff006e",  # Hot pink
            
            # Text
            "--3f-text": "#f0e6ff",
            "--3f-text-dim": "#c79dff",
            "--3f-text-muted": "#8b5cf6",
            
            # Borders
            "--3f-border": "rgba(218, 0, 255, 0.4)",
            "--3f-border-hover": "rgba(218, 0, 255, 0.8)",
            
            # Status
            "--3f-success": "#00ff9f",
            "--3f-warning": "#ffea00",
            "--3f-danger": "#ff006e",
            "--3f-info": "#00d9ff"
        }
    }
}

def get_theme(theme_id: str):
    """Get theme by ID"""
    return THEMES.get(theme_id, THEMES["dark_neon"])

def get_all_themes():
    """Get list of all available themes"""
    return [
        {
            "id": theme["id"],
            "name": theme["name"],
            "description": theme["description"]
        }
        for theme in THEMES.values()
    ]
