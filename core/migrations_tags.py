import sqlite3
import os
import json
import datetime
import uuid

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'app.db')

INITIAL_TAGS = [
    {"id": "tag_excluded", "name": "排除", "colorKey": "pink", "backgroundColor": "#F5E0E9", "textColor": "#9D174D"},
    {"id": "tag_ohako", "name": "おはこ", "colorKey": "blue", "backgroundColor": "#DDEBF1", "textColor": "#245B78"},
    {"id": "tag_high_pitch", "name": "高温練習", "colorKey": "red", "backgroundColor": "#FFE2DD", "textColor": "#D44C47"},
    {"id": "tag_party", "name": "盛上", "colorKey": "gray", "backgroundColor": "#E3E2E0", "textColor": "#5A5A5A"},
    {"id": "tag_okinawa", "name": "沖縄", "colorKey": "brown", "backgroundColor": "#EEE0DA", "textColor": "#64473A"},
    {"id": "tag_hiphop", "name": "HIPHOP", "colorKey": "green", "backgroundColor": "#DBEDDB", "textColor": "#0F7B6C"}
]

TAG_MAPPING = {
    "排除": "tag_excluded",
    "おはこ": "tag_ohako",
    "高温練習": "tag_high_pitch",
    "高音練習": "tag_high_pitch",
    "盛上": "tag_party",
    "盛り上がり": "tag_party",
    "沖縄": "tag_okinawa",
    "HIPHOP": "tag_hiphop",
    "HipHop": "tag_hiphop",
    "Hip-Hop": "tag_hiphop",
}

def migrate_tags() -> None:
    """
    Migrate tags from JSON string lists in songs/artists to the unified tags system.
    """
    print("Starting tags migration...")
    if not os.path.exists(DB_PATH):
        print("Database not found. Skipping.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tag_definitions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                color_key TEXT NOT NULL,
                background_color TEXT NOT NULL,
                text_color TEXT NOT NULL,
                display_order INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS song_tags (
                song_id INTEGER NOT NULL,
                tag_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (song_id, tag_id),
                FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tag_definitions(id)
            )
        """)

        # Insert initial tags if they don't exist
        now = datetime.datetime.now().isoformat()
        
        for i, tag in enumerate(INITIAL_TAGS):
            order = i + 1
            # Use INSERT OR IGNORE, but if it exists, maybe update it? Let's just INSERT OR IGNORE for safety
            conn.execute("""
                INSERT OR IGNORE INTO tag_definitions 
                (id, name, color_key, background_color, text_color, display_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (tag['id'], tag['name'], tag['colorKey'], tag['backgroundColor'], tag['textColor'], order, now, now))
        
        # Migrate existing data
        songs = conn.execute("SELECT id, tag_b FROM songs WHERE tag_b IS NOT NULL AND tag_b != '' AND tag_b != '[]'").fetchall()
        
        migrated_count = 0
        unknown_tags = {} # name -> id
        max_order = len(INITIAL_TAGS)
        
        for song in songs:
            song_id = song['id']
            tag_b_val = song['tag_b']
            
            tags_to_add = []
            try:
                # Try parsing as JSON array
                parsed = json.loads(tag_b_val)
                if isinstance(parsed, list):
                    tags_to_add = [str(x).strip() for x in parsed if str(x).strip()]
                else:
                    tags_to_add = [str(parsed).strip()]
            except json.JSONDecodeError:
                # Fallback to comma separation
                tags_to_add = [x.strip() for x in tag_b_val.split(',') if x.strip()]
                
            for t_name in tags_to_add:
                # Map to tag_id
                tag_id = TAG_MAPPING.get(t_name)
                
                if not tag_id:
                    # Unknown tag. Check if it's already in db by name (maybe from previous run)
                    row = conn.execute("SELECT id FROM tag_definitions WHERE name = ?", (t_name,)).fetchone()
                    if row:
                        tag_id = row['id']
                    else:
                        if t_name in unknown_tags:
                            tag_id = unknown_tags[t_name]
                        else:
                            # Create new tag
                            max_order += 1
                            new_id = f"tag_{uuid.uuid4().hex[:8]}"
                            unknown_tags[t_name] = new_id
                            tag_id = new_id
                            conn.execute("""
                                INSERT INTO tag_definitions 
                                (id, name, color_key, background_color, text_color, display_order, is_active, created_at, updated_at)
                                VALUES (?, ?, 'default', '#f1f1f1', '#333333', ?, 1, ?, ?)
                            """, (new_id, t_name, max_order, now, now))
                            print(f"Created new unknown tag: {t_name} ({new_id})")

                # Insert into song_tags
                try:
                    conn.execute("INSERT INTO song_tags (song_id, tag_id, created_at) VALUES (?, ?, ?)", (song_id, tag_id, now))
                    migrated_count += 1
                except sqlite3.IntegrityError:
                    pass # already exists (duplicate tag in array)
                    
        conn.commit()
        print(f"Migration completed successfully. Migrated {migrated_count} tag relations.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_tags()
