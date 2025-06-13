import sqlite3

def check_column_order():
    """Check the actual column order in your structures table"""
    db_path = "structures.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get column information
            cursor.execute("PRAGMA table_info(structures)")
            columns_info = cursor.fetchall()
            
            print("Current column order in structures table:")
            print("Index | Column Name | Type | NotNull | Default | PrimaryKey")
            print("-" * 60)
            
            for col in columns_info:
                print(f"{col[0]:5} | {col[1]:15} | {col[2]:8} | {col[3]:7} | {str(col[4]):7} | {col[5]}")
            
            # Also get a sample row to see what data looks like
            cursor.execute("SELECT * FROM structures LIMIT 1")
            sample_row = cursor.fetchone()
            
            if sample_row:
                print(f"\nSample row data:")
                for i, value in enumerate(sample_row):
                    column_name = columns_info[i][1] if i < len(columns_info) else f"col_{i}"
                    print(f"{i:2}: {column_name:20} = {value}")
            else:
                print("\nNo data in structures table")
                
    except sqlite3.Error as e:
        print(f"Error checking columns: {e}")

if __name__ == "__main__":
    check_column_order()