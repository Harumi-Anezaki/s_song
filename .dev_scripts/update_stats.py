import codecs
import re

with codecs.open('core/services/stats_service.py', 'r', 'utf-8') as f:
    stats_py = f.read()

target_str = """            a['view_threshold'] = th.get('view_threshold')
            a['vpd_threshold'] = th.get('vpd_threshold')"""

new_str = """            a['view_threshold'] = th.get('view_threshold')
            a['vpd_threshold'] = th.get('vpd_threshold')
            a['total_views_calc'] = sum(views_list)
            a['vpd_calc'] = sum(vpd_list)"""

if 'total_views_calc' not in stats_py:
    stats_py = stats_py.replace(target_str, new_str)
    with codecs.open('core/services/stats_service.py', 'w', 'utf-8') as f:
        f.write(stats_py)

print("Updated stats_service.py")
