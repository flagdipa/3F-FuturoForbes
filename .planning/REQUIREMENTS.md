# Requirements - 3F v1.0

## 🎯 Goal
Stabilize the existing brownfield codebase into a production-ready v1.0 version for personal financial management.

## 🏗️ Core Functional Requirements
- **Ledger Reliability**: Finalize and audit the `LedgerEngine` to ensure accurate balance calculations across all account types (ASSET, LIABILITY, etc.).
- **Transaction Management**: 
  - Complete CRUD for transactions.
  - Support for multi-category and multi-account splits (Double-Entry).
  - Bulk transaction import (CSV/Excel).
- **Organization**:
  - Hierarchical category management.
  - Payee/Beneficiary database with default category mapping.
- **Reporting**:
  - Integrated Cashflow analysis.
  - Expense Heatmaps.
  - Account forecast (Financial projection).
- **Automation**:
  - Functional plugin system.
  - **PaddleOCR Integration**: Automatic receipt parsing into transaction drafts.
- **Security**:
  - Local authentication (JWT).
  - Encrypted environment variables.

## 🎨 UI/UX Requirements
- **Neon Dashboard**: A fully responsive landing page with key stats (Total Net Worth, Monthly Burn Rate).
- **Dynamic Sidebar**: Reactive account list with real-time balances.
- **Micro-interactions**: Use Alpine.js for smooth state transitions without full page reloads.

## 🛠️ Technical Requirements
- **Database**: SQLModel with Alembic migrations for schema evolution.
- **Testing**: Playwright coverage for critical paths (Login -> Add Transaction -> Verify Balance).
- **Performance**: Optimize SQL queries for calculating balances in sub-200ms.
