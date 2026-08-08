import codecs
import re

with codecs.open('core/services/stats_service.py', 'r', 'utf-8') as f:
    content = f.read()

# Update calculate_top70_thresholds
thresholds_old = """        thresholds[aid] = {
            'view_threshold': view_threshold,
            'vpd_threshold': vpd_threshold,
            'song_count': count
        }"""
thresholds_new = """        thresholds[aid] = {
            'view_threshold': view_threshold,
            'vpd_threshold': vpd_threshold,
            'song_count': count,
            'total_views_sum': sum(s['total_views'] for s in st_list),
            'vpd_sum': sum(s['views_per_day'] for s in st_list)
        }"""
content = content.replace(thresholds_old, thresholds_new)

# Add fallback for < 5 songs
fallback_old = """    for aid, st_list in artist_songs.items():
        count = len(st_list)
        if count <= 5:
            continue # 5Ȉȉ̏ꍇ͌vZȂ"""

fallback_new = """    for aid, st_list in artist_songs.items():
        count = len(st_list)
        if count <= 5:
            # We still need the sum even if count <= 5
            thresholds[aid] = {
                'view_threshold': None,
                'vpd_threshold': None,
                'song_count': count,
                'total_views_sum': sum(s['total_views'] for s in st_list),
                'vpd_sum': sum(s['views_per_day'] for s in st_list)
            }
            continue"""
content = content.replace(fallback_old, fallback_new)

# Update get_database_songs SQL
sql_old = """SELECT s.*, a.name as artist_name, a.rating as artist_rating 
            FROM songs s
            LEFT JOIN artists a ON s.main_artist_id = a.id"""
sql_new = """SELECT s.*, a.name as artist_name, a.rating as artist_rating, a.singability as artist_singability
            FROM songs s
            LEFT JOIN artists a ON s.main_artist_id = a.id"""
content = content.replace(sql_old, sql_new)


# Update get_database_songs properties
props_old = """                song_dict['view_threshold'] = th['view_threshold']
                song_dict['vpd_threshold'] = th['vpd_threshold']
                song_dict['artist_song_count'] = th['song_count']
                
                if song_dict['total_views'] < th['view_threshold'] and song_dict['views_per_day'] < th['vpd_threshold']:
                    is_outdated = True
            else:
                song_dict['view_threshold'] = None
                song_dict['vpd_threshold'] = None
                song_dict['artist_song_count'] = 0
                
            song_dict['is_outdated'] = is_outdated"""

props_new = """                song_dict['view_threshold'] = th.get('view_threshold')
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
            song_dict['artist_singability'] = song_dict.get('artist_singability')"""

content = content.replace(props_old, props_new)

with codecs.open('core/services/stats_service.py', 'w', 'utf-8') as f:
    f.write(content)

print("Updated stats_service.py for songs schema")
