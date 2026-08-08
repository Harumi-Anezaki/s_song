with open('core/static/js/app.js', 'rb') as f:
    content = f.read()

target = b'<select id="db-table-select" class="form-group" style="padding:8px;">'
replace = b'<select id="db-table-select" class="form-group" style="padding:8px;" onchange="loadRawDb()">'

if target in content:
    content = content.replace(target, replace)
    with open('core/static/js/app.js', 'wb') as f:
        f.write(content)
    print("Added onchange to select!")
else:
    print("Target not found.")
