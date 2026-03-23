from datetime import datetime, date
from typing import Optional, List, Any, Dict
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from decimal import Decimal
from enum import Enum

# --- MIXINS ---

class AuditMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SoftDeleteMixin(SQLModel):
    deleted_at: Optional[datetime] = Field(default=None)

# --- USUARIOS ---

class User(AuditMixin, SoftDeleteMixin, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    theme_id: str = Field(default="3f-neon")
    language: str = Field(default="es")

    # Relationships
    accounts: List["Account"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    institutions: List["Institution"] = Relationship(back_populates="user")

# --- FINANZAS CORE ---

class Currency(SoftDeleteMixin, table=True):
    __tablename__ = "currencies"
    code: str = Field(primary_key=True)  # ISO 4217
    name: str
    symbol: Optional[str] = None
    decimal_places: int = Field(default=2)
    is_base: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExchangeRate(SQLModel, table=True):
    __tablename__ = "exchange_rates"
    id: Optional[int] = Field(default=None, primary_key=True)
    from_currency: str = Field(foreign_key="currencies.code")
    to_currency: str = Field(foreign_key="currencies.code")
    rate: Decimal = Field(max_digits=20, decimal_places=8)
    provider: Optional[str] = None
    rate_date: datetime = Field(default_factory=datetime.utcnow)

class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class Institution(SoftDeleteMixin, table=True):
    __tablename__ = "institutions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(index=True)
    type: Optional[str] = None # Bank, Broker, etc.
    branch: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    cuit: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="institutions")
    accounts: List["Account"] = Relationship(back_populates="institution")

class Account(AuditMixin, SoftDeleteMixin, table=True):
    __tablename__ = "accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    name: str
    code: str = Field(unique=True, index=True)
    type: AccountType
    currency_code: str = Field(foreign_key="currencies.code")
    account_number: Optional[str] = None
    institution_id: Optional[int] = Field(default=None, foreign_key="institutions.id")
    initial_balance: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    current_balance: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    color: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = Field(default=True)

    # Relationships
    user: User = Relationship(back_populates="accounts")
    splits: List["TransactionSplit"] = Relationship(back_populates="account")
    institution: Optional["Institution"] = Relationship(back_populates="accounts")

class Category(SoftDeleteMixin, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    name: str
    type: str # INCOME, EXPENSE
    color: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    splits: List["TransactionSplit"] = Relationship(back_populates="category")

class Payee(SoftDeleteMixin, table=True):
    __tablename__ = "payees"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True)
    default_category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    bank_name: Optional[str] = None
    cbu: Optional[str] = None
    cuit: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="payee")

# --- TRANSACCIONES (Double-Entry) ---

class TransactionTagLink(SQLModel, table=True):
    __tablename__ = "transaction_tag_link"
    transaction_id: int = Field(foreign_key="transactions.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="tags", link_model=TransactionTagLink)

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    RECONCILED = "RECONCILED"
    VOID = "VOID"

class Transaction(AuditMixin, SoftDeleteMixin, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    date: datetime = Field(index=True)
    description: Optional[str] = None
    payee_id: Optional[int] = Field(default=None, foreign_key="payees.id")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    reference_number: Optional[str] = None
    notes: Optional[str] = None

    # Relationships
    user: User = Relationship(back_populates="transactions")
    splits: List["TransactionSplit"] = Relationship(back_populates="transaction")
    payee: Optional["Payee"] = Relationship(back_populates="transactions")
    tags: List["Tag"] = Relationship(back_populates="transactions", link_model=TransactionTagLink)

class TransactionSplit(SQLModel, table=True):
    __tablename__ = "transaction_splits"
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id", ondelete="CASCADE")
    account_id: int = Field(foreign_key="accounts.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    amount: Decimal = Field(max_digits=20, decimal_places=8) # Positive for Debit, Negative for Credit
    currency_code: str = Field(foreign_key="currencies.code")
    currency_amount: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=8)
    memo: Optional[str] = None
    reconciled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transaction: Transaction = Relationship(back_populates="splits")
    account: Account = Relationship(back_populates="splits")
    category: Optional[Category] = Relationship(back_populates="splits")

# --- MÓDULOS ADICIONALES ---

class Budget(SoftDeleteMixin, table=True):
    __tablename__ = "budgets"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    period_type: str = Field(default="MONTHLY")  # MONTHLY, YEARLY, CUSTOM
    start_date: date
    end_date: date
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lines: List["BudgetLine"] = Relationship(back_populates="budget")

class BudgetLine(SQLModel, table=True):
    __tablename__ = "budget_lines"
    id: Optional[int] = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="budgets.id")
    category_id: int = Field(foreign_key="categories.id")
    allocated_amount: Decimal = Field(max_digits=20, decimal_places=8)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    budget: Optional[Budget] = Relationship(back_populates="lines")

class SavingGoal(SoftDeleteMixin, table=True):
    __tablename__ = "saving_goals"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    name: str
    target_amount: Decimal = Field(max_digits=20, decimal_places=8)
    current_amount: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    target_date: Optional[date] = None
    currency_code: str = Field(foreign_key="currencies.code")
    color: str = Field(default="#0d6efd")
    icon: str = Field(default="fa-bullseye")
    notes: Optional[str] = None
    status: str = Field(default="ACTIVE")
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GoalContribution(SQLModel, table=True):
    __tablename__ = "goal_contributions"
    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: int = Field(foreign_key="saving_goals.id")
    amount: Decimal = Field(max_digits=20, decimal_places=8)
    transaction_id: Optional[int] = Field(default=None, foreign_key="transactions.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- ACTIVOS E INVERSIONES ---

class Asset(SoftDeleteMixin, table=True):
    __tablename__ = "assets"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    type: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(default=None, max_digits=20, decimal_places=8)
    currency_code: str = Field(foreign_key="currencies.code")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssetValuation(SQLModel, table=True):
    __tablename__ = "asset_valuations"
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="assets.id", ondelete="CASCADE")
    valuation_date: date
    amount: Decimal = Field(max_digits=20, decimal_places=8)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Investment(SoftDeleteMixin, table=True):
    __tablename__ = "investments"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    symbol: str = Field(index=True)
    name: str
    type: str # STOCK, CRYPTO, etc.
    currency_code: str = Field(foreign_key="currencies.code")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvestmentTransaction(SQLModel, table=True):
    __tablename__ = "investment_transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    investment_id: int = Field(foreign_key="investments.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id")
    account_id: int = Field(foreign_key="accounts.id")
    date: datetime
    type: str # BUY, SELL
    quantity: Decimal = Field(max_digits=20, decimal_places=8)
    price_per_unit: Decimal = Field(max_digits=20, decimal_places=8)
    commission: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    taxes: Decimal = Field(default=0, max_digits=20, decimal_places=8)
    total_amount: Decimal = Field(max_digits=20, decimal_places=8)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvestmentPrice(SQLModel, table=True):
    __tablename__ = "investment_prices"
    id: Optional[int] = Field(default=None, primary_key=True)
    investment_id: int = Field(foreign_key="investments.id", ondelete="CASCADE")
    price_date: datetime = Field(default_factory=datetime.utcnow)
    price: Decimal = Field(max_digits=20, decimal_places=8)
    source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- SISTEMA DE METADATOS (KVP SLOTS) ---

class CustomField(SQLModel, table=True):
    __tablename__ = "custom_fields"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    entity_type: str # ACCOUNT, TRANSACTION, etc.
    name: str
    type: str # STRING, NUMBER, DATE, BOOLEAN
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomFieldValue(SQLModel, table=True):
    __tablename__ = "custom_field_values"
    id: Optional[int] = Field(default=None, primary_key=True)
    field_id: int = Field(foreign_key="custom_fields.id", ondelete="CASCADE")
    entity_id: int
    value: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# --- BÓVEDA DIGITAL (VAULT) ---

class Directory(SoftDeleteMixin, table=True):
    __tablename__ = "directories"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="directories.id")
    path: str  # Full computed path, e.g. "/Facturas/2024"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Attachment(SoftDeleteMixin, table=True):
    __tablename__ = "attachments"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    entity_type: Optional[str] = None     # 'transaction', 'account', etc.
    entity_id: Optional[int] = None       # FK a la entidad relacionada
    original_filename: str                # Nombre original del archivo subido
    generated_filename: str              # Nombre generado: YYMMDD_hhmm_COD1_COD2.ext
    file_path: str                        # Ruta fisica completa en disco
    directory_id: Optional[int] = Field(default=None, foreign_key="directories.id")
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- AUDITORÍA Y PLUGINS ---

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    old_values: Optional[str] = None # JSON string
    new_values: Optional[str] = None # JSON string
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Plugin(SQLModel, table=True):
    """
    Represents a module or plugin of the system.
    Inspired by PrestaShop's modular architecture.
    """
    __tablename__ = "plugins"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    technical_name: str = Field(unique=True, index=True) # e.g.: "ia_ocr", "gmail_connector"
    display_name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    author: str = "3F Core"
    
    # Lifecycle states
    is_installed: bool = Field(default=False)
    is_active: bool = Field(default=False)
    
    # Flexible metadata
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    subscribed_hooks: str = Field(default="") # Comma-separated list of hooks
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SystemConfig(AuditMixin, table=True):
    __tablename__ = "system_config"
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
