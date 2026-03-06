import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.core.database import engine
from sqlmodel import Session, select
from backend.models import Account, User, Transaction, Category

def fetch_counts():
    with Session(engine) as session:
        print("Users:", len(session.exec(select(User)).all()))
        print("Accounts:", len(session.exec(select(Account)).all()))
        print("Transactions:", len(session.exec(select(Transaction)).all()))
        print("Categories:", len(session.exec(select(Category)).all()))

if __name__ == '__main__':
    fetch_counts()
