from sqlmodel import Session, select, func
from ...models.models import Categoria, LibroTransacciones, TransaccionDividida, Presupuesto, Beneficiario
from ...models.models_advanced import TransaccionRecurrente
from typing import Dict

class CategoryExtService:
    @staticmethod
    def get_stats(session: Session, category_id: int) -> Dict[str, int]:
        """Fetch usage statistics for a category"""
        stats = {
            "transacciones": session.exec(select(func.count()).where(LibroTransacciones.id_categoria == category_id)).one(),
            "divisiones": session.exec(select(func.count()).where(TransaccionDividida.id_categoria == category_id)).one(),
            "programadas": session.exec(select(func.count()).where(TransaccionRecurrente.id_categoria == category_id)).one(),
            "divisiones_programadas": 0, # Placeholder, depends on model complexity
            "beneficiarios": session.exec(select(func.count()).where(Beneficiario.id_categoria == category_id)).one(),
            "presupuestos": session.exec(select(func.count()).where(Presupuesto.id_categoria == category_id)).one(),
        }
        return stats

    @staticmethod
    def merge(session: Session, id_origen: int, id_destino: int, delete_source: bool = False):
        """Move all items from origin category to destination category"""
        # 1. Update Transactions
        trans = session.exec(select(LibroTransacciones).where(LibroTransacciones.id_categoria == id_origen)).all()
        for t in trans:
            t.id_categoria = id_destino
            session.add(t)

        # 2. Update Splits
        splits = session.exec(select(TransaccionDividida).where(TransaccionDividida.id_categoria == id_origen)).all()
        for s in splits:
            s.id_categoria = id_destino
            session.add(s)

        # 3. Update Scheduled Transactions
        recurring = session.exec(select(TransaccionRecurrente).where(TransaccionRecurrente.id_categoria == id_origen)).all()
        for r in recurring:
            r.id_categoria = id_destino
            session.add(r)

        # 4. Update Payee defaults
        payees = session.exec(select(Beneficiario).where(Beneficiario.id_categoria == id_origen)).all()
        for p in payees:
            p.id_categoria = id_destino
            session.add(p)

        # 5. Update Budgets
        budgets = session.exec(select(Presupuesto).where(Presupuesto.id_categoria == id_origen)).all()
        for b in budgets:
            b.id_categoria = id_destino
            session.add(b)

        session.commit()

        # 6. Delete source if requested and has no subcategories
        if delete_source:
            subcats_count = session.exec(select(func.count()).select_from(Categoria).where(Categoria.id_padre == id_origen)).one()
            if subcats_count == 0:
                source_cat = session.get(Categoria, id_origen)
                if source_cat:
                    session.delete(source_cat)
                    session.commit()
            else:
                return {"warning": "Categoría de origen no eliminada porque tiene subcategorías."}

        return {"success": True}

category_ext_service = CategoryExtService()
