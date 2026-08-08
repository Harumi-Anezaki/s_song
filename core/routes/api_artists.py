from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

bp_artists = Blueprint('bp_artists', __name__)

@bp_artists.route('/api/artists', methods=['GET', 'POST'])
def api_artists() -> Any:
    """
    api_artists function.
    """
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.execute("INSERT INTO artists (name, created_at, updated_at) VALUES (?, datetime('now', 'localtime'), datetime('now', 'localtime'))", ('新規歌手',))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
            
    with get_db() as conn:
        data = request.json
        if data and 'name' in data:
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


@bp_artists.route('/api/artists/<int:artist_id>', methods=['PUT'])
def api_update_artist(artist_id: Any) -> Any:
    """
    api_update_artist function.
    """
    data = request.json
    with get_db() as conn:
        conn.execute("UPDATE artists SET name=?, phonetic_name=?, rating=?, memo=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (data.get('name'), data.get('phonetic_name'), data.get('rating', 0), data.get('memo'), artist_id))
        conn.commit()
        return jsonify({'success': True})


@bp_artists.route('/api/database_view/artists', methods=['GET'])
def api_db_view_artists() -> Any:
    """
    api_db_view_artists function.
    """
    from services.stats_service import get_database_artists
    return jsonify(get_database_artists())


@bp_artists.route('/api/artists/<int:artist_id>', methods=['PATCH'])
def api_update_artist_partial(artist_id: Any) -> Any:
    """
    api_update_artist_partial function.
    """
    data = request.json
    allowed_fields = ['name', 'rating', 'singability', 'memo']
    updates = []
    params = []
    
    extra_updates = {}
    has_extra = False
    
    for k, v in data.items():
        if k in allowed_fields:
            updates.append(f"{k} = ?")
            params.append(v)
        else:
            extra_updates[k] = v
            has_extra = True
            
    if not updates and not has_extra:
        return jsonify({'error': 'No valid fields provided'}), 400
        
    try:
        with get_db() as conn:
            if has_extra:
                import json
                row = conn.execute("SELECT extra_properties FROM artists WHERE id = ?", (artist_id,)).fetchone()
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
                query = f"UPDATE artists SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                params.append(artist_id)
                conn.execute(query, tuple(params))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Custom Schemas & Views (Notion-like) API

@bp_artists.route('/api/artists/<int:artist_id>', methods=['DELETE'])
def api_delete_artist(artist_id: Any) -> Any:
    """
    api_delete_artist function.
    """
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


