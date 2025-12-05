"""Simple script to view database contents"""
import sqlite3

# Connect to database
conn = sqlite3.connect('skillswap.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
for table in tables:
    print(f"- {table['name']}")

print("\n" + "=" * 60)
print("TABLE CONTENTS")
print("=" * 60)

# Show contents of each table
for table in tables:
    table_name = table['name']
    print(f"\n--- {table_name.upper()} ---")
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if rows:
        # Print column names
        print(", ".join([description[0] for description in cursor.description]))
        print("-" * 60)
        
        # Print rows
        for row in rows:
            print(", ".join([str(value) for value in row]))
        
        print(f"\nTotal: {len(rows)} rows")
    else:
        print("(empty)")

conn.close()
