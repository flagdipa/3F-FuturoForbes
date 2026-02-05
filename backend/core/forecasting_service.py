"""
Service for financial forecasting and trend analysis.
Implements Linear Regression as seen in MMEX.
"""
from typing import List, Dict, Tuple
from decimal import Decimal
import datetime

class ForecastingService:
    @staticmethod
    def calculate_weighted_regression(data: List[Tuple[int, float]]) -> Dict[str, float]:
        """
        Calculates weighted linear regression y = mx + b
        Recent data points have more weight.
        """
        n = len(data)
        if n < 2:
            return {"slope": 0, "intercept": data[0][1] if n == 1 else 0}

        # Weights: linear increase from 1 to 2
        weights = [1.0 + (i / (n - 1)) for i in range(n)]
        sum_w = sum(weights)
        sum_wx = sum(w * x for w, (x, y) in zip(weights, data))
        sum_wy = sum(w * y for w, (x, y) in zip(weights, data))
        sum_wxx = sum(w * x * x for w, (x, y) in zip(weights, data))
        sum_wxy = sum(w * x * y for w, (x, y) in zip(weights, data))

        denominator = (sum_w * sum_wxx - sum_wx * sum_wx)
        if abs(denominator) < 1e-9:
            return {"slope": 0, "intercept": sum_wy / sum_w}

        m = (sum_w * sum_wxy - sum_wx * sum_wy) / denominator
        b = (sum_wy - m * sum_wx) / sum_w

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
