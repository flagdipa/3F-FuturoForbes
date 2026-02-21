import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select, SQLModel, Field, Column, JSON
from backend.core.database import engine

logger = logging.getLogger("argentina_datos.services")

# database models
class ArgDatCache(SQLModel, table=True):
    __tablename__ = "argdat_cache"
    endpoint: str = Field(primary_key=True)
    datos: Dict[str, Any] = Field(sa_column=Column(JSON))
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)

class ArgDatSyncLog(SQLModel, table=True):
    __tablename__ = "argdat_sync_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint: str = Field(index=True)
    estado: str = Field(index=True) # "ok", "error"
    mensaje: Optional[str] = None
    ejecutado_el: datetime = Field(default_factory=datetime.utcnow)

class ArgentinaDatosService:
    BASE_URL = "https://api.argentinadatos.com"

    def __init__(self):
        # Create tables if not exist
        SQLModel.metadata.create_all(engine)

    async def fetch_and_cache(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Consumes the external API and caches the result.
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Update cache
                with Session(engine) as session:
                    cache_entry = session.get(ArgDatCache, endpoint)
                    if cache_entry:
                        cache_entry.datos = data
                        cache_entry.actualizado_el = datetime.utcnow()
                    else:
                        cache_entry = ArgDatCache(endpoint=endpoint, datos=data)
                    session.add(cache_entry)
                    
                    # Log success
                    log = ArgDatSyncLog(endpoint=endpoint, estado="ok")
                    session.add(log)
                    session.commit()
                return data
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            with Session(engine) as session:
                log = ArgDatSyncLog(endpoint=endpoint, estado="error", mensaje=str(e))
                session.add(log)
                session.commit()
            return None

    def get_cached_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        with Session(engine) as session:
            cache_entry = session.get(ArgDatCache, endpoint)
            return cache_entry.datos if cache_entry else None

    def get_all_cached(self, endpoints: List[str]) -> Dict[str, Any]:
        results = {}
        with Session(engine) as session:
            for ep in endpoints:
                cache_entry = session.get(ArgDatCache, ep)
                if cache_entry:
                    results[ep] = {
                        "datos": cache_entry.datos,
                        "actualizado_el": cache_entry.actualizado_el.isoformat()
                    }
        return results
