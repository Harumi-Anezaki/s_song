import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'app.db')

def migrate_db() -> None:
    """
    Migrate the database to support Notion-like UI features.
    Creates settings, filters, database_views, and tags tables.
    """
    print("Starting Notion-like views migrations...")
    if not os.path.exists(DB_PATH):
        print("Database not found. Skipping migrations.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # Check songs columns
        songs_info = conn.execute("PRAGMA table_info(songs)").fetchall()
        songs_columns = [col['name'] for col in songs_info]
        if 'extra_properties' not in songs_columns:
            print("Adding 'extra_properties' to 'songs' table...")
            conn.execute("ALTER TABLE songs ADD COLUMN extra_properties TEXT DEFAULT '{}'")
            
        # Check artists columns
        artists_info = conn.execute("PRAGMA table_info(artists)").fetchall()
        artists_columns = [col['name'] for col in artists_info]
        if 'extra_properties' not in artists_columns:
            print("Adding 'extra_properties' to 'artists' table...")
            conn.execute("ALTER TABLE artists ADD COLUMN extra_properties TEXT DEFAULT '{}'")

        # Create custom_schemas table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_schemas (
                id TEXT PRIMARY KEY,
                target_table TEXT NOT NULL,
                key TEXT NOT NULL,
                label TEXT NOT NULL,
                type TEXT NOT NULL,
                options TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create views table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS views (
                id TEXT PRIMARY KEY,
                target_table TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                config TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("Migrations completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
