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
        clean_val = value.replace("$", "").replace("€", "").replace("£", "").strip()
        
        # Heuristic for continental vs anglo notation:
        # If there's a comma AND a dot: remove comma (thousands) if dot is decimal
        # If there's multiple dots: they are thousands
        if "," in clean_val and "." in clean_val:
            if clean_val.find(",") < clean_val.find("."):
                clean_val = clean_val.replace(",", "") # Anglo: 1,000.00
            else:
                clean_val = clean_val.replace(".", "").replace(",", ".") # Continental: 1.000,00
        elif "," in clean_val:
            # Check if comma looks like decimal (last positions)
            if clean_val.count(",") == 1 and len(clean_val.split(",")[1]) <= 2:
                clean_val = clean_val.replace(",", ".")
            else:
                clean_val = clean_val.replace(",", "")
        
        try:
            return Decimal(clean_val)
        except:
            return Decimal("0")

    def _parse_date(self, value: str) -> str:
        """Attempts to parse varied date formats into ISO string"""
        formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", 
            "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date().isoformat()
            except:
                continue
        return value # Return as is if failed
