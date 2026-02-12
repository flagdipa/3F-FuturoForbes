import sys
import os
from datetime import date, timedelta
from decimal import Decimal

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.forecasting_service import forecasting_service

def test_forecasting():
    print("Testing Advanced Forecasting Engine...")
    
    current_balance = Decimal("1000.00")
    today = date.today()
    
    recurring_txs = [
        # Daily tx: -10 every day
        {
            "frecuencia": "Daily",
            "intervalo": 1,
            "monto_transaccion": Decimal("-10.00"),
            "proxima_fecha": today
        },
        # Weekly tx: -50 every week
        {
            "frecuencia": "Weekly",
            "intervalo": 1,
            "monto_transaccion": Decimal("-50.00"),
            "proxima_fecha": today + timedelta(days=2) # 2 days from now
        },
        # Monthly tx: +2000 salary
        {
            "frecuencia": "Monthly",
            "intervalo": 1,
            "monto_transaccion": Decimal("2000.00"),
            "proxima_fecha": today + timedelta(days=5) # 5 days from now
        }
    ]
    
    projections = forecasting_service.forecast_account_balance(current_balance, recurring_txs, days=30)
    
    print(f"Start Balance: {current_balance}")
    print(f"Day 0: {projections[0]['fecha']} -> {projections[0]['saldo']}")
    print(f"Day 2 (Should reflect weekly -50 and daily -10*3): {projections[2]['fecha']} -> {projections[2]['saldo']}")
    print(f"Day 5 (Should reflect monthly +2000): {projections[5]['fecha']} -> {projections[5]['saldo']}")
    print(f"Day 30 (Final Projection): {projections[30]['fecha']} -> {projections[30]['saldo']}")

    # Verification logic
    # Day 0: only daily -10 -> 990
    # Day 2: -10 (d0), -10 (d1), -10 (d2), -50 (d2) -> 1000 - 80 = 920
    # Day 5: -10*6 (d0-d5), -50 (d2), +2000 (d5) -> 1000 - 60 - 50 + 2000 = 2890
    
    assert projections[0]['saldo'] == 990.0
    assert projections[2]['saldo'] == 920.0
    assert projections[5]['saldo'] == 2890.0
    print("✅ Logic verification PASS!")

if __name__ == "__main__":
    test_forecasting()
