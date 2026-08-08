import codecs
import re

with codecs.open('core/static/js/app.js', 'r', 'cp932') as f:
    content = f.read()

target = """            const keys = Object.keys(data[0]);
            let html = '<table><thead><tr>' + keys.map(k => `<th>${k}</th>`).join('') + '</tr></thead><tbody>';
            data.forEach(row => {
                html += '<tr>' + keys.map(k => `<td>${row[k] !== null ? row[k] : ''}</td>`).join('') + '</tr>';
            });
            html += '</tbody></table>';
            out.innerHTML = html;"""

replace = """            window.currentRawDbData = data;
            window.currentRawDbCols = Object.keys(data[0]);
            window.renderRawDbTable = function() {
                const keys = window.currentRawDbCols;
                const d = window.currentRawDbData;
                let html = '<table><thead><tr>' + keys.map(k => `<th draggable="true" data-key="${k}">${k}</th>`).join('') + '</tr></thead><tbody>';
                d.forEach(row => {
                    html += '<tr>' + keys.map(k => `<td>${row[k] !== null ? row[k] : ''}</td>`).join('') + '</tr>';
                });
                html += '</tbody></table>';
                out.innerHTML = html;
                
                // Attach D&D events
                let draggedCol = null;
                out.querySelectorAll('th[draggable="true"]').forEach(th => {
                    th.addEventListener('dragstart', (e) => {
                        draggedCol = th.getAttribute('data-key');
                        e.dataTransfer.effectAllowed = 'move';
                        e.dataTransfer.setData('text/plain', draggedCol);
                    });
                    th.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        th.classList.add('drag-over');
                    });
                    th.addEventListener('dragleave', () => {
                        th.classList.remove('drag-over');
                    });
                    th.addEventListener('drop', (e) => {
                        e.preventDefault();
                        th.classList.remove('drag-over');
                        const targetCol = th.getAttribute('data-key');
                        if (draggedCol && targetCol && draggedCol !== targetCol) {
                            const fromIdx = window.currentRawDbCols.indexOf(draggedCol);
                            const toIdx = window.currentRawDbCols.indexOf(targetCol);
                            if (fromIdx !== -1 && toIdx !== -1) {
                                const [moved] = window.currentRawDbCols.splice(fromIdx, 1);
                                window.currentRawDbCols.splice(toIdx, 0, moved);
                                window.renderRawDbTable();
                            }
                        }
                    });
                });
            };
            window.renderRawDbTable();"""

if target in content:
    content = content.replace(target, replace)
    with codecs.open('core/static/js/app.js', 'w', 'cp932') as f:
        f.write(content)
    print("Updated app.js for D&D!")
else:
    print("Target not found. Trying with regex or CR LF.")
    target_win = target.replace('\n', '\r\n')
    if target_win in content:
        content = content.replace(target_win, replace.replace('\n', '\r\n'))
        with codecs.open('core/static/js/app.js', 'w', 'cp932') as f:
            f.write(content)
        print("Updated app.js with CR LF!")
    else:
        print("Not found at all!")
