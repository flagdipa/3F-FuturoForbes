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
        Projects balance based on scheduled transactions with frequency-aware logic.
        """
        today = datetime.date.today()
        projections = []
        running_balance = Decimal(str(current_balance))
        
        # Pre-calculate occurrence dates for each recurring transaction within the window
        end_date = today + datetime.timedelta(days=days)
        
        # Map of date -> total change
        daily_changes = {}

        for tx in recurring_txs:
            monto = Decimal(str(tx.get('monto_transaccion', 0)))
            freq = tx.get('frecuencia', 'Monthly')
            interval = tx.get('intervalo', 1)
            start_date = tx.get('proxima_fecha')
            
            if not start_date:
                continue
            
            # If start_date is a string, convert it
            if isinstance(start_date, str):
                start_date = datetime.date.fromisoformat(start_date)
            
            # Simple iteration to find occurrences
            current_occurrence = start_date
            
            # Logic for occurrences
            while current_occurrence <= end_date:
                if current_occurrence >= today:
                    daily_changes[current_occurrence] = daily_changes.get(current_occurrence, Decimal(0)) + monto
                
                # Advance date based on frequency
                if freq == 'Daily':
                    current_occurrence += datetime.timedelta(days=interval)
                elif freq == 'Weekly':
                    current_occurrence += datetime.timedelta(weeks=interval)
                elif freq == 'Bi-weekly':
                    current_occurrence += datetime.timedelta(weeks=2 * interval)
                elif freq == 'Monthly':
                    # Rough month advancement
                    # For more precision, we usually use relativedelta, but let's use a standard approximation
                    # to keep it lightweight if we don't have python-dateutil
                    # Using a safe way to jump months:
                    days_in_month = 30 # Approximation for loop safety
                    new_month = current_occurrence.month + interval
                    new_year = current_occurrence.year + (new_month - 1) // 12
                    new_month = (new_month - 1) % 12 + 1
                    try:
                        current_occurrence = current_occurrence.replace(year=new_year, month=new_month)
                    except ValueError:
                        # Handle month end issues (e.g. Jan 31 -> Feb 28)
                        import calendar
                        _, last_day = calendar.monthrange(new_year, new_month)
                        current_occurrence = current_occurrence.replace(year=new_year, month=new_month, day=last_day)
                elif freq == 'Yearly':
                    try:
                        current_occurrence = current_occurrence.replace(year=current_occurrence.year + interval)
                    except ValueError:
                        # Handle Feb 29
                        current_occurrence = current_occurrence.replace(year=current_occurrence.year + interval, day=28)
                else:
                    # Unknown frequency, break to avoid infinite loop
                    break

        # Generate daily snapshots
        for d in range(days + 1):
            date_point = today + datetime.timedelta(days=d)
            if date_point in daily_changes:
                running_balance += daily_changes[date_point]
            
            projections.append({
                "fecha": date_point.isoformat(),
                "saldo": float(round(running_balance, 2))
            })
            
        return projections

forecasting_service = ForecastingService()
