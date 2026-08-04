import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    PORT = int(os.getenv('PORT', 5000))
