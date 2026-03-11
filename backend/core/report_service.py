"""
ReportService — Reportes financieros reales basados en el modelo de doble entrada.

Todos los cálculos se hacen sobre transaction_splits + accounts.type para
distinguir ingresos (INCOME), gastos (EXPENSE) y activos (ASSET/LIABILITY).
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
from sqlmodel import Session, select, func, col
from collections import defaultdict

from ..models import Transaction, TransactionSplit, Account, Category, AccountType

logger = logging.getLogger("report_service")

# Paleta neon para categorías (se cicla si hay más de 10 categorías)
CATEGORY_COLORS = [
    "#00f2ff", "#7000ff", "#ff0055", "#ffe600", "#00ff9d",
    "#ff9900", "#ff00cc", "#00ccff", "#ccff00", "#ffffff"
]


class ReportService:
    """
    Reportes financieros sobre datos reales del ledger de doble entrada.
    """
    def __init__(self, db: Session):
        self.db = db

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _float(self, val) -> float:
        """Convierte Decimal o None a float."""
        if val is None:
            return 0.0
        return float(val)

    def _user_account_ids(self, user_id: int, acct_types: list[str]) -> list[int]:
        """Devuelve IDs de cuentas del usuario por tipo."""
        stmt = select(Account.id).where(
            Account.user_id == user_id,
            Account.type.in_(acct_types),
            Account.deleted_at.is_(None)
        )
        return [r for r in self.db.exec(stmt)]

    # ─── Cashflow (Ingresos vs Gastos por mes) ────────────────────────────────

    def get_cashflow_report(self, user_id: int, date_from: datetime, date_to: datetime) -> Dict[str, Any]:
        """Agrupa ingresos y gastos por mes dentro del período."""
        income_ids = self._user_account_ids(user_id, [AccountType.INCOME.value])
        expense_ids = self._user_account_ids(user_id, [AccountType.EXPENSE.value])

        # Ingresos por mes
        income_by_month = self._sum_by_month(income_ids, date_from, date_to, negate=True)
        # Gastos por mes
        expense_by_month = self._sum_by_month(expense_ids, date_from, date_to, negate=False)

        # Unir todos los meses conocidos
        all_months = sorted(set(list(income_by_month.keys()) + list(expense_by_month.keys())))

        monthly_breakdown = []
        total_income = 0.0
        total_expense = 0.0

        for month in all_months:
            inc = income_by_month.get(month, 0.0)
            exp = expense_by_month.get(month, 0.0)
            total_income += inc
            total_expense += exp
            monthly_breakdown.append({
                "month": month,
                "income": round(inc, 2),
                "expense": round(exp, 2),
                "net": round(inc - exp, 2),
            })

        return {
            "period": f"{date_from.strftime('%Y-%m')} to {date_to.strftime('%Y-%m')}",
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_cashflow": round(total_income - total_expense, 2),
            "monthly_breakdown": monthly_breakdown,
        }

    def _sum_by_month(self, account_ids: list[int], date_from: datetime, date_to: datetime, negate: bool) -> Dict[str, float]:
        """Agrupa la suma de splits por 'YYYY-MM' para una lista de cuentas."""
        if not account_ids:
            return {}

        result = defaultdict(float)
        stmt = (
            select(Transaction.date, TransactionSplit.amount)
            .join(Transaction, TransactionSplit.transaction_id == Transaction.id)
            .where(
                TransactionSplit.account_id.in_(account_ids),
                Transaction.date >= date_from,
                Transaction.date <= date_to,
                Transaction.deleted_at.is_(None),
            )
        )
        rows = self.db.exec(stmt).all()
        for tx_date, amount in rows:
            month_key = tx_date.strftime("%Y-%m")
            val = self._float(amount)
            result[month_key] += (-val if negate else abs(val))
        return result

    # ─── Distribución por Categoría ───────────────────────────────────────────

    def get_category_distribution(self, user_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Suma gastos agrupados por categoría en el período."""
        expense_ids = self._user_account_ids(user_id, [AccountType.EXPENSE.value])
        if not expense_ids:
            return []

        stmt = (
            select(
                Category.id,
                Category.name,
                Category.color,
                func.sum(TransactionSplit.amount).label("total")
            )
            .join(TransactionSplit, TransactionSplit.category_id == Category.id)
            .join(Transaction, TransactionSplit.transaction_id == Transaction.id)
            .where(
                TransactionSplit.account_id.in_(expense_ids),
                Transaction.date >= date_from,
                Transaction.date <= date_to,
                Transaction.deleted_at.is_(None),
                Category.user_id == user_id,
                Category.deleted_at.is_(None),
            )
            .group_by(Category.id, Category.name, Category.color)
            .order_by(func.sum(TransactionSplit.amount).desc())
        )
        rows = self.db.exec(stmt).all()

        total_all = sum(abs(self._float(r.total)) for r in rows) or 1.0
        result = []
        for i, r in enumerate(rows):
            val = abs(self._float(r.total))
            result.append({
                "category_id": r.id,
                "name": r.name,
                "color": r.color or CATEGORY_COLORS[i % len(CATEGORY_COLORS)],
                "total_expense": round(val, 2),
                "percentage": round(val / total_all * 100, 1),
            })
        return result

    # ─── Heatmap de actividad ─────────────────────────────────────────────────

    def get_spending_heatmap(self, user_id: int, date_from: datetime, date_to: datetime) -> Dict[str, Any]:
        """Distribución de actividad por día de la semana y hora (usando Python para calcular)."""
        expense_ids = self._user_account_ids(user_id, [AccountType.EXPENSE.value])
        if not expense_ids:
            return {"days_of_week": {}, "heatmap_data": []}

        stmt = (
            select(Transaction.date, TransactionSplit.amount)
            .join(Transaction, TransactionSplit.transaction_id == Transaction.id)
            .where(
                TransactionSplit.account_id.in_(expense_ids),
                Transaction.date >= date_from,
                Transaction.date <= date_to,
                Transaction.deleted_at.is_(None),
            )
        )
        rows = self.db.exec(stmt).all()

        DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_count: Dict[str, float] = defaultdict(float)
        heatmap: Dict[tuple, float] = defaultdict(float)

        for tx_date, amount in rows:
            day_idx = tx_date.weekday()  # 0=Monday
            hour = tx_date.hour
            val = abs(self._float(amount))
            days_count[DAY_NAMES[day_idx]] += val
            heatmap[(day_idx, hour)] += val

        # Normalizar heatmap a intensidad 0-100
        max_val = max(heatmap.values(), default=1)
        heatmap_data = [
            [day, hour, round(val / max_val * 100)]
            for (day, hour), val in heatmap.items()
        ]

        return {
            "days_of_week": dict(days_count),
            "heatmap_data": sorted(heatmap_data, key=lambda x: x[2], reverse=True),
        }

    # ─── Patrimonio Neto ──────────────────────────────────────────────────────

    def get_net_worth_trend(self, user_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """
        Devuelve el patrimonio neto actual (ASSET - LIABILITY) como punto único.
        Una evolución histórica real requeriría snapshots; devolvemos los balances actuales por mes.
        """
        asset_stmt = (
            select(func.sum(Account.current_balance))
            .where(Account.user_id == user_id, Account.type == AccountType.ASSET, Account.deleted_at.is_(None))
        )
        liab_stmt = (
            select(func.sum(Account.current_balance))
            .where(Account.user_id == user_id, Account.type == AccountType.LIABILITY, Account.deleted_at.is_(None))
        )
        total_assets = self._float(self.db.exec(asset_stmt).one_or_none())
        total_liab = self._float(self.db.exec(liab_stmt).one_or_none())
        net_worth = total_assets + total_liab  # liabilities son negativas en el modelo

        # Construir trend mensual a partir del cashflow acumulado
        cashflow = self.get_cashflow_report(user_id, date_from, date_to)
        trend = []
        running = net_worth
        for m in reversed(cashflow["monthly_breakdown"]):
            trend.insert(0, {
                "date": m["month"],
                "assets": round(running + abs(total_liab), 2),
                "liabilities": round(total_liab, 2),
                "net_worth": round(running, 2),
            })
            running -= m["net"]  # Restar hacia atrás

        return trend if trend else [{"date": datetime.now().strftime("%Y-%m"), "assets": total_assets, "liabilities": total_liab, "net_worth": net_worth}]

    # ─── Budget vs Actual ─────────────────────────────────────────────────────

    def get_budget_vs_actual(self, user_id: int, current_month: str) -> List[Dict[str, Any]]:
        """Compara presupuestos asignados vs gastos reales del mes."""
        try:
            year, month = int(current_month.split("-")[0]), int(current_month.split("-")[1])
        except (ValueError, IndexError):
            year, month = datetime.now().year, datetime.now().month

        date_from = datetime(year, month, 1)
        date_to = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Importar Budget aquí para evitar posibles circulares
        try:
            from ..models import Budget
        except ImportError:
            return []

        budget_stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.year == year,
            Budget.month == month,
        )
        budgets = self.db.exec(budget_stmt).all()
        if not budgets:
            return []

        expense_ids = self._user_account_ids(user_id, [AccountType.EXPENSE.value])
        result = []

        for budget in budgets:
            stmt = (
                select(func.sum(TransactionSplit.amount))
                .join(Transaction, TransactionSplit.transaction_id == Transaction.id)
                .where(
                    TransactionSplit.account_id.in_(expense_ids),
                    TransactionSplit.category_id == budget.category_id,
                    Transaction.date >= date_from,
                    Transaction.date < date_to,
                    Transaction.deleted_at.is_(None),
                )
            )
            spent = abs(self._float(self.db.exec(stmt).one_or_none()))
            budgeted = self._float(budget.amount)
            pct = round(spent / budgeted * 100, 1) if budgeted else 0

            status = "ontrack"
            if pct > 100:
                status = "overbudget"
            elif pct < 70:
                status = "underbudget"

            result.append({
                "category": budget.category.name if budget.category else str(budget.category_id),
                "budgeted": round(budgeted, 2),
                "spent": round(spent, 2),
                "percentage": pct,
                "status": status,
            })

        return sorted(result, key=lambda x: x["spent"], reverse=True)
