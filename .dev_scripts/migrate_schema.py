import sqlite3
import json
import uuid

def insert_schema(conn, target, key, label, type, expression=None):
    exists = conn.execute("SELECT 1 FROM custom_schemas WHERE target_table=? AND key=?", (target, key)).fetchone()
    if exists:
        if expression is not None:
            options = json.dumps({"expression": expression})
            conn.execute("UPDATE custom_schemas SET label=?, type=?, options=? WHERE target_table=? AND key=?", (label, type, options, target, key))
        else:
            conn.execute("UPDATE custom_schemas SET label=?, type=? WHERE target_table=? AND key=?", (label, type, target, key))
        return
    new_id = f"schema_{uuid.uuid4().hex[:8]}"
    options = json.dumps({"expression": expression}) if expression is not None else None
    conn.execute("INSERT INTO custom_schemas (id, target_table, key, label, type, options) VALUES (?, ?, ?, ?, ?, ?)",
                 (new_id, target, key, label, type, options))

with sqlite3.connect('data/app.db') as conn:
    # 1. Delete the incorrect ones from artists
    keys_to_delete = ['rating', 'singability', 'main_songs', 'sub_songs', 'total_views_calc', 'vpd_calc', 'view_threshold', 'vpd_threshold']
    conn.execute(f"DELETE FROM custom_schemas WHERE target_table='artists' AND key IN ({','.join(['?']*len(keys_to_delete))})", keys_to_delete)
    
    # Also delete 'name' override if any
    conn.execute("DELETE FROM custom_schemas WHERE target_table='artists' AND key='name'")
    
    # 2. Insert into songs
    # We will use formula to reference artist data if we can, or just standard columns if backend returns them
    insert_schema(conn, 'songs', 'artist_rating', '歌手_好き度', 'number')
    insert_schema(conn, 'songs', 'artist_singability', '歌手_歌いやすさ', 'number')
    insert_schema(conn, 'songs', 'main_artist_id', '歌手_曲(メイン)', 'relation')
    insert_schema(conn, 'songs', 'sub_artists', '歌手_曲(サブ)', 'relation')
    
    # 歌手の全体再生数と回/日 (If backend doesn't provide them yet, they will be empty. We will update backend next)
    insert_schema(conn, 'songs', 'artist_total_views', '歌手_再生数', 'rollup')
    insert_schema(conn, 'songs', 'artist_vpd', '歌手_回/日', 'rollup')
    
    # Thresholds are formula columns
    insert_schema(conn, 'songs', 'artist_view_threshold', '歌手_再生数_上位70%', 'formula', 'prop("view_threshold")')
    insert_schema(conn, 'songs', 'artist_vpd_threshold', '歌手_回/日_上位70%', 'formula', 'prop("vpd_threshold")')
    
    conn.commit()

print("Migrated schema to songs table")
