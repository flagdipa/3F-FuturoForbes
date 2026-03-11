# models_audit.py — Re-export del modelo AuditLog centralizado en models_v2.
#
# IMPORTANTE: Este archivo solo re-exporta la clase AuditLog definida en models_v2.py.
# NO redefine la clase para evitar el error:
#   sqlalchemy.exc.InvalidRequestError: Table 'audit_logs' is already defined
#
# Los atributos del schema LEGACY que usaban los tests antiguos eran:
#   accion, entidad, id_usuario, id_entidad, ip_address, detalles
# El schema ACTUAL en models_v2 usa:
#   action, entity_type, user_id, entity_id, ip_address, old_values, new_values
#
# Los tests en test_base_crud.py deben actualizarse para usar los nombres actuales.

from .models_v2 import AuditLog

__all__ = ["AuditLog"]
