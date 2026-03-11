from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from ....models import TransactionStatus

class PayeeSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class AccountSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class CategorySimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class TagSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: Optional[str] = None

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
    model_config = ConfigDict(from_attributes=True)
    id: int
    account: Optional[AccountSimple] = None
    category: Optional[CategorySimple] = None

class TransactionBase(BaseModel):
    date: datetime
    description: Optional[str] = None
    payee_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    splits: List[SplitCreate]
    status: Optional[TransactionStatus] = None  # Optional; defaults to PENDING on create
    tag_ids: Optional[List[int]] = None

class TransactionUpdate(BaseModel):
    date: Optional[datetime] = None
    description: Optional[str] = None
    payee_id: Optional[int] = None
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: TransactionStatus
    payee: Optional[PayeeSimple] = None
    splits: List[SplitResponse]
    tags: List[TagSimple] = []
    created_at: datetime
    updated_at: datetime

class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal
    currency_code: str
    date: datetime
    description: Optional[str] = None
