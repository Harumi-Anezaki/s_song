import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'app.db')

def migrate_db() -> None:
    """
    Migrate the database to the latest schema version.
    This creates necessary tables if they do not exist and adds missing columns.
    """
    print("Starting migrations...")
    if not os.path.exists(DB_PATH):
        print("Database not found. Skipping migrations.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # Create view_settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS view_settings (
                view_id TEXT PRIMARY KEY,
                config TEXT
            )
        """)
        
        # Check artists columns
        artists_info = conn.execute("PRAGMA table_info(artists)").fetchall()
        artists_columns = [col['name'] for col in artists_info]
        
        if 'singability' not in artists_columns:
            print("Adding 'singability' to 'artists' table...")
            conn.execute("ALTER TABLE artists ADD COLUMN singability INTEGER DEFAULT 0")
            
        # Check songs columns
        songs_info = conn.execute("PRAGMA table_info(songs)").fetchall()
        songs_columns = [col['name'] for col in songs_info]
        
        if 'primary_video_id' not in songs_columns:
            print("Adding 'primary_video_id' to 'songs' table...")
            conn.execute("ALTER TABLE songs ADD COLUMN primary_video_id TEXT")
            
        conn.commit()
        print("Migrations completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
