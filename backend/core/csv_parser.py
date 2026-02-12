import csv
import io
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

class CSVParser:
    """
    Universal CSV Parser for Bank Statements.
    Attempts to auto-detect columns: date, description, and amount.
    """
    
    # Common header names to look for
    COLUMN_MAP = {
        "fecha": ["fecha", "date", "fec", "day", "vencimiento"],
        "descripcion": ["descripcion", "concepto", "detalle", "detail", "description", "notas", "notas/comentario"],
        "monto": ["monto", "importe", "amount", "valor", "balance", "total", "value"],
    }

    def __init__(self, content: bytes, delimiter: str = ","):
        self.content = content
        self.delimiter = delimiter
        self.df: Optional[pd.DataFrame] = None

    def parse(self) -> List[Dict[str, Any]]:
        """Parses CSV and returns a list of normalized dictionaries"""
        try:
            # Detect encoding and read with pandas for flexibility
            # Using io.BytesIO to keep everything in memory
            self.df = pd.read_csv(io.BytesIO(self.content), sep=self.delimiter)
            
            # Normalize column names (lowercase and strip)
            self.df.columns = [c.lower().strip() for c in self.df.columns]
            
            mapping = self._detect_columns()
            normalized_data = []
            
            for _, row in self.df.iterrows():
                try:
                    raw_date = str(row.get(mapping["fecha"], ""))
                    raw_monto = str(row.get(mapping["monto"], "0"))
                    
                    # Clean amount (remove symbols, handles commas as decimals or thousands)
                    monto = self._clean_amount(raw_monto)
                    
                    entry = {
                        "fecha": self._parse_date(raw_date),
                        "descripcion": str(row.get(mapping["descripcion"], "")),
                        "monto": monto,
                        "raw_row": row.to_dict()
                    }
                    normalized_data.append(entry)
                except Exception as e:
                    # Skip rows that definitely aren't transactions (headers, footers)
                    continue
            
            return normalized_data
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

    def _detect_columns(self) -> Dict[str, str]:
        """Maps CSV headers to internal keys using fuzzy matching"""
        mapping = {}
        for internal_key, candidates in self.COLUMN_MAP.items():
            found = False
            for col in self.df.columns:
                if any(cand in col for cand in candidates):
                    mapping[internal_key] = col
                    found = True
                    break
            if not found:
                # If not found, use a placeholder or raise error if critical
                mapping[internal_key] = self.df.columns[0] # Fallback
        return mapping

    def _clean_amount(self, value: str) -> Decimal:
        """Cleans currency strings into Decimal"""
        if not value: return Decimal("0")
        # Remove currency symbols and spaces
        clean_val = str(value).replace("$", "").replace("€", "").replace("£", "").strip()
        
        # Helper to check if string is a valid number
        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        if not clean_val:
            return Decimal("0")

        # Heuristics for thousands/decimal separators
        if "," in clean_val and "." in clean_val:
            # Both present. The one that appears last is likely the decimal separator
            last_comma = clean_val.rfind(",")
            last_dot = clean_val.rfind(".")
            
            if last_comma > last_dot:
                # 1.000,00 -> remove dots, replace comma with dot
                clean_val = clean_val.replace(".", "").replace(",", ".")
            else:
                # 1,000.00 -> remove commas
                clean_val = clean_val.replace(",", "")
        elif "," in clean_val:
            # Only comma. Ambiguous: 1,000 (one thousand) or 1,00 (one)
            # Assumption: If 1 or 2 digits after comma, it's decimal. If 3, it's thousands.
            parts = clean_val.split(",")
            if len(parts) > 1 and len(parts[-1]) == 3 and is_number(parts[-1]): 
                 # Likely thousands separator: 100,000
                 clean_val = clean_val.replace(",", "")
            else:
                 # Likely decimal separator: 10,5 or 100,00
                 clean_val = clean_val.replace(",", ".")
        # If only dot, usually standard decimal (10.5) or thousands (1.000)
        # But standard python float handles 10.5. 
        # For 1.000 (one thousand), it's ambiguous. We assume dot is decimal unless multiple dots.
        
        try:
            return Decimal(clean_val)
        except:
            return Decimal("0")

    def _parse_date(self, value: str) -> str:
        """Attempts to parse varied date formats into ISO string"""
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", 
            "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y",
            "%d/%m/%y", "%m/%d/%y", "%d-%m-%y", # Short year
            "%d %b %Y", "%d %B %Y" # Text months
        ]
        value = str(value).strip()
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except:
                continue
        
        # Fail strategy: Return today or raise error? 
        # For now, return the original string to let SQL/Pydantic fail or handle it
        return value
