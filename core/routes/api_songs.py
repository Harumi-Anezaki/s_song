from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

bp_songs = Blueprint('bp_songs', __name__)

@bp_songs.route('/api/songs', methods=['GET', 'POST'])
def api_songs() -> Any:
    """
    api_songs function.
    """
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.execute("INSERT INTO songs (title, created_at, updated_at) VALUES (?, datetime('now', 'localtime'), datetime('now', 'localtime'))", ('新規曲',))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
            
    with get_db() as conn:
        songs = conn.execute("SELECT * FROM songs WHERE is_archived = 0").fetchall()
        return jsonify([dict(s) for s in songs])


@bp_songs.route('/api/songs/<int:song_id>', methods=['GET'])
def api_song_detail(song_id: Any) -> Any:
    """
    api_song_detail function.
    """
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


@bp_songs.route('/api/songs/<int:song_id>', methods=['PUT'])
def api_update_song(song_id: Any) -> Any:
    """
    api_update_song function.
    """
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


@bp_songs.route('/api/songs/merge', methods=['POST'])
def api_merge_songs() -> Any:
    """
    api_merge_songs function.
    """
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


@bp_songs.route('/api/database_view/songs', methods=['GET'])
def api_db_view_songs() -> Any:
    """
    api_db_view_songs function.
    """
    from services.stats_service import get_database_songs
    return jsonify(get_database_songs())


@bp_songs.route('/api/songs/<int:song_id>', methods=['PATCH'])
def api_update_song_partial(song_id: Any) -> Any:
    """
    api_update_song_partial function.
    """
    data = request.json
    allowed_fields = ['title', 'main_artist_id', 'tag_a', 'tag_b', 'dl_status', 'manual_base_date', 'use_manual_date', 'primary_video_id', 'memo']
    updates = []
    params = []
    
    extra_updates = {}
    has_extra = False
    
    for k, v in data.items():
        if k == 'tag_b_list':
            import json
            tag_b_ids = []
            if isinstance(v, str):
                tag_b_ids = [x.strip() for x in v.replace(' ', ',').split(',') if x.strip()]
            elif isinstance(v, list):
                tag_b_ids = v
            updates.append("tag_b = ?")
            params.append(json.dumps(tag_b_ids))
        elif k == 'effective_base_date':
            updates.append("manual_base_date = ?")
            params.append(v)
            updates.append("use_manual_date = ?")
            params.append(1 if v else 0)
        elif k in allowed_fields:
            if k == 'tag_b':
                import json
                updates.append(f"{k} = ?")
                params.append(json.dumps(v) if isinstance(v, list) else v)
            else:
                updates.append(f"{k} = ?")
                params.append(v)
        elif k not in ['sub_artist_ids', 'sub_artists']:
            extra_updates[k] = v
            has_extra = True
                
    if not updates and not has_extra and 'sub_artist_ids' not in data and 'sub_artists' not in data and 'tag_b_list' not in data:
        return jsonify({'error': 'No valid fields provided'}), 400
        
    try:
        with get_db() as conn:
            if has_extra:
                # fetch current extra_properties
                import json
                row = conn.execute("SELECT extra_properties FROM songs WHERE id = ?", (song_id,)).fetchone()
                if row:
                    try:
                        current_extra = json.loads(row['extra_properties'] or '{}')
                    except:
                        current_extra = {}
                    
                    for ek, ev in extra_updates.items():
                        current_extra[ek] = ev
                    
                    updates.append("extra_properties = ?")
                    params.append(json.dumps(current_extra))
                    
            if updates:
                query = f"UPDATE songs SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                params.append(song_id)
                conn.execute(query, tuple(params))
                

                        
            if 'sub_artist_ids' in data:
                sub_ids = data['sub_artist_ids']
                conn.execute("DELETE FROM song_sub_artists WHERE song_id = ?", (song_id,))
                for sid in sub_ids:
                    conn.execute("INSERT INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (song_id, sid))
                    
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_songs.route('/api/songs/<int:song_id>', methods=['DELETE'])
def api_delete_song(song_id: Any) -> Any:
    """
    api_delete_song function.
    """
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


