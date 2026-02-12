from sqlmodel import Session, create_engine, select, SQLModel, text
from backend.models.models import (
    Usuario, Divisa, ListaCuentas, Beneficiario, 
    Categoria, LibroTransacciones, IdentidadFinanciera,
    TipoEntidadFinanciera
)
from decimal import Decimal
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup engines
SRC_URL = "mysql+pymysql://root:@localhost:3306/temp_recovery"
DEST_URL = os.getenv("DATABASE_URL")

src_engine = create_engine(SRC_URL)
dest_engine = create_engine(DEST_URL)

def migrate():
    print("🚀 Iniciando migración de datos...")
    
    with Session(src_engine) as src_session, Session(dest_engine) as dest_session:
        # 1. Map Divisas
        print("💱 Mapeando divisas...")
        divisa_map = {} # old_id -> new_id
        src_divisas = src_session.execute(text("SELECT id_divisa, nombre_divisa, simbolo_prefijo FROM divisas")).all()
        for d_id, d_nom, d_iso in src_divisas:
            # En el dump, d_iso es 'simbolo_prefijo' (e.g. 'ARS', 'USD')
            dest_d = dest_session.exec(select(Divisa).where(Divisa.codigo_iso == d_iso)).first()
            if not dest_d:
                 new_d = Divisa(nombre_divisa=d_nom or d_iso, codigo_iso=d_iso, simbolo_prefijo="$", tipo_divisa="Fiat")
                 dest_session.add(new_d)
                 dest_session.commit()
                 dest_session.refresh(new_d)
                 divisa_map[d_id] = new_d.id_divisa
            else:
                 divisa_map[d_id] = dest_d.id_divisa
        
        # 2. Map Usuarios (No hay en origen, usamos el default id=1)
        print("👤 Usando usuario por defecto (ID: 1)...")
        default_user_id = 1
        # Asegurarnos que el usuario 1 exista
        dest_u1 = dest_session.get(Usuario, 1)
        if not dest_u1:
             print("⚠️ Usuario 1 no encontrado en destino. Creándolo...")
             new_u = Usuario(id_usuario=1, email="admin@3f.com", password="pbkdf2:sha256:...", rol_id=1)
             dest_session.add(new_u)
             dest_session.commit()

        # 3. Categorias
        print("📂 Migrando categorías...")
        cat_map = {} # old_id -> new_id
        src_cats = src_session.execute(text("SELECT * FROM categorias")).all()
        for c in src_cats:
            dest_c = dest_session.exec(select(Categoria).where(Categoria.nombre_categoria == c.nombre_categoria)).first()
            if not dest_c:
                new_c = Categoria(
                    nombre_categoria=c.nombre_categoria,
                    id_padre=None, color=None, notas=None
                )
                dest_session.add(new_c)
                dest_session.commit()
                dest_session.refresh(new_c)
                cat_map[c.id_categoria] = new_c.id_categoria
            else:
                cat_map[c.id_categoria] = dest_c.id_categoria

        # 4. Beneficiarios
        print("🤝 Migrando beneficiarios...")
        ben_map = {} # old_id -> new_id
        src_bens = src_session.execute(text("SELECT * FROM beneficiarios")).all()
        for b in src_bens:
            dest_b = dest_session.exec(select(Beneficiario).where(Beneficiario.nombre_beneficiario == b.nombre_beneficiario)).first()
            if not dest_b:
                new_b = Beneficiario(
                    nombre_beneficiario=b.nombre_beneficiario, 
                    id_categoria=cat_map.get(b.id_categoria), 
                    notas=b.notas or ""
                )
                dest_session.add(new_b)
                dest_session.commit()
                dest_session.refresh(new_b)
                ben_map[b.id_beneficiario] = new_b.id_beneficiario
            else:
                ben_map[b.id_beneficiario] = dest_b.id_beneficiario

        # 5. Cuentas (Integración con Entidades Financieras)
        print("🏦 Migrando cuentas y vinculando entidades...")
        acc_map = {} # old_id -> new_id
        src_accs = src_session.execute(text("SELECT * FROM lista_cuentas")).all()
        
        tipo_otro = dest_session.exec(select(TipoEntidadFinanciera).where(TipoEntidadFinanciera.nombre_tipo == "Otro")).first()
        id_tipo_otro = tipo_otro.id_tipo if tipo_otro else 1

        for a in src_accs:
            id_identidad = None
            if hasattr(a, 'entidad_financiera') and a.entidad_financiera:
                ident = dest_session.exec(select(IdentidadFinanciera).where(IdentidadFinanciera.nombre == a.entidad_financiera)).first()
                if not ident:
                    ident = IdentidadFinanciera(nombre=a.entidad_financiera, id_tipo=id_tipo_otro, activo=True)
                    dest_session.add(ident)
                    dest_session.commit()
                    dest_session.refresh(ident)
                id_identidad = ident.id_identidad

            dest_a = dest_session.exec(select(ListaCuentas).where(ListaCuentas.nombre_cuenta == a.nombre_cuenta)).first()
            
            new_id_divisa = divisa_map.get(a.id_divisa, 1)

            if not dest_a:
                new_a = ListaCuentas(
                    nombre_cuenta=a.nombre_cuenta, tipo_cuenta=a.tipo_cuenta,
                    numero_cuenta=a.numero_cuenta, estado=a.estado, notas=a.notas,
                    id_identidad_financiera=id_identidad, sitio_web=a.sitio_web,
                    saldo_inicial=a.saldo_inicial, id_divisa=new_id_divisa
                )
                dest_session.add(new_a)
                dest_session.commit()
                dest_session.refresh(new_a)
                acc_map[a.id_cuenta] = new_a.id_cuenta
            else:
                acc_map[a.id_cuenta] = dest_a.id_cuenta

        # 6. Transacciones (The big one)
        print("💸 Migrando transacciones (esto puede tardar)...")
        src_txs = src_session.execute(text("SELECT * FROM libro_transacciones")).all()
        count = 0
        for t in src_txs:
            new_acc_id = acc_map.get(t.id_cuenta)
            new_cat_id = cat_map.get(t.id_categoria)
            new_ben_id = ben_map.get(t.id_beneficiario)

            if not new_acc_id: continue 

            new_tx = LibroTransacciones(
                id_cuenta=new_acc_id, 
                id_categoria=new_cat_id,
                id_beneficiario=new_ben_id or 1, # Default placeholder if none
                monto_transaccion=t.monto_transaccion,
                fecha_transaccion=t.fecha_transaccion, 
                notas=t.notas,
                codigo_transaccion=t.codigo_transaccion
            )
            dest_session.add(new_tx)
            count += 1
            if count % 500 == 0:
                dest_session.commit()
                print(f"  - {count} transacciones procesadas...")
        
        dest_session.commit()
        print(f"✅ Migración finalizada. Total: {count} transacciones.")

if __name__ == "__main__":
    migrate()
