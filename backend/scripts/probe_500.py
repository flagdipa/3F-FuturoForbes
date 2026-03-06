import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.core.database import engine
from sqlmodel import Session, select
from backend.models import Account
from backend.api.v1.accounts import AccountResponse

def test_fetch():
    with Session(engine) as session:
        accounts = session.exec(select(Account)).all()
        for acc in accounts:
            try:
                print("Revisando cuenta:", acc.id, acc.name)
                resp = AccountResponse.model_validate(acc)
                print("✓ OK")
            except Exception as e:
                print("❌ ERROR en cuenta id", acc.id)
                print(e)

if __name__ == '__main__':
    test_fetch()
