import datetime
import math
import json
import sqlite3
from typing import Dict, Any, List, Optional
from database import get_db

def calculate_song_stats(conn: sqlite3.Connection) -> Dict[int, Dict[str, Any]]:
    """
    全曲の集計データを計算し、辞書で返します。
    
    Args:
        conn (sqlite3.Connection): データベース接続オブジェクト。
        
    Returns:
        Dict[int, Dict[str, Any]]: song_idをキーとした集計情報の辞書。
        { song_id: { 'total_views': int, 'views_per_day': float, 'effective_base_date': str, 'auto_base_date': str, 'main_artist_id': int } }
    """
    songs = conn.execute("SELECT * FROM songs WHERE is_archived = 0").fetchall()
    videos = conn.execute("SELECT song_id, view_count, published_at FROM videos WHERE status = 'active' AND song_id IS NOT NULL").fetchall()
    
    # song_idごとの動画リスト
    video_map = {}
    for v in videos:
        sid = v['song_id']
        if sid not in video_map:
            video_map[sid] = []
        video_map[sid].append(dict(v))

    stats = {}
    now = datetime.datetime.now()
    today_date = now.date()

    for s in songs:
        sid = s['id']
        v_list = video_map.get(sid, [])
        
        if not v_list:
            stats[sid] = {
                'total_views': 0,
                'views_per_day': 0.0,
                'effective_base_date': None,
                'auto_base_date': None,
                'main_artist_id': s['main_artist_id']
            }
            continue

        total_views = sum(v['view_count'] for v in v_list)
        
        # 自動基準日 = 最古の投稿日
        auto_base_date_str = min(v['published_at'] for v in v_list)
        # ISO8601対応などで先頭10文字(YYYY-MM-DD)を取得
        auto_base_date_str = auto_base_date_str[:10]
        
        effective_base_date_str = auto_base_date_str
        if s['use_manual_date'] and s['manual_base_date']:
            effective_base_date_str = s['manual_base_date']

        try:
            base_date = datetime.datetime.strptime(effective_base_date_str, '%Y-%m-%d').date()
            elapsed_days = (today_date - base_date).days
            if elapsed_days <= 0:
                elapsed_days = 1 # 0除算防止、未来日付対応
            views_per_day = total_views / elapsed_days
        except Exception:
            views_per_day = 0.0
            
        stats[sid] = {
            'total_views': total_views,
            'views_per_day': views_per_day,
            'effective_base_date': effective_base_date_str,
            'auto_base_date': auto_base_date_str,
            'main_artist_id': s['main_artist_id']
        }
        
    return stats

def calculate_top70_thresholds(stats: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    メイン歌手ごとの上位70%境界値を計算します。
    
    Args:
        stats (Dict[int, Dict[str, Any]]): `calculate_song_stats` で計算された全曲の集計データ。
        
    Returns:
        Dict[int, Dict[str, Any]]: artist_idをキーとした境界値情報の辞書。
        { artist_id: { 'view_threshold': int, 'vpd_threshold': float, 'song_count': int } }
    """
    artist_songs = {}
    for sid, st in stats.items():
        aid = st['main_artist_id']
        if aid is None:
            continue
        # 有効動画がない（再生数0、日付なし）場合は母集団に入れない
        if st['effective_base_date'] is None:
            continue
            
        if aid not in artist_songs:
            artist_songs[aid] = []
        artist_songs[aid].append(st)

    thresholds = {}
    for aid, st_list in artist_songs.items():
        count = len(st_list)
        if count <= 5:
            continue # 5曲以下の場合は計算しない
            
        target_index = math.floor(count * 0.7) - 1
        if target_index < 0:
            target_index = 0
            
        # 再生数降順
        st_list_views = sorted(st_list, key=lambda x: x['total_views'], reverse=True)
        view_threshold = st_list_views[target_index]['total_views']
        
        # 回/日降順
        st_list_vpd = sorted(st_list, key=lambda x: x['views_per_day'], reverse=True)
        vpd_threshold = st_list_vpd[target_index]['views_per_day']
        
        thresholds[aid] = {
            'view_threshold': view_threshold,
            'vpd_threshold': vpd_threshold,
            'song_count': count,
            'total_views_sum': sum(s['total_views'] for s in st_list),
            'vpd_sum': sum(s['views_per_day'] for s in st_list)
        }
        
    return thresholds

def get_view_data(view_name: str) -> List[Dict[str, Any]]:
    """
    指定されたビュー名に応じた楽曲リストを取得・フィルタ・ソートします。
    
    Args:
        view_name (str): 対象のビュー名（例: 'おはこ', 'カラオケ' など）。
        
    Returns:
        List[Dict[str, Any]]: 表示用にフォーマットされた楽曲辞書のリスト。
    """
    with get_db() as conn:
        stats = calculate_song_stats(conn)
        thresholds = calculate_top70_thresholds(stats)
        
        # 全曲と関連情報を取得
        songs_query = """
            SELECT s.*, a.name as artist_name, a.rating as artist_rating, a.singability as artist_singability
            FROM songs s
            LEFT JOIN artists a ON s.main_artist_id = a.id
            WHERE s.is_archived = 0
        """
        songs_rows = conn.execute(songs_query).fetchall()
        
        results = []
        for row in songs_rows:
            song_dict = dict(row)
            sid = song_dict['id']
            st = stats.get(sid, {})
            aid = song_dict['main_artist_id']
            
            song_dict['total_views'] = st.get('total_views', 0)
            song_dict['views_per_day'] = st.get('views_per_day', 0.0)
            song_dict['effective_base_date'] = st.get('effective_base_date')
            
            is_outdated = False
            if aid in thresholds:
                th = thresholds[aid]
                song_dict['view_threshold'] = th['view_threshold']
                song_dict['vpd_threshold'] = th['vpd_threshold']
                song_dict['artist_song_count'] = th['song_count']
                
                # 時代遅れ判定: 両方が境界値未満の場合のみ
                if song_dict['total_views'] < th['view_threshold'] and song_dict['views_per_day'] < th['vpd_threshold']:
                    is_outdated = True
            else:
                song_dict['view_threshold'] = None
                song_dict['vpd_threshold'] = None
                song_dict['artist_song_count'] = 0
                
            song_dict['is_outdated'] = is_outdated
            
            # タグのパース
            try:
                song_dict['tag_b_list'] = json.loads(song_dict['tag_b']) if song_dict['tag_b'] else []
            except:
                song_dict['tag_b_list'] = []

            results.append(song_dict)
            
        # ビューに応じたフィルタリングとソート（バックエンドで行うかフロントで行うか。今回はバックエンドで行う）
        return apply_view_filter_and_sort(results, view_name)

def apply_view_filter_and_sort(songs: List[Dict[str, Any]], view_name: str) -> List[Dict[str, Any]]:
    """
    取得した全曲リストに対し、ビューごとのフィルタリングとソートを適用します。
    
    Args:
        songs (List[Dict[str, Any]]): データベースから取得した楽曲辞書のリスト。
        view_name (str): 対象のビュー名。
        
    Returns:
        List[Dict[str, Any]]: フィルタ・ソート済みの楽曲リスト。
    """
    filtered = songs
    
    # Helper functions for sorting
    def sort_key_default(x: Any) -> Any:
        """
    sort_key_default function.
    """
        # 好き度降順、歌手名昇順、回/日降順
        rating = x.get('artist_rating') or 0
        name = x.get('artist_name') or ''
        vpd = x.get('views_per_day') or 0.0
        return (-rating, name, -vpd)
        
    if view_name == 'おはこ':
        filtered = [s for s in filtered if 'tag_ohako' in s['tag_b_list'] and not s['is_outdated']]
        filtered.sort(key=sort_key_default)
    elif view_name == '高音練習':
        filtered = [s for s in filtered if 'tag_high_pitch' in s['tag_b_list'] and not s['is_outdated']]
        filtered.sort(key=sort_key_default)
    elif view_name == '盛上':
        filtered = [s for s in filtered if 'tag_party' in s['tag_b_list']]
        filtered.sort(key=lambda x: x.get('total_views', 0), reverse=True)
    elif view_name == 'カラオケ':
        filtered = [s for s in filtered if s['tag_a'] == '日本' 
                    and 'tag_party' not in s['tag_b_list'] 
                    and 'tag_okinawa' not in s['tag_b_list'] 
                    and 'tag_hiphop' not in s['tag_b_list']
                    and not s['is_outdated']
                    and s['main_artist_id'] is not None]
        filtered.sort(key=sort_key_default)
    elif view_name == '聞流日本':
        filtered = [s for s in filtered if s['tag_a'] == '日本' 
                    and 'tag_party' not in s['tag_b_list'] 
                    and 'tag_okinawa' not in s['tag_b_list'] 
                    and 'tag_hiphop' not in s['tag_b_list']
                    and 'tag_excluded' not in s['tag_b_list']
                    and not s['is_outdated']
                    and s['main_artist_id'] is not None]
        filtered.sort(key=sort_key_default)
    elif view_name == '聞流海外':
        filtered = [s for s in filtered if s['tag_a'] == '海外' 
                    and 'tag_party' not in s['tag_b_list'] 
                    and 'tag_okinawa' not in s['tag_b_list'] 
                    and 'tag_hiphop' not in s['tag_b_list']
                    and 'tag_excluded' not in s['tag_b_list']
                    and not s['is_outdated']
                    and s['main_artist_id'] is not None]
        filtered.sort(key=sort_key_default)
    elif view_name == 'HIPHOP':
        filtered = [s for s in filtered if 'tag_hiphop' in s['tag_b_list'] and not s['is_outdated']]
        filtered.sort(key=sort_key_default)
    elif view_name == '沖縄':
        filtered = [s for s in filtered if 'tag_okinawa' in s['tag_b_list']]
        filtered.sort(key=sort_key_default)
    elif view_name == '排除':
        filtered = [s for s in filtered if 'tag_excluded' in s['tag_b_list']]
        filtered.sort(key=sort_key_default)
    elif view_name == '時代遅れ':
        filtered = [s for s in filtered if s['is_outdated']]
        filtered.sort(key=sort_key_default)
    elif view_name == '未DL':
        filtered = [s for s in filtered if s['dl_status'] == '未DL']
        filtered.sort(key=sort_key_default)
    elif view_name == 'すべて':
        pass # All non-archived songs
        
    return filtered

def get_database_artists() -> List[Dict[str, Any]]:
    """
    Notion風UI用: 歌手_原本ビューに必要なすべての情報（ロールアップ含む）を取得します。
    """
    with get_db() as conn:
        stats = calculate_song_stats(conn)
        thresholds = calculate_top70_thresholds(stats)
        
        artists_rows = conn.execute("SELECT * FROM artists").fetchall()
        
        songs_rows = conn.execute("SELECT id, title, main_artist_id FROM songs WHERE is_archived = 0").fetchall()
        main_songs_map = {}
        for s in songs_rows:
            aid = s['main_artist_id']
            if aid not in main_songs_map:
                main_songs_map[aid] = []
            main_songs_map[aid].append(dict(s))
            
        sub_songs_rows = conn.execute("""
            SELECT ssa.artist_id, s.id, s.title 
            FROM song_sub_artists ssa
            JOIN songs s ON ssa.song_id = s.id
            WHERE s.is_archived = 0
        """).fetchall()
        sub_songs_map = {}
        for r in sub_songs_rows:
            aid = r['artist_id']
            if aid not in sub_songs_map:
                sub_songs_map[aid] = []
            sub_songs_map[aid].append({'id': r['id'], 'title': r['title']})
            
        results = []
        for row in artists_rows:
            a = dict(row)
            aid = a['id']
            
            m_songs = main_songs_map.get(aid, [])
            m_songs_ids = [{'id': s['id'], 'title': s['title']} for s in m_songs]
            
            s_songs = sub_songs_map.get(aid, [])
            
            views_list = []
            vpd_list = []
            for s in m_songs:
                st = stats.get(s['id'], {})
                if st.get('effective_base_date'):
                    views_list.append(st.get('total_views', 0))
                    vpd_list.append(st.get('views_per_day', 0.0))
                    
            th = thresholds.get(aid, {})
            
            a['main_songs'] = m_songs_ids
            a['sub_songs'] = s_songs
            a['views_list'] = views_list
            a['vpd_list'] = vpd_list
            a['view_threshold'] = th.get('view_threshold')
            a['vpd_threshold'] = th.get('vpd_threshold')
            a['total_views_calc'] = sum(views_list)
            a['vpd_calc'] = sum(vpd_list)
            
            try:
                extra_props = json.loads(a.get('extra_properties', '{}'))
                for k, v in extra_props.items():
                    a[k] = v
            except:
                pass
            
            results.append(a)
            
        return results

def get_database_songs() -> List[Dict[str, Any]]:
    """
    Notion風UI用: 曲_原本ビューに必要なすべての情報を取得します。
    """
    with get_db() as conn:
        stats = calculate_song_stats(conn)
        thresholds = calculate_top70_thresholds(stats)
        
        songs_query = """
            SELECT s.*, a.name as artist_name, a.rating as artist_rating, a.singability as artist_singability
            FROM songs s
            LEFT JOIN artists a ON s.main_artist_id = a.id
            WHERE s.is_archived = 0
        """
        songs_rows = conn.execute(songs_query).fetchall()
        
        sub_artists_query = """
            SELECT ssa.song_id, a.id, a.name 
            FROM song_sub_artists ssa
            JOIN artists a ON ssa.artist_id = a.id
        """
        sub_artists_rows = conn.execute(sub_artists_query).fetchall()
        sub_artists_map = {}
        for r in sub_artists_rows:
            sid = r['song_id']
            if sid not in sub_artists_map:
                sub_artists_map[sid] = []
            sub_artists_map[sid].append({'id': r['id'], 'name': r['name']})
            
        song_tags_query = """
            SELECT st.song_id, t.id
            FROM song_tags st
            JOIN tag_definitions t ON st.tag_id = t.id
            WHERE t.is_active = 1
            ORDER BY t.display_order ASC
        """
        try:
            song_tags_rows = conn.execute(song_tags_query).fetchall()
        except sqlite3.OperationalError:
            song_tags_rows = []
            
        song_tags_map = {}
        for r in song_tags_rows:
            sid = r['song_id']
            if sid not in song_tags_map:
                song_tags_map[sid] = []
            song_tags_map[sid].append(r['id'])
            
        videos_query = """
            SELECT song_id, url, view_count, status
            FROM videos
            WHERE status != 'excluded'
        """
        videos_rows = conn.execute(videos_query).fetchall()
        videos_map = {}
        for v in videos_rows:
            sid = v['song_id']
            if sid not in videos_map:
                videos_map[sid] = []
            videos_map[sid].append(dict(v))
            
        results = []
        for row in songs_rows:
            song_dict = dict(row)
            sid = song_dict['id']
            st = stats.get(sid, {})
            aid = song_dict['main_artist_id']
            
            song_dict['total_views'] = st.get('total_views', 0)
            song_dict['views_per_day'] = st.get('views_per_day', 0.0)
            song_dict['effective_base_date'] = st.get('effective_base_date')
            
            is_outdated = False
            if aid in thresholds:
                th = thresholds[aid]
                song_dict['view_threshold'] = th.get('view_threshold')
                song_dict['vpd_threshold'] = th.get('vpd_threshold')
                song_dict['artist_song_count'] = th.get('song_count', 0)
                song_dict['artist_total_views'] = th.get('total_views_sum', 0)
                song_dict['artist_vpd'] = th.get('vpd_sum', 0.0)
                
                if th.get('view_threshold') is not None and song_dict['total_views'] < th['view_threshold'] and song_dict['views_per_day'] < th['vpd_threshold']:
                    is_outdated = True
            else:
                song_dict['view_threshold'] = None
                song_dict['vpd_threshold'] = None
                song_dict['artist_song_count'] = 0
                song_dict['artist_total_views'] = 0
                song_dict['artist_vpd'] = 0.0
                
            song_dict['is_outdated'] = is_outdated
            # Add artist stats natively so UI schema can reference them
            song_dict['artist_singability'] = song_dict.get('artist_singability')
            song_dict['tag_b_list'] = song_tags_map.get(sid, [])
                
            song_dict['sub_artists'] = sub_artists_map.get(sid, [])
            
            v_list = videos_map.get(sid, [])
            song_dict['video_count'] = len(v_list)
            
            primary_url = None
            if v_list:
                v_list_sorted = sorted(v_list, key=lambda v: v.get('view_count', 0), reverse=True)
                primary_url = "\n".join([v['url'] for v in v_list_sorted if v.get('url')])
                
            song_dict['primary_url'] = primary_url
            
            try:
                extra_props = json.loads(song_dict.get('extra_properties', '{}'))
                for k, v in extra_props.items():
                    song_dict[k] = v
            except:
                pass
            
            results.append(song_dict)
            
        return results
