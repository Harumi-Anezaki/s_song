from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

bp_youtube = Blueprint('bp_youtube', __name__)

@bp_youtube.route('/api/youtube/search', methods=['POST'])
def api_youtube_search() -> Any:
    """
    api_youtube_search function.
    """
    data = request.json
    keyword = data.get('keyword')
    max_results = data.get('max_results') or 200
    min_views = data.get('min_views') or 0
    
    if not keyword:
        return jsonify({'error': 'キーワードが必要です'}), 400
        
    try:
        with get_db() as conn:
            existing = conn.execute("SELECT id FROM artists WHERE name = ?", (keyword,)).fetchone()
            if not existing:
                conn.execute("INSERT INTO artists (name) VALUES (?)", (keyword,))
                conn.commit()
                
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp_youtube.route('/api/videos/exclude', methods=['POST'])
def api_exclude_video() -> Any:
    """
    api_exclude_video function.
    """
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


@bp_youtube.route('/api/videos/update', methods=['POST'])
def api_videos_update() -> Any:
    """
    api_videos_update function.
    """
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


