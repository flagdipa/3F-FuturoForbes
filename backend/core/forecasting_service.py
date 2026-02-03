"""
Service for financial forecasting and trend analysis.
Implements Linear Regression as seen in MMEX.
"""
from typing import List, Dict, Tuple
from decimal import Decimal
import datetime

class ForecastingService:
    @staticmethod
    def calculate_linear_regression(data: List[Tuple[int, float]]) -> Dict[str, float]:
        """
        Calculates y = mx + b
        data: List of (index, value)
        returns: { 'slope': m, 'intercept': b }
        """
        n = len(data)
        if n < 2:
            return {"slope": 0, "intercept": data[0][1] if n == 1 else 0}

        sum_x = sum(x for x, y in data)
        sum_y = sum(y for x, y in data)
        sum_xy = sum(x * y for x, y in data)
        sum_xx = sum(x * x for x, y in data)

        # slope (m)
        denominator = (n * sum_xx - sum_x * sum_x)
        if denominator == 0:
            return {"slope": 0, "intercept": sum_y / n}
            
        m = (n * sum_xy - sum_x * sum_y) / denominator
        # intercept (b)
        b = (sum_y - m * sum_x) / n

        return {"slope": m, "intercept": b}

    @staticmethod
    def forecast_account_balance(current_balance: Decimal, recurring_txs: List[Dict], days: int = 30) -> List[Dict]:
        """
        Proyects balance based on scheduled transactions.
        """
        today = datetime.date.today()
        projections = []
        running_balance = float(current_balance)
        
        # Simple projection: daily snapshots
        for d in range(days + 1):
            date_point = today + datetime.timedelta(days=d)
            # Find txs for this date
            for tx in recurring_txs:
                # This is a simplification. Real logic should check if date matches frequency.
                if tx.get('proxima_fecha') == date_point:
                    running_balance += float(tx.get('monto_transaccion', 0))
            
            projections.append({
                "fecha": date_point.isoformat(),
                "saldo": round(running_balance, 2)
            })
            
        return projections

forecasting_service = ForecastingService()
