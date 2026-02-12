from sqlmodel import Session, create_engine, select, text
from backend.models.models import Beneficiario, LibroTransacciones, ListaCuentas
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup engine
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/3f_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL)

def fix_encoding():
    print("🚀 Iniciando reparación de codificación UTF-8...")
    
    with Session(engine) as session:
        # 1. Fix Beneficiarios
        print("🔧 Analizando Beneficiarios...")
        beneficiarios = session.exec(select(Beneficiario)).all()
        count = 0
        for b in beneficiarios:
            original_name = b.nombre_beneficiario
            
            # Common corruption patterns
            # The specific case reported: 'Naci-|-n' -> 'Nación'
            # This looks like a pipe delimiter issue or specific encoding artifact
            
            new_name = original_name
            
            # Specific Fixes
            if "Naci-|-n" in new_name:
                new_name = new_name.replace("Naci-|-n", "Nación")
            
            # Generic Latin-1/Mojibake fixes
            replacements = {
                "Ã³": "ó",
                "Ã¡": "á",
                "Ã©": "é",
                "Ã": "í", # Sometimes í is just Ã followed by nothing visual or non-printable
                "Ã±": "ñ",
                "Ãº": "ú",
                "â": "–", 
                "Â": "" # Often appears before special chars
            }
            
            # Apply replacements carefully
            # Only apply generic fixes if we didn't just fix a specific one, or do both?
            # Let's do string replacement for the explicit reported case first.
            
            if new_name != original_name:
                b.nombre_beneficiario = new_name
                session.add(b)
                count += 1
                print(f"  📝 Fixed: '{original_name}' -> '{new_name}'")
        
        if count > 0:
            session.commit()
            print(f"✅ Se corrigieron {count} beneficiarios.")
        else:
            print("✨ No se encontraron beneficiarios corruptos conocidos.")

        # 2. Fix Cuentas (if needed)
        print("🔧 Analizando Cuentas...")
        cuentas = session.exec(select(ListaCuentas)).all()
        c_count = 0
        for c in cuentas:
            if "Naci-|-n" in c.nombre_cuenta:
                c.nombre_cuenta = c.nombre_cuenta.replace("Naci-|-n", "Nación")
                session.add(c)
                c_count += 1
                print(f"  📝 Fixed Account: '{c.nombre_cuenta}'")
        
        if c_count > 0:
            session.commit()
            print(f"✅ Se corrigieron {c_count} cuentas.")

    print("🏁 Proceso finalizado.")

if __name__ == "__main__":
    fix_encoding()
