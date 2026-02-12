from sqlalchemy import create_engine, inspect

SRC_URL = "mysql+pymysql://root:@localhost:3306/temp_recovery"
engine = create_engine(SRC_URL)
inspector = inspect(engine)

tables_to_inspect = ['beneficiarios', 'categorias', 'divisas', 'lista_cuentas']
for table_name in tables_to_inspect:
    print(f"\nTable: {table_name}")
    try:
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
    except Exception as e:
        print(f"  Error inspecting {table_name}: {e}")
