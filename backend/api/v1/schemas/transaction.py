from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from ....models import TransactionStatus

class SplitBase(BaseModel):
    account_id: int
    category_id: Optional[int] = None
    amount: Decimal
    currency_code: str
    currency_amount: Optional[Decimal] = None
    memo: Optional[str] = None

class SplitCreate(SplitBase):
    pass

class SplitResponse(SplitBase):
    id: int

class TransactionBase(BaseModel):
    date: datetime
    description: Optional[str] = None
    payee_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    splits: List[SplitCreate]

class TransactionUpdate(BaseModel):
    date: Optional[datetime] = None
    description: Optional[str] = None
    payee_id: Optional[int] = None
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    status: TransactionStatus
    splits: List[SplitResponse]
    created_at: datetime
    updated_at: datetime

class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal
    currency_code: str
    date: datetime
    description: Optional[str] = None
