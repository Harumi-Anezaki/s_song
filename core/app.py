from flask import Flask, render_template, jsonify, request
import os
import threading
from config import Config
from database import init_db, get_db
from services import youtube, song_service, stats_service, backup_service

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/youtube/search', methods=['POST'])
def api_youtube_search():
    data = request.json
    keyword = data.get('keyword')
    max_results = data.get('max_results', 200)
    min_views = data.get('min_views', 0)
    
    if not keyword:
        return jsonify({'error': 'キーワードが必要です'}), 400
        
    try:
        results = youtube.search_videos(keyword, max_results, min_views)
        
        # 既存のDBに存在するかどうか（除外済みか、登録済みか）をチェック
        with get_db() as conn:
            excluded = conn.execute("SELECT id, reason FROM excluded_videos").fetchall()
            excluded_dict = {row['id']: row['reason'] for row in excluded}
            
            registered = conn.execute("SELECT id FROM videos").fetchall()
            registered_set = {row['id'] for row in registered}
            
            for r in results:
                if r['id'] in excluded_dict:
                    r['db_status'] = 'excluded'
                elif r['id'] in registered_set:
                    r['db_status'] = 'registered'
                else:
                    r['db_status'] = 'new'
                    
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/exclude', methods=['POST'])
def api_exclude_video():
    data = request.json
    video_id = data.get('id')
    reason = data.get('reason', '')
    search_keyword = data.get('search_keyword', '')
    title = data.get('title', '')
    url = data.get('url', '')
    channel_name = data.get('channel_name', '')
    
    if not video_id:
        return jsonify({'error': 'ID is required'}), 400
        
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO excluded_videos 
                (id, reason, search_keyword, old_title, old_url, old_channel_name, is_manual_exclusion)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (video_id, reason, search_keyword, title, url, channel_name))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/songs/register_temp', methods=['POST'])
def api_register_temp():
    data = request.json
    videos = data.get('videos', [])
    
    if not videos:
        return jsonify({'error': 'No videos provided'}), 400
        
    try:
        with get_db() as conn:
            for v in videos:
                existing = conn.execute("SELECT id FROM videos WHERE id = ?", (v['id'],)).fetchone()
                if existing:
                    continue
                    
                cursor = conn.execute("INSERT INTO songs (title, tag_b) VALUES (?, ?)", (v['title'], '[]'))
                song_id = cursor.lastrowid
                
                conn.execute("""
                    INSERT INTO videos (id, song_id, title, url, view_count, published_at, channel_id, channel_name, duration_sec, formatted_duration, thumbnail_url, status, last_api_update)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
                """, (
                    v['id'], song_id, v['title'], v['url'], v['view_count'], v['published_at'],
                    v['channel_id'], v['channel_name'], v['duration_sec'], v['formatted_duration'],
                    v['thumbnail_url'], v['last_api_update']
                ))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists', methods=['GET', 'POST'])
def api_artists():
    with get_db() as conn:
        if request.method == 'POST':
            data = request.json
            name = data.get('name')
            if not name:
                return jsonify({'error': 'Name is required'}), 400
            cursor = conn.execute("INSERT INTO artists (name, phonetic_name, rating, memo) VALUES (?, ?, ?, ?)",
                                  (name, data.get('phonetic_name', ''), data.get('rating', 0), data.get('memo', '')))
            conn.commit()
            return jsonify({'id': cursor.lastrowid, 'success': True})
        else:
            artists = conn.execute("SELECT * FROM artists ORDER BY phonetic_name, name").fetchall()
            return jsonify([dict(a) for a in artists])

@app.route('/api/artists/<int:artist_id>', methods=['PUT'])
def api_update_artist(artist_id):
    data = request.json
    with get_db() as conn:
        conn.execute("UPDATE artists SET name=?, phonetic_name=?, rating=?, memo=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (data.get('name'), data.get('phonetic_name'), data.get('rating', 0), data.get('memo'), artist_id))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/songs', methods=['GET'])
def api_songs():
    with get_db() as conn:
        songs = conn.execute("SELECT * FROM songs WHERE is_archived = 0").fetchall()
        return jsonify([dict(s) for s in songs])

@app.route('/api/songs/<int:song_id>', methods=['GET'])
def api_song_detail(song_id):
    with get_db() as conn:
        song = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
        if not song:
            return jsonify({'error': 'Not found'}), 404
            
        videos = conn.execute("SELECT * FROM videos WHERE song_id = ? AND status != 'excluded'", (song_id,)).fetchall()
        
        main_artist = None
        if song['main_artist_id']:
            main_artist = conn.execute("SELECT * FROM artists WHERE id = ?", (song['main_artist_id'],)).fetchone()
            
        sub_artists = conn.execute("""
            SELECT a.* FROM artists a
            JOIN song_sub_artists ssa ON a.id = ssa.artist_id
            WHERE ssa.song_id = ?
        """, (song_id,)).fetchall()
        
        return jsonify({
            'song': dict(song),
            'videos': [dict(v) for v in videos],
            'main_artist': dict(main_artist) if main_artist else None,
            'sub_artists': [dict(a) for a in sub_artists]
        })

@app.route('/api/songs/<int:song_id>', methods=['PUT'])
def api_update_song(song_id):
    data = request.json
    with get_db() as conn:
        try:
            conn.execute("""
                UPDATE songs 
                SET title=?, main_artist_id=?, tag_a=?, tag_b=?, dl_status=?, manual_base_date=?, use_manual_date=?, memo=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (data.get('title'), data.get('main_artist_id'), data.get('tag_a'), data.get('tag_b'), data.get('dl_status'), data.get('manual_base_date'), data.get('use_manual_date', 0), data.get('memo'), song_id))
            
            sub_artist_ids = data.get('sub_artist_ids', [])
            conn.execute("DELETE FROM song_sub_artists WHERE song_id=?", (song_id,))
            for aid in sub_artist_ids:
                conn.execute("INSERT INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (song_id, aid))
            
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/songs/merge', methods=['POST'])
def api_merge_songs():
    data = request.json
    source_ids = data.get('source_ids', [])
    target_id = data.get('target_id')
    new_title = data.get('new_title', '')
    main_artist_id = data.get('main_artist_id')
    sub_artist_ids = data.get('sub_artist_ids', [])
    
    if not source_ids:
        return jsonify({'error': '統合元の曲が選択されていません'}), 400
    if not new_title:
        return jsonify({'error': '統合後の曲名が必要です'}), 400
        
    try:
        final_id = song_service.merge_songs(source_ids, target_id, new_title, main_artist_id, sub_artist_ids)
        return jsonify({'success': True, 'target_id': final_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/views/<view_name>', methods=['GET'])
def api_views(view_name):
    try:
        results = stats_service.get_view_data(view_name)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/export', methods=['GET'])
def api_backup_export():
    try:
        json_data = backup_service.export_to_json()
        return jsonify({'success': True, 'data': json_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/import', methods=['POST'])
def api_backup_import():
    data = request.json
    json_str = data.get('json_str')
    if not json_str:
        return jsonify({'error': 'No data provided'}), 400
        
    try:
        backup_service.import_from_json(json_str)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/update', methods=['POST'])
def api_videos_update():
    data = request.json
    video_ids = data.get('video_ids', [])
    if not video_ids:
        return jsonify({'error': 'No videos specified'}), 400
        
    with get_db() as conn:
        if 'ALL' in video_ids:
            rows = conn.execute("SELECT id FROM videos WHERE status = 'active'").fetchall()
            video_ids = [row['id'] for row in rows]
            
        if not video_ids:
            return jsonify({'success': True, 'message': 'No videos to update', 'updated_count': 0})
            
        try:
            details = youtube.get_video_details(video_ids)
            fetched_ids = {d['id'] for d in details}
            missing_ids = set(video_ids) - fetched_ids
            
            for d in details:
                conn.execute("""
                    UPDATE videos 
                    SET title=?, view_count=?, published_at=?, channel_id=?, channel_name=?, duration_sec=?, formatted_duration=?, thumbnail_url=?, last_api_update=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (d['title'], d['view_count'], d['published_at'], d['channel_id'], d['channel_name'], d['duration_sec'], d['formatted_duration'], d['thumbnail_url'], d['last_api_update'], d['id']))
                
            for mid in missing_ids:
                conn.execute("UPDATE videos SET status='missing', updated_at=CURRENT_TIMESTAMP WHERE id=?", (mid,))
                
            conn.commit()
            return jsonify({
                'success': True,
                'updated_count': len(details),
                'missing_count': len(missing_ids)
            })
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/shutdown', methods=['POST'])
def api_shutdown():
    def kill_server():
        os._exit(0)
    threading.Timer(0.5, kill_server).start()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=app.config['PORT'], debug=(os.getenv('FLASK_ENV', 'development') == 'development'))
