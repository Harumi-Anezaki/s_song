import codecs
import re
import os

with codecs.open('core/app.py', 'r', 'utf-8') as f:
    content = f.read()

blocks = []
route_matches = list(re.finditer(r'^@app\.route', content, flags=re.MULTILINE))

for i, match in enumerate(route_matches):
    start = match.start()
    end = route_matches[i+1].start() if i+1 < len(route_matches) else len(content)
    blocks.append(content[start:end])
    
print(f"Found {len(blocks)} route blocks")

mapping = {
    'api_youtube': ['api_youtube_search', 'api_videos_exclude', 'api_videos_update', 'api_videos_merge_to_existing'],
    'api_songs': ['api_songs_register_temp', 'api_songs_merge_temp', 'api_get_songs', 'api_get_song', 'api_update_song', 'api_merge_songs', 'api_patch_song', 'api_delete_song'],
    'api_artists': ['api_artists', 'api_update_artist', 'api_patch_artist', 'api_delete_artist'],
    'api_notion': ['api_get_schemas', 'api_create_schema', 'api_update_schema', 'api_get_views_config', 'api_create_view_config', 'api_get_tags', 'api_create_tag', 'api_patch_tag', 'api_reorder_tags', 'api_merge_tags', 'api_database_view_songs', 'api_database_view_artists', 'api_get_view_settings', 'api_update_view_settings'],
    'api_system': ['index', 'api_get_view', 'api_export_backup', 'api_import_backup', 'api_shutdown', 'api_get_db_raw']
}

blueprint_blocks = {k: [] for k in mapping.keys()}

for block in blocks:
    m = re.search(r'^def\s+([a-zA-Z0-9_]+)\(', block, flags=re.MULTILINE)
    if m:
        fname = m.group(1)
        found = False
        for bp, fnames in mapping.items():
            if fname in fnames:
                bp_block = block.replace('@app.route', f'@{bp}.route')
                blueprint_blocks[bp].append(bp_block)
                found = True
                break
        if not found:
            if 'youtube' in block or 'video' in fname: blueprint_blocks['api_youtube'].append(block.replace('@app.route', f'@api_youtube.route'))
            elif 'song' in fname: blueprint_blocks['api_songs'].append(block.replace('@app.route', f'@api_songs.route'))
            elif 'artist' in fname: blueprint_blocks['api_artists'].append(block.replace('@app.route', f'@api_artists.route'))
            elif 'tag' in fname or 'schema' in fname or 'view' in fname: blueprint_blocks['api_notion'].append(block.replace('@app.route', f'@api_notion.route'))
            else: blueprint_blocks['api_system'].append(block.replace('@app.route', f'@api_system.route'))

header = '''from flask import Blueprint, jsonify, request, render_template
import sqlite3
import json
import uuid
import datetime
import math
from typing import Dict, Any, List

from database import get_db
from services import youtube, song_service, stats_service, backup_service

{bp_name} = Blueprint('{bp_name}', __name__)

'''

os.makedirs('core/routes', exist_ok=True)

for bp, blocks in blueprint_blocks.items():
    with codecs.open(f'core/routes/{bp}.py', 'w', 'utf-8') as f:
        f.write(header.format(bp_name=bp))
        for b in blocks:
            f.write(b)
            f.write('\\n')

app_py_content = '''import os
import sys
import threading
from flask import Flask

# Windows Embedded Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import init_db

# Import blueprints
from routes.api_youtube import api_youtube
from routes.api_songs import api_songs
from routes.api_artists import api_artists
from routes.api_notion import api_notion
from routes.api_system import api_system

app = Flask(__name__)
app.config.from_object(Config)

init_db()

app.register_blueprint(api_youtube)
app.register_blueprint(api_songs)
app.register_blueprint(api_artists)
app.register_blueprint(api_notion)
app.register_blueprint(api_system)

if __name__ == "__main__":
    if app.config.get("OPEN_BROWSER_ON_START", True):
        import webbrowser
        port = app.config.get("PORT", 5000)
        threading.Timer(1.25, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(port=app.config.get("PORT", 5000), debug=True, use_reloader=False)
'''

with codecs.open('core/app.py', 'w', 'utf-8') as f:
    f.write(app_py_content)

print("Refactoring complete.")
