from .models_v2 import (
    User, Currency, ExchangeRate, AccountType, Account, Category, Payee,
    TransactionStatus, Transaction, TransactionSplit, Tag, TransactionTagLink, Budget, BudgetLine,
    SavingGoal, GoalContribution, Asset, AssetValuation, Investment, InvestmentPrice,
    InvestmentTransaction, CustomField, CustomFieldValue, AuditLog, Plugin, SystemConfig
)

metadata_models = [
    User, Currency, ExchangeRate, Account, Category, Payee, 
    Transaction, TransactionSplit, Tag, TransactionTagLink, Budget, BudgetLine, SavingGoal, GoalContribution,
    Asset, AssetValuation, Investment, InvestmentPrice, InvestmentTransaction,
    CustomField, CustomFieldValue, AuditLog, Plugin, SystemConfig
]
