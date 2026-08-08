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
    # We will use formula to reference artist data if we can, or just standard columns if backend returns them
    insert_schema(conn, 'artists', 'name', '名前', 'title')
    insert_schema(conn, 'artists', 'rating', '歌手_好き度', 'number')
    insert_schema(conn, 'artists', 'singability', '歌手_歌いやすさ', 'number')
    insert_schema(conn, 'artists', 'main_songs', '歌手_曲(メイン)', 'relation')
    insert_schema(conn, 'artists', 'sub_songs', '歌手_曲(サブ)', 'relation')
    
    # 歌手の全体再生数と回/日 
    insert_schema(conn, 'artists', 'total_views_calc', '歌手_再生数', 'rollup')
    insert_schema(conn, 'artists', 'vpd_calc', '歌手_回/日', 'rollup')
    
    # Thresholds are formula columns referencing the native fields
    insert_schema(conn, 'artists', 'view_threshold', '歌手_再生数_上位70%', 'formula', 'prop("view_threshold")')
    insert_schema(conn, 'artists', 'vpd_threshold', '歌手_回/日_上位70%', 'formula', 'prop("vpd_threshold")')
    
    # 作成日時
    insert_schema(conn, 'artists', 'created_at', '作成日時', 'date')
    
    conn.commit()

print("Artist schema inserted")
