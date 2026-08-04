import pytest
import sqlite3
import os
import tempfile
import json
from services.song_service import merge_songs
from services.stats_service import calculate_song_stats
from services.backup_service import export_to_json, import_from_json

@pytest.fixture
def db_conn():
    import database
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, 'test.db')
    original_path = database.DB_PATH
    database.DB_PATH = test_db_path
    
    database.init_db()
    conn = database.get_db()
    
    yield conn
    
    conn.close()
    database.DB_PATH = original_path

def test_unique_video_id(db_conn):
    db_conn.execute("INSERT INTO songs (id, title) VALUES (1, 'Song 1')")
    db_conn.execute("INSERT INTO videos (id, song_id, title) VALUES ('vid1', 1, 'Video 1')")
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute("INSERT INTO videos (id, song_id, title) VALUES ('vid1', 1, 'Video 2')")

def test_merge_songs_sums_views(db_conn):
    db_conn.execute("INSERT INTO songs (id, title) VALUES (1, 'Song 1')")
    db_conn.execute("INSERT INTO songs (id, title) VALUES (2, 'Song 2')")
    db_conn.execute("INSERT INTO videos (id, song_id, view_count, status, published_at) VALUES ('vid1', 1, 100, 'active', '2023-01-01')")
    db_conn.execute("INSERT INTO videos (id, song_id, view_count, status, published_at) VALUES ('vid2', 2, 200, 'active', '2023-01-01')")
    db_conn.execute("INSERT INTO videos (id, song_id, view_count, status, published_at) VALUES ('vid3', 2, 300, 'excluded', '2023-01-01')")
    db_conn.commit()

    merge_songs([1, 2], None, 'Merged Song', None, [])
    
    stats = calculate_song_stats(db_conn)
    active_songs = db_conn.execute("SELECT id FROM songs WHERE is_archived = 0").fetchall()
    assert len(active_songs) == 1
    new_id = active_songs[0]['id']
    
    assert stats[new_id]['total_views'] == 300

def test_date_calculation(db_conn):
    db_conn.execute("INSERT INTO songs (id, title, use_manual_date, manual_base_date) VALUES (1, 'Song 1', 0, '2020-01-01')")
    db_conn.execute("INSERT INTO videos (id, song_id, view_count, status, published_at) VALUES ('vid1', 1, 100, 'active', '2022-05-01T00:00:00Z')")
    db_conn.execute("INSERT INTO videos (id, song_id, view_count, status, published_at) VALUES ('vid2', 1, 100, 'active', '2021-03-01T00:00:00Z')")
    db_conn.commit()
    
    stats = calculate_song_stats(db_conn)
    assert stats[1]['auto_base_date'] == '2021-03-01'
    assert stats[1]['effective_base_date'] == '2021-03-01'
    
    db_conn.execute("UPDATE songs SET use_manual_date = 1 WHERE id = 1")
    db_conn.commit()
    stats = calculate_song_stats(db_conn)
    assert stats[1]['effective_base_date'] == '2020-01-01'

def test_backup_restore(db_conn):
    db_conn.execute("INSERT INTO settings (key, value) VALUES ('test', 'value')")
    db_conn.commit()
    
    json_str = export_to_json()
    data = json.loads(json_str)
    assert 'artists' in data
    assert 'YOUTUBE_API_KEY' not in json_str 
    
    db_conn.execute("DELETE FROM settings")
    db_conn.commit()
    
    import_from_json(json_str)
    settings = db_conn.execute("SELECT * FROM settings").fetchall()
    assert len(settings) == 1
    assert settings[0]['value'] == 'value'
