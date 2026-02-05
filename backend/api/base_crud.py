from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlmodel import Session, select, func, SQLModel
from .schemas.common import PaginatedResponse, PaginationMetadata
from ..core.audit_service import audit_service

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseCRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic Base CRUD Service with integrated Auditing.
    Promotes DRY and simplifies API routers.
    """
    def __init__(self, model: Type[ModelType], entity_name: Optional[str] = None):
        self.model = model
        self.entidad = entity_name or model.__name__

    def get(self, session: Session, id_val: Any) -> Optional[ModelType]:
        """Fetch a single record by its ID"""
        return session.get(self.model, id_val)

    def list(
        self, 
        session: Session, 
        offset: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse[ModelType]:
        """List records with pagination and optional filters"""
        query = select(self.model)
        
        # Apply basic filters if provided
        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr) and value is not None:
                    query = query.where(getattr(self.model, attr) == value)
        
        # Count total
        total_query = select(func.count()).select_from(query.subquery())
        total = session.exec(total_query).one()
        
        # Fetch data
        query = query.offset(offset).limit(limit)
        items = session.exec(query).all()
        
        return PaginatedResponse(
            data=items,
            pagination=PaginationMetadata(
                total=total,
                offset=offset,
                limit=limit,
                has_more=(offset + limit) < total
            )
        )

    def create(
        self, 
        session: Session, 
        obj_in: CreateSchemaType,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> ModelType:
        """Create a new record with automatic auditing"""
        obj_data = obj_in.dict() if hasattr(obj_in, "dict") else dict(obj_in)
        db_obj = self.model(**obj_data)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        
        # Audit
        if user_id:
            audit_service.log(
                session=session,
                user_id=user_id,
                accion="CREATE",
                entidad=self.entidad,
                id_entidad=getattr(db_obj, list(db_obj.__dict__.keys())[1], None), # Primary key trick
                detalles=obj_data,
                ip_address=ip_address
            )
            
        return db_obj

    def update(
        self, 
        session: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> ModelType:
        """Update an existing record with automatic auditing"""
        obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else dict(obj_in)
        
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        
        # Audit
        if user_id:
            audit_service.log(
                session=session,
                user_id=user_id,
                accion="UPDATE",
                entidad=self.entidad,
                id_entidad=getattr(db_obj, list(db_obj.__dict__.keys())[1], None),
                detalles=obj_data,
                ip_address=ip_address
            )
            
        return db_obj

    def delete(
        self, 
        session: Session, 
        id_val: Any,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """Delete a record by its ID with automatic auditing"""
        db_obj = session.get(self.model, id_val)
        if not db_obj:
            return False
            
        session.delete(db_obj)
        session.commit()
        
        # Audit
        if user_id:
            audit_service.log(
                session=session,
                user_id=user_id,
                accion="DELETE",
                entidad=self.entidad,
                id_entidad=id_val if isinstance(id_val, int) else None,
                detalles={"id_eliminado": id_val},
                ip_address=ip_address
            )
            
        return True
