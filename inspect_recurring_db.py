"""
Check transacciones_programadas table structure
"""
import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Fer21gon',
        database='futuroforbes_db'
    )
    cursor = conn.cursor()
    
    print("Checking if table exists...")
    cursor.execute("SHOW TABLES LIKE 'transacciones_programadas'")
    if not cursor.fetchone():
        print("Table does NOT exist.")
    else:
        print("Table exists. Columns:")
        cursor.execute("DESCRIBE transacciones_programadas")
        for col in cursor.fetchall():
            print(f"  {col[0]}: {col[1]}")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
