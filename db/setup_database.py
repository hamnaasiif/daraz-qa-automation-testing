"""
Setup SQLite database with test data
"""
import sqlite3
import os

def create_database():
    """Create test database with sample data"""
    
    # Database path
    db_path = 'db/test_data.db'
    
    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Old database removed")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create search_terms table
    cursor.execute('''
        CREATE TABLE search_terms (
            id INTEGER PRIMARY KEY,
            term TEXT NOT NULL,
            category TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    print("Table 'search_terms' created")
    
    # Insert sample data
    search_data = [
        ('laptop', 'Electronics', 1),
        ('mobile', 'Electronics', 1),
        ('headphones', 'Electronics', 1),
        ('shoes', 'Fashion', 1),
        ('watch', 'Accessories', 1)
    ]
    
    cursor.executemany(
        'INSERT INTO search_terms (term, category, is_active) VALUES (?, ?, ?)',
        search_data
    )
    
    conn.commit()
    print(f"Inserted {len(search_data)} search terms")
    
    # Verify data
    cursor.execute('SELECT * FROM search_terms')
    rows = cursor.fetchall()
    print(f"\nDatabase contents:")
    for row in rows:
        print(f"   {row}")
    
    conn.close()
    print("\nDatabase created successfully!")
    print(f"📍 Location: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    create_database()