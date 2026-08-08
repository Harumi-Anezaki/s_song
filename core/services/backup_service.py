from typing import Any
import json
import datetime
from database import get_db

def export_to_json() -> Any:
    """
    export_to_json function.
    """
    with get_db() as conn:
        data = {
            'version': '1.0',
            'exported_at': datetime.datetime.now().isoformat(),
            'artists': [dict(row) for row in conn.execute("SELECT * FROM artists").fetchall()],
            'songs': [dict(row) for row in conn.execute("SELECT * FROM songs").fetchall()],
            'song_sub_artists': [dict(row) for row in conn.execute("SELECT * FROM song_sub_artists").fetchall()],
            'videos': [dict(row) for row in conn.execute("SELECT * FROM videos").fetchall()],
            'excluded_videos': [dict(row) for row in conn.execute("SELECT * FROM excluded_videos").fetchall()],
            'search_history': [dict(row) for row in conn.execute("SELECT * FROM search_history").fetchall()],
            'settings': [dict(row) for row in conn.execute("SELECT * FROM settings").fetchall()],
            'tag_definitions': [dict(row) for row in conn.execute("SELECT * FROM tag_definitions").fetchall()],
            'song_tags': [dict(row) for row in conn.execute("SELECT * FROM song_tags").fetchall()],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

def import_from_json(json_str: Any) -> Any:
    """
    import_from_json function.
    """
    data = json.loads(json_str)
    
    with get_db() as conn:
        try:
            # Delete in reverse dependency order
            conn.execute("DELETE FROM song_tags")
            conn.execute("DELETE FROM song_sub_artists")
            conn.execute("DELETE FROM videos")
            conn.execute("DELETE FROM excluded_videos")
            conn.execute("DELETE FROM search_history")
            conn.execute("DELETE FROM songs")
            conn.execute("DELETE FROM tag_definitions")
            conn.execute("DELETE FROM artists")
            conn.execute("DELETE FROM settings")
            
            # Insert parents first
            for t in data.get('tag_definitions', []):
                conn.execute("INSERT INTO tag_definitions (id, name, color_key, background_color, text_color, display_order, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (t['id'], t['name'], t['color_key'], t['background_color'], t['text_color'], t['display_order'], t['is_active'], t['created_at'], t['updated_at']))

            for a in data.get('artists', []):
                conn.execute("INSERT INTO artists (id, name, phonetic_name, rating, memo, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (a['id'], a['name'], a['phonetic_name'], a['rating'], a['memo'], a['created_at'], a['updated_at']))
                             
            for s in data.get('songs', []):
                conn.execute("INSERT INTO songs (id, title, main_artist_id, tag_a, tag_b, dl_status, auto_base_date, manual_base_date, use_manual_date, memo, is_archived, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (s['id'], s['title'], s['main_artist_id'], s['tag_a'], s['tag_b'], s['dl_status'], s['auto_base_date'], s['manual_base_date'], s['use_manual_date'], s['memo'], s['is_archived'], s['created_at'], s['updated_at']))
                             
            for sa in data.get('song_sub_artists', []):
                conn.execute("INSERT INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (sa['song_id'], sa['artist_id']))
                
            for v in data.get('videos', []):
                conn.execute("INSERT INTO videos (id, song_id, title, url, view_count, published_at, channel_id, channel_name, duration_sec, formatted_duration, thumbnail_url, status, last_api_update, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (v['id'], v['song_id'], v['title'], v['url'], v['view_count'], v['published_at'], v['channel_id'], v['channel_name'], v['duration_sec'], v['formatted_duration'], v['thumbnail_url'], v['status'], v['last_api_update'], v['created_at'], v['updated_at']))
                             
            for e in data.get('excluded_videos', []):
                conn.execute("INSERT INTO excluded_videos (id, reason, excluded_at, search_keyword, old_title, old_url, old_channel_name, is_manual_exclusion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (e['id'], e['reason'], e['excluded_at'], e['search_keyword'], e['old_title'], e['old_url'], e['old_channel_name'], e.get('is_manual_exclusion', 1)))
                             
            for sh in data.get('search_history', []):
                conn.execute("INSERT INTO search_history (id, keyword, min_views, created_at) VALUES (?, ?, ?, ?)",
                             (sh['id'], sh['keyword'], sh['min_views'], sh['created_at']))
                             
            for st in data.get('song_tags', []):
                conn.execute("INSERT INTO song_tags (song_id, tag_id, created_at) VALUES (?, ?, ?)", (st['song_id'], st['tag_id'], st['created_at']))
                             
            for setting in data.get('settings', []):
                conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (setting['key'], setting['value']))
                
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
