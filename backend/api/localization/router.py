from fastapi import APIRouter, Depends, HTTPException
from ..auth.deps import get_current_user
import json
import os
from typing import Dict, Any

router = APIRouter(prefix="/localization", tags=["Localization"])

# Relative to the root of the project where uvicorn is running
LANG_DIR = "frontend/static/js"

@router.get("/languages")
async def list_languages(current_user: Any = Depends(get_current_user)):
    """Lists available language files."""
    try:
        files = [f for f in os.listdir(LANG_DIR) if f.startswith("lang-") and f.endswith(".json")]
        langs = [f.replace("lang-", "").replace(".json", "") for f in files]
        return langs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lang}")
async def get_translations(lang: str, current_user: Any = Depends(get_current_user)):
    """Retrieves full translation dictionary for a language."""
    file_path = os.path.join(LANG_DIR, f"lang-{lang}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Language '{lang}' not found")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lang}")
async def update_translations(lang: str, data: Dict[str, Any], current_user: Any = Depends(get_current_user)):
    """Overwrites the translation dictionary for a language."""
    file_path = os.path.join(LANG_DIR, f"lang-{lang}.json")
    # No check if exists, allow creating new languages? No, let's restrict to existing for safety or check dir
    if not os.path.isdir(LANG_DIR):
        raise HTTPException(status_code=500, detail="Static directory not found")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return {"status": "success", "message": f"Language '{lang}' updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
