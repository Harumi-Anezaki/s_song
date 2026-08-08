from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

bp_notion = Blueprint('bp_notion', __name__)

@bp_notion.route('/api/views/<view_name>', methods=['GET'])
def api_views(view_name: Any) -> Any:
    """
    api_views function.
    """
    try:
        results = stats_service.get_view_data(view_name)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/view_settings', methods=['GET'])
def get_view_settings() -> Any:
    """
    get_view_settings function.
    """
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM view_settings").fetchall()
        import json
        settings = {}
        for r in rows:
            try:
                settings[r['view_id']] = json.loads(r['config'])
            except:
                settings[r['view_id']] = {}
        return jsonify(settings)


@bp_notion.route('/api/view_settings', methods=['POST'])
def save_view_settings() -> Any:
    """
    save_view_settings function.
    """
    data = request.json
    view_id = data.get('view_id')
    config = data.get('config')
    import json
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO view_settings (view_id, config) VALUES (?, ?)", (view_id, json.dumps(config)))
        conn.commit()
    return jsonify({'success': True})


@bp_notion.route('/api/schemas', methods=['GET'])
def api_get_schemas() -> Any:
    """
    api_get_schemas function.
    """
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM custom_schemas ORDER BY created_at ASC").fetchall()
            schemas = []
            for r in rows:
                s = dict(r)
                if s.get('options'):
                    import json
                    s['options'] = json.loads(s['options'])
                schemas.append(s)
            return jsonify(schemas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/schemas', methods=['POST'])
def api_create_schema() -> Any:
    """
    api_create_schema function.
    """
    data = request.json
    import uuid
    import json
    new_id = f"schema_{uuid.uuid4().hex[:8]}"
    options_str = json.dumps(data.get('options', [])) if data.get('options') else None
    
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO custom_schemas (id, target_table, key, label, type, options)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_id, data['target_table'], data['key'], data['label'], data['type'], options_str))
            conn.commit()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@bp_notion.route('/api/schemas/update', methods=['POST'])
def api_update_schema() -> Any:
    """
    api_update_schema function.
    """
    data = request.json
    try:
        with get_db() as conn:
            # Check if exists
            row = conn.execute("SELECT * FROM custom_schemas WHERE target_table = ? AND key = ?", (data['target_table'], data['key'])).fetchone()
            if row:
                options_str = json.dumps(data.get('options', [])) if data.get('options') else row['options']
                conn.execute("UPDATE custom_schemas SET label = ?, options = ? WHERE id = ?", (data['label'], options_str, row['id']))
            else:
                # If it's a base schema, we can't update it in DB unless we create it as a custom schema override.
                # Actually, we can just insert it as a custom schema override!
                import uuid
                new_id = f"schema_{uuid.uuid4().hex[:8]}"
                options_str = json.dumps(data.get('options', [])) if data.get('options') else None
                conn.execute("""
                    INSERT INTO custom_schemas (id, target_table, key, label, type, options)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (new_id, data['target_table'], data['key'], data['label'], data.get('type', 'text'), options_str))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/views_config', methods=['GET'])
def api_get_views() -> Any:
    """
    api_get_views function.
    """
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM views ORDER BY created_at ASC").fetchall()
            views = []
            for r in rows:
                v = dict(r)
                import json
                v['config'] = json.loads(v['config'])
                views.append(v)
            return jsonify(views)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/views_config', methods=['POST'])
def api_save_view() -> Any:
    """
    api_save_view function.
    """
    data = request.json
    view_id = data.get('id')
    import json
    import uuid
    
    if not view_id:
        view_id = f"view_{uuid.uuid4().hex[:8]}"
        
    config_str = json.dumps(data.get('config', {}))
    try:
        with get_db() as conn:
            # Upsert
            existing = conn.execute("SELECT id FROM views WHERE id = ?", (view_id,)).fetchone()
            if existing:
                conn.execute("""
                    UPDATE views 
                    SET target_table=?, name=?, type=?, config=?, updated_at=CURRENT_TIMESTAMP 
                    WHERE id=?
                """, (data['target_table'], data['name'], data['type'], config_str, view_id))
            else:
                conn.execute("""
                    INSERT INTO views (id, target_table, name, type, config)
                    VALUES (?, ?, ?, ?, ?)
                """, (view_id, data['target_table'], data['name'], data['type'], config_str))
            conn.commit()
        return jsonify({'success': True, 'id': view_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Tags API



@bp_notion.route('/api/views_config/<view_id>', methods=['DELETE'])
def api_delete_view(view_id: Any) -> Any:
    """
    api_delete_view function.
    """
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM views WHERE id = ?", (view_id,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/tags', methods=['GET'])
def api_get_tags() -> Any:
    """
    api_get_tags function.
    """
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM tag_definitions WHERE is_active = 1 ORDER BY display_order ASC").fetchall()
            tags = [dict(r) for r in rows]
            # format camelCase for frontend
            for t in tags:
                t['colorKey'] = t.pop('color_key')
                t['backgroundColor'] = t.pop('background_color')
                t['textColor'] = t.pop('text_color')
                t['displayOrder'] = t.pop('display_order')
                t['isActive'] = bool(t.pop('is_active'))
            return jsonify(tags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/tags', methods=['POST'])
def api_create_tag() -> Any:
    """
    api_create_tag function.
    """
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    color_key = data.get('colorKey', 'gray')
    bg_color = data.get('backgroundColor', '#e3e2e0')
    txt_color = data.get('textColor', '#5a5a5a')
    display_order = data.get('displayOrder', 99)
    
    import uuid
    import datetime
    new_id = f"tag_{uuid.uuid4().hex[:8]}"
    now = datetime.datetime.now().isoformat()
    
    try:
        with get_db() as conn:
            # check duplicate
            if conn.execute("SELECT id FROM tag_definitions WHERE name = ?", (name,)).fetchone():
                return jsonify({'error': 'Tag name already exists'}), 400
                
            conn.execute("""
                INSERT INTO tag_definitions (id, name, color_key, background_color, text_color, display_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (new_id, name, color_key, bg_color, txt_color, display_order, now, now))
            conn.commit()
            return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/tags/<tag_id>', methods=['PATCH'])
def api_update_tag(tag_id: Any) -> Any:
    """
    api_update_tag function.
    """
    data = request.json
    updates = []
    params = []
    
    mapping = {
        'name': 'name',
        'colorKey': 'color_key',
        'backgroundColor': 'background_color',
        'textColor': 'text_color',
        'displayOrder': 'display_order',
        'isActive': 'is_active'
    }
    
    for k, v in data.items():
        if k in mapping:
            updates.append(f"{mapping[k]} = ?")
            params.append(1 if v is True else 0 if v is False else v)
            
    if not updates:
        return jsonify({'error': 'No fields provided'}), 400
        
    import datetime
    updates.append("updated_at = ?")
    params.append(datetime.datetime.now().isoformat())
    params.append(tag_id)
    
    try:
        with get_db() as conn:
            conn.execute(f"UPDATE tag_definitions SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/tags/reorder', methods=['POST'])
def api_reorder_tags() -> Any:
    """
    api_reorder_tags function.
    """
    data = request.json
    tag_ids = data.get('tag_ids', [])
    if not tag_ids:
        return jsonify({'success': True})
        
    import datetime
    now = datetime.datetime.now().isoformat()
    
    try:
        with get_db() as conn:
            for i, tid in enumerate(tag_ids):
                conn.execute("UPDATE tag_definitions SET display_order = ?, updated_at = ? WHERE id = ?", (i + 1, now, tid))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp_notion.route('/api/tags/<source_id>/merge/<target_id>', methods=['POST'])
def api_merge_tags(source_id: Any, target_id: Any) -> Any:
    """
    api_merge_tags function.
    """
    import datetime
    now = datetime.datetime.now().isoformat()
    try:
        with get_db() as conn:
            # check if both tags exist
            src = conn.execute("SELECT id FROM tag_definitions WHERE id = ?", (source_id,)).fetchone()
            tgt = conn.execute("SELECT id FROM tag_definitions WHERE id = ?", (target_id,)).fetchone()
            if not src or not tgt:
                return jsonify({'error': 'Source or target tag not found'}), 404
                
            # fetch all songs with source_id
            songs = conn.execute("SELECT song_id FROM song_tags WHERE tag_id = ?", (source_id,)).fetchall()
            
            # insert into target_id (ignore if already exists)
            for row in songs:
                song_id = row['song_id']
                try:
                    conn.execute("INSERT INTO song_tags (song_id, tag_id, created_at) VALUES (?, ?, ?)", (song_id, target_id, now))
                except Exception:
                    pass # already has target_id
                    
            # delete source_id from song_tags
            conn.execute("DELETE FROM song_tags WHERE tag_id = ?", (source_id,))
            
            # disable source_id tag
            conn.execute("UPDATE tag_definitions SET is_active = 0, updated_at = ? WHERE id = ?", (now, source_id))
            
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=app.config['PORT'], debug=(os.getenv('FLASK_ENV', 'development') == 'development'))



@bp_notion.route('/api/schemas/update_property', methods=['POST'])
def api_update_property() -> Any:
    """
    api_update_property function.
    """
    data = request.json
    target_table = data.get('target_table')
    key = data.get('key')
    label = data.get('label')
    options = data.get('options')
    
    if not target_table or not key:
        return jsonify({'error': 'Missing parameters'}), 400
        
    try:
        with get_db() as conn:
            # Check if it's a custom schema
            row = conn.execute("SELECT id FROM custom_schemas WHERE target_table = ? AND key = ?", (target_table, key)).fetchone()
            if row:
                conn.execute(
                    "UPDATE custom_schemas SET label = ?, options = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (label, options, row['id'])
                )
            else:
                # Store in settings table for hardcoded properties
                settings_key = f"prop_settings_{target_table}_{key}"
                conn.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
                    (settings_key, options, options)
                )
                
                # Also save the label if provided
                if label:
                    label_key = f"prop_label_{target_table}_{key}"
                    conn.execute(
                        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
                        (label_key, label, label)
                    )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_notion.route('/api/schemas/property_settings', methods=['GET'])
def api_get_property_settings() -> Any:
    """
    api_get_property_settings function.
    """
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT key, value FROM settings WHERE key LIKE 'prop_settings_%' OR key LIKE 'prop_label_%'").fetchall()
            result = {}
            for r in rows:
                result[r['key']] = r['value']
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_notion.route('/api/schemas/option_labels', methods=['GET'])
def api_get_option_labels() -> Any:
    """
    api_get_option_labels function.
    """
    try:
        with get_db() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = 'option_labels'").fetchone()
            if row:
                import json
                return jsonify(json.loads(row['value']))
            return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_notion.route('/api/schemas/option_labels', methods=['POST'])
def api_save_option_labels() -> Any:
    """
    api_save_option_labels function.
    """
    data = request.json
    try:
        import json
        labels_json = json.dumps(data)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES ('option_labels', ?) ON CONFLICT(key) DO UPDATE SET value = ?",
                (labels_json, labels_json)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
