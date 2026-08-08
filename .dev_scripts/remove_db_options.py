with open('core/static/js/app.js', 'rb') as f:
    content = f.read()

target = b"""<option value="songs">songs (譖ｲ)</option>
                  <option value="artists">artists (豁梧焔)</option>
                  <option value="videos">videos (蜍慕判)</option>
                  <option value="song_sub_artists">song_sub_artists (繧ｵ繝匁ｭ梧焔邏蝉ｻ倥￠)</option>"""

replace = b"""<option value="songs">songs (譖ｲ)</option>
                  <option value="artists">artists (豁梧焔)</option>"""

if target in content:
    content = content.replace(target, replace)
    with open('core/static/js/app.js', 'wb') as f:
        f.write(content)
    print('Updated app.js!')
else:
    print('Target not found, trying with carriage returns.')
    target_win = target.replace(b'\n', b'\r\n')
    if target_win in content:
        content = content.replace(target_win, replace.replace(b'\n', b'\r\n'))
        with open('core/static/js/app.js', 'wb') as f:
            f.write(content)
        print('Updated app.js with CR LF!')
    else:
        print('Target not found at all. Here is a snippet of what is there:')
        import re
        m = re.search(b'<select id="db-table-select".*?</select>', content, re.DOTALL)
        if m:
            print(m.group(0).decode('cp932', 'ignore'))
