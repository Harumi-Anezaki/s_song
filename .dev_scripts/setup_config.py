import os
import json
import codecs

# Read existing .env if present
env_dict = {}
if os.path.exists('.env'):
    with codecs.open('.env', 'r', 'utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                env_dict[k] = v

config_data = {
    "YOUTUBE_API_KEY": env_dict.get('YOUTUBE_API_KEY', ""),
    "PORT": int(env_dict.get('PORT', 5000)),
    "OPEN_BROWSER_ON_START": True
}

with codecs.open('config.json', 'w', 'utf-8') as f:
    json.dump(config_data, f, indent=4)

config_py_content = """import os
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
"""

with codecs.open('core/config.py', 'w', 'utf-8') as f:
    f.write(config_py_content)

print("config.json created and config.py updated.")
