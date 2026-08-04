import os
import requests
import datetime
import isodate
from typing import List, Dict, Any, Optional

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

def get_api_key() -> Optional[str]:
    """環境変数からYouTube APIキーを取得します。"""
    return os.getenv('YOUTUBE_API_KEY')

def search_videos(keyword: str, max_results: int = 200, min_views: int = 0) -> List[Dict[str, Any]]:
    """
    YouTube APIを使用して動画を検索し、条件に一致するものを取得します。
    
    Args:
        keyword (str): 検索キーワード。
        max_results (int): 取得する最大件数（デフォルト: 200）。
        min_views (int): フィルタリングする最低再生回数（デフォルト: 0）。
        
    Returns:
        List[Dict[str, Any]]: 検索結果の動画詳細辞書のリスト。
        
    Raises:
        ValueError: APIキーが設定されていない場合。
        RuntimeError: API通信でエラーが発生した場合。
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("APIキーが設定されていません。")

    videos = []
    next_page_token = None
    fetched_count = 0

    while fetched_count < max_results:
        fetch_size = min(50, max_results - fetched_count)
        
        params = {
            'part': 'snippet',
            'type': 'video',
            'order': 'viewCount',
            'maxResults': fetch_size,
            'q': keyword,
            'key': api_key
        }
        if next_page_token:
            params['pageToken'] = next_page_token

        try:
            res = requests.get(f"{YOUTUBE_API_URL}/search", params=params)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"YouTube API通信エラー: {e}")

        items = data.get('items', [])
        if not items:
            break

        video_ids = [item['id']['videoId'] for item in items]
        fetched_count += len(video_ids)

        if video_ids:
            # 詳細を取得
            details = get_video_details(video_ids)
            for v in details:
                if v['view_count'] >= min_views:
                    videos.append(v)
        
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    videos.sort(key=lambda x: x['view_count'], reverse=True)
    return videos

def get_video_details(video_ids: List[str]) -> List[Dict[str, Any]]:
    """
    動画IDのリストから詳細な動画情報（再生数や動画時間など）を取得します。
    
    Args:
        video_ids (List[str]): YouTubeの動画IDリスト。
        
    Returns:
        List[Dict[str, Any]]: 取得された動画詳細辞書のリスト。
        
    Raises:
        RuntimeError: API通信で詳細取得に失敗した場合。
    """
    api_key = get_api_key()
    if not api_key or not video_ids:
        return []

    results = []
    # 50件ずつに分割
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': ','.join(chunk),
            'key': api_key
        }
        try:
            res = requests.get(f"{YOUTUBE_API_URL}/videos", params=params)
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"YouTube API通信エラー(詳細取得): {e}")

        for item in data.get('items', []):
            try:
                # ISO 8601 duration
                duration_iso = item['contentDetails']['duration']
                duration_td = isodate.parse_duration(duration_iso)
                duration_sec = int(duration_td.total_seconds())
                
                minutes = duration_sec // 60
                seconds = duration_sec % 60
                formatted_duration = f"{minutes}:{seconds:02d}"

                results.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={item['id']}",
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet'].get('channelId', ''),
                    'channel_name': item['snippet']['channelTitle'],
                    'duration_sec': duration_sec,
                    'formatted_duration': formatted_duration,
                    'thumbnail_url': item['snippet']['thumbnails'].get('high', item['snippet']['thumbnails'].get('default', {})).get('url', ''),
                    'last_api_update': datetime.datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error parsing video {item.get('id')}: {e}")
                pass # 欠損している動画はスキップ

    return results
