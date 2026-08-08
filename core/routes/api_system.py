from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

bp_system = Blueprint('bp_system', __name__)

@bp_system.route('/')
def index() -> Any:
    """
    index function.
    """
    return render_template('index.html')


@bp_system.route('/api/songs/register_temp', methods=['POST'])
def api_register_temp() -> Any:
    """
    api_register_temp function.
    """
    data = request.json
    videos = data.get('videos', [])
    main_artist_id = data.get('main_artist_id')
    sub_artist_ids = data.get('sub_artist_ids', [])
    
    if not videos:
        return jsonify({'error': 'No videos provided'}), 400
        
    try:
        with get_db() as conn:
            for v in videos:
                existing = conn.execute("SELECT id FROM videos WHERE id = ?", (v['id'],)).fetchone()
                if existing:
                    continue
                    
                cursor = conn.execute("INSERT INTO songs (title, main_artist_id, tag_b) VALUES (?, ?, ?)", (v['title'], main_artist_id, '[]'))
                song_id = cursor.lastrowid
                
                for sub_id in sub_artist_ids:
                    conn.execute("INSERT OR IGNORE INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (song_id, sub_id))
                
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


@bp_system.route('/api/songs/merge_temp', methods=['POST'])
def api_merge_temp() -> Any:
    """
    api_merge_temp function.
    """
    data = request.json
    videos = data.get('videos', [])
    title = data.get('title', '')
    main_artist_id = data.get('main_artist_id')
    sub_artist_ids = data.get('sub_artist_ids', [])
    
    if not videos or not title:
        return jsonify({'error': 'Videos and title are required'}), 400
        
    try:
        with get_db() as conn:
            cursor = conn.execute("INSERT INTO songs (title, main_artist_id, tag_b) VALUES (?, ?, ?)", (title, main_artist_id, '[]'))
            song_id = cursor.lastrowid
            
            for sub_id in sub_artist_ids:
                conn.execute("INSERT OR IGNORE INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (song_id, sub_id))
            
            for v in videos:
                existing = conn.execute("SELECT id FROM videos WHERE id = ?", (v['id'],)).fetchone()
                if existing:
                    continue
                
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


@bp_system.route('/api/backup/export', methods=['GET'])
def api_backup_export() -> Any:
    """
    api_backup_export function.
    """
    try:
        json_data = backup_service.export_to_json()
        return jsonify({'success': True, 'data': json_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_system.route('/api/backup/import', methods=['POST'])
def api_backup_import() -> Any:
    """
    api_backup_import function.
    """
    data = request.json
    json_str = data.get('json_str')
    if not json_str:
        return jsonify({'error': 'No data provided'}), 400
        
    try:
        backup_service.import_from_json(json_str)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_system.route('/api/shutdown', methods=['POST'])
def api_shutdown() -> Any:
    """
    api_shutdown function.
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({'error': 'Not running with the Werkzeug Server'}), 500
    func()
    return jsonify({'success': True})


@bp_system.route('/api/db/raw/<table>', methods=['GET'])
def api_db_raw(table: Any) -> Any:
    """
    api_db_raw function.
    """
    allowed_tables = ['songs', 'artists', 'videos', 'song_sub_artists', 'excluded_videos', 'settings', 'search_history', 'merge_history']
    if table not in allowed_tables:
        return jsonify({'error': 'Invalid table'}), 400
    try:
        with get_db() as conn:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_system.route('/api/videos/merge_to_existing', methods=['POST'])
def api_merge_to_existing() -> Any:
    """
    api_merge_to_existing function.
    """
    data = request.json
    videos = data.get('videos', [])
    target_song_id = data.get('target_song_id')
    if not videos or not target_song_id:
        return jsonify({'error': 'Videos and target_song_id required'}), 400
        
    try:
        with get_db() as conn:
            for v in videos:
                existing = conn.execute("SELECT id FROM videos WHERE id = ?", (v['id'],)).fetchone()
                if existing:
                    # Update to map to target_song_id and set status 'active'
                    conn.execute("UPDATE videos SET song_id = ?, status = 'active' WHERE id = ?", (target_song_id, v['id']))
                else:
                    conn.execute("""
                        INSERT INTO videos (id, song_id, title, channel_name, url, thumbnail_url, view_count, published_at, formatted_duration, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                    """, (
                        v['id'], target_song_id, v['title'], v['channel_name'], 
                        v['url'], v['thumbnail_url'], v['view_count'], 
                        v['published_at'], v['formatted_duration']
                    ))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

