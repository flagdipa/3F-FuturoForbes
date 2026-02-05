"""
Database index creation script for performance optimization.
Creates strategic indexes on foreign keys and frequently filtered columns.
"""
from sqlmodel import Session, text
from backend.core.database import engine
import logging

logger = logging.getLogger(__name__)


def create_indexes():
    """Create performance indexes on critical tables after checking for existence"""
    
    indexes = [
        ("idx_libro_tx_cuenta", "libro_transacciones", "id_cuenta"),
        ("idx_libro_tx_beneficiario", "libro_transacciones", "id_beneficiario"),
        ("idx_libro_tx_categoria", "libro_transacciones", "id_categoria"),
        ("idx_libro_tx_fecha", "libro_transacciones", "fecha_transaccion"),
        
        ("idx_tx_etiqueta_tx", "transacciones_etiquetas", "id_transaccion"),
        ("idx_tx_etiqueta_et", "transacciones_etiquetas", "id_etiqueta"),
        
        ("idx_tx_dividida_tx", "transacciones_divididas", "id_transaccion"),
        ("idx_tx_dividida_cat", "transacciones_divididas", "id_categoria"),
        
        ("idx_recurrente_fecha", "transacciones_programadas", "proxima_fecha, activo"),
        ("idx_recurrente_cuenta", "transacciones_programadas", "id_cuenta"),
        
        ("idx_audit_usuario", "audit_logs", "id_usuario"),
        ("idx_audit_fecha", "audit_logs", "fecha"),
        ("idx_audit_entidad", "audit_logs", "entidad, id_entidad"),
        
        ("idx_cuenta_divisa", "lista_cuentas", "id_divisa"),
        ("idx_beneficiario_cat", "beneficiarios", "id_categoria"),
        ("idx_categoria_padre", "categorias", "id_padre"),
        
        ("idx_inversion_cuenta", "inversiones", "id_cuenta"),
        ("idx_inversion_simbolo", "inversiones", "simbolo"),
    ]
    
    # Get existing indexes to avoid duplicates
    existing_indexes = [idx[0] for idx in verify_indexes()]
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    with Session(engine) as session:
        for idx_name, table_name, cols in indexes:
            if idx_name in existing_indexes:
                logger.info(f"⏭ Index {idx_name} already exists, skipping")
                skipped_count += 1
                continue
                
            try:
                # Use standard CREATE INDEX (without IF NOT EXISTS for widest compatibility)
                sql = f"CREATE INDEX {idx_name} ON {table_name}({cols})"
                session.exec(text(sql))
                logger.info(f"✓ Created index: {idx_name}")
                created_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"✗ Failed to create index {idx_name}: {e}")
        
        session.commit()
    
    logger.info(f"\n✅ Index creation complete: {created_count} created, {skipped_count} skipped, {failed_count} failed")
    return created_count, failed_count


def verify_indexes():
    """Verify that indexes were created successfully"""
    
    with Session(engine) as session:
        # Check dialect
        db_type = engine.dialect.name
        
        if db_type == "sqlite":
            query = """
                SELECT name, tbl_name 
                FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
                ORDER BY tbl_name, name
            """
        elif db_type == "mysql":
            query = """
                SELECT index_name as name, table_name as tbl_name
                FROM information_schema.statistics
                WHERE table_schema = DATABASE() AND index_name LIKE 'idx_%'
                ORDER BY table_name, index_name
            """
        elif db_type == "postgresql":
            query = """
                SELECT indexname as name, tablename as tbl_name
                FROM pg_indexes
                WHERE indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """
        else:
            logger.info(f"Skipping index verification for unsupported dialect: {db_type}")
            return []
            
        result = session.exec(text(query))
        indexes = result.all()
        
        logger.info(f"\n📊 Found {len(indexes)} custom indexes:")
        
        current_table = None
        for idx_name, tbl_name in indexes:
            if current_table != tbl_name:
                current_table = tbl_name
                logger.info(f"\n  {tbl_name}:")
            logger.info(f"    - {idx_name}")
        
        return indexes


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    logger.info("🔨 Creating database indexes for performance optimization...\n")
    
    created, failed = create_indexes()
    
    logger.info(f"\n{'='*60}")
    verify_indexes()
    logger.info(f"{'='*60}\n")
    
    if failed == 0:
        logger.info("✅ All indexes created successfully!")
    else:
        logger.info(f"⚠️ {failed} indexes failed to create")
