import os
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

config_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

_config_cache = {}
if os.path.exists(config_json_path):
    with open(config_json_path, 'r', encoding='utf-8') as f:
        try:
            _config_cache = json.load(f)
        except:
            pass

class Config:
    YOUTUBE_API_KEY = _config_cache.get('YOUTUBE_API_KEY') or os.getenv('YOUTUBE_API_KEY')
    PORT = _config_cache.get('PORT') or int(os.getenv('PORT', 5000))
    OPEN_BROWSER_ON_START = _config_cache.get('OPEN_BROWSER_ON_START', True)
