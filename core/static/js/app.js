document.addEventListener('DOMContentLoaded', () => {
    initRouter();
});

const views = {
    'songs': renderSongsView,
    'youtube': renderYoutubeView,
    'artists': renderArtistsView,
    'excluded': renderExcludedView,
    'backup': renderBackupView
};

function initRouter() {
    const hash = window.location.hash.replace('#', '') || 'songs';
    navigate(hash);

    window.addEventListener('hashchange', () => {
        const newHash = window.location.hash.replace('#', '') || 'songs';
        navigate(newHash);
    });
}

function navigate(viewName) {
    document.querySelectorAll('.sidebar-item').forEach(el => {
        el.classList.remove('active');
        if (el.getAttribute('href') === `#${viewName}`) {
            el.classList.add('active');
        }
    });

    const mainContent = document.getElementById('view-content');
    if (views[viewName]) {
        views[viewName](mainContent);
    } else {
        mainContent.innerHTML = '<h1>Not Found</h1>';
    }
}

const VIEW_TABS = [
    'おはこ', '高音練習', '盛上', 'カラオケ', '聞流日本', '聞流海外', 
    'HIPHOP', '沖縄', '排除', '時代遅れ', '未DL', 'すべて'
];

let currentView = 'おはこ';

function renderSongsView(container) {
    let tabsHtml = '<div class="view-tabs" style="display:flex; gap:16px; margin-bottom:16px; border-bottom:1px solid var(--border-color);">';
    VIEW_TABS.forEach(tab => {
        const active = (tab === currentView) ? 'border-bottom: 2px solid var(--primary-color); font-weight:bold;' : '';
        tabsHtml += `<div style="padding:8px 0; cursor:pointer; ${active}" onclick="changeSongsView('${tab}')">${tab}</div>`;
    });
    tabsHtml += '</div>';

    container.innerHTML = `
        <h1>選曲</h1>
        ${tabsHtml}
        <div id="songs-list" class="table-container">読み込み中...</div>
    `;
    loadSongsView(currentView);
}

window.changeSongsView = function(viewName) {
    currentView = viewName;
    navigate('songs'); // re-render
};

window.loadSongsView = async function(viewName) {
    try {
        const res = await fetch(\`/api/views/\${viewName}\`);
        const data = await res.json();
        
        if(data.error) {
            document.getElementById('songs-list').innerHTML = \`<span style="color:red">\${data.error}</span>\`;
            return;
        }
        
        if(data.length === 0) {
            document.getElementById('songs-list').innerHTML = 'データがありません。';
            return;
        }

        let html = \`<table>
            <thead>
                <tr>
                    <th>曲名</th>
                    <th>歌手</th>
                    <th>合計再生数</th>
                    <th>回/日</th>
                    <th>タグA</th>
                    <th>DL</th>
                    <th>時代遅れ</th>
                </tr>
            </thead>
            <tbody>\`;
            
        data.forEach(s => {
            const vpd = typeof s.views_per_day === 'number' ? s.views_per_day.toFixed(2) : s.views_per_day;
            const outdated = s.is_outdated ? '⚠️' : '';
            html += \`<tr style="cursor:pointer;" onclick="openSongDetail(\${s.id})">
                <td>\${s.title}</td>
                <td>\${s.artist_name || ''}</td>
                <td>\${s.total_views.toLocaleString()}</td>
                <td>\${vpd}</td>
                <td>\${s.tag_a || ''}</td>
                <td>\${s.dl_status}</td>
                <td>\${outdated}</td>
            </tr>\`;
        });
        html += '</tbody></table>';
        document.getElementById('songs-list').innerHTML = html;
        
    } catch(e) {
        document.getElementById('songs-list').innerHTML = 'エラー: ' + e;
    }
};

function renderYoutubeView(container) {
    container.innerHTML = `
        <h1>YouTube検索</h1>
        <div class="form-group">
            <label>検索キーワード</label>
            <input type="text" id="yt-keyword" placeholder="キーワード">
        </div>
        <div class="form-group">
            <label>最低再生回数</label>
            <select id="yt-min-views">
                <option value="0">制限なし</option>
                <option value="10000000">1000万回</option>
                <option value="100000000">1億回</option>
            </select>
        </div>
        <button class="btn btn-primary" id="btn-search">検索</button>
        <div id="yt-status" style="margin-top: 16px;"></div>
        <div id="yt-results" class="table-container"></div>
    `;

    document.getElementById('btn-search').addEventListener('click', async () => {
        const keyword = document.getElementById('yt-keyword').value;
        const minViews = document.getElementById('yt-min-views').value;
        const statusEl = document.getElementById('yt-status');
        const resultsEl = document.getElementById('yt-results');
        
        if (!keyword) {
            alert('キーワードを入力してください');
            return;
        }

        statusEl.innerHTML = '<span class="loading">検索中...</span>';
        resultsEl.innerHTML = '';

        try {
            const res = await fetch('/api/youtube/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword, min_views: parseInt(minViews) })
            });
            const data = await res.json();
            
            if (data.error) {
                statusEl.innerHTML = `<span style="color:var(--danger-color)">エラー: ${data.error}</span>`;
                return;
            }

            statusEl.innerHTML = `${data.results.length}件の動画が見つかりました。`;
            renderYoutubeResults(data.results, resultsEl, keyword);
            
        } catch (e) {
            statusEl.innerHTML = `<span style="color:var(--danger-color)">通信エラー: ${e}</span>`;
        }
    });
}

function renderYoutubeResults(results, container, searchKeyword) {
    if (results.length === 0) return;

    let html = `
        <table>
            <thead>
                <tr>
                    <th>サムネイル</th>
                    <th>タイトル</th>
                    <th>アカウント</th>
                    <th>再生回数</th>
                    <th>投稿日</th>
                    <th>動画時間</th>
                    <th>状態</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
    `;

    window.ytSearchResults = results;

    results.forEach((v, index) => {
        html += `
            <tr id="row-${v.id}">
                <td><img src="${v.thumbnail_url}" width="120" style="border-radius:4px"></td>
                <td><a href="${v.url}" target="_blank">${v.title}</a></td>
                <td>${v.channel_name}</td>
                <td>${v.view_count.toLocaleString()}</td>
                <td>${v.published_at.substring(0, 10)}</td>
                <td>${v.formatted_duration}</td>
                <td id="status-${v.id}">${v.db_status}</td>
                <td>
                    <button class="btn" onclick="excludeVideo('${v.id}', ${index}, '${searchKeyword}')">除外</button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
        <div style="margin-top: 16px;">
            <button class="btn btn-primary" onclick="registerRemainingAsTemp()">残った動画を仮曲として登録</button>
        </div>
    `;

    container.innerHTML = html;
}

window.excludeVideo = async function(id, index, searchKeyword) {
    const video = window.ytSearchResults[index];
    try {
        const res = await fetch('/api/videos/exclude', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: id,
                reason: '手動除外',
                search_keyword: searchKeyword,
                title: video.title,
                url: video.url,
                channel_name: video.channel_name
            })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById(`row-${id}`).style.opacity = '0.5';
            document.getElementById(`status-${id}`).innerText = 'excluded';
            video.db_status = 'excluded';
        } else {
            alert('除外失敗: ' + data.error);
        }
    } catch (e) {
        alert('通信エラー: ' + e);
    }
};

window.registerRemainingAsTemp = async function() {
    const remaining = window.ytSearchResults.filter(v => v.db_status === 'new');
    if (remaining.length === 0) {
        alert('登録する新しい動画がありません。');
        return;
    }

    if (!confirm(`${remaining.length}件の動画を仮曲として登録しますか？`)) {
        return;
    }

    try {
        const res = await fetch('/api/songs/register_temp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ videos: remaining })
        });
        const data = await res.json();
        
        if (data.success) {
            alert('登録が完了しました。');
            remaining.forEach(v => {
                v.db_status = 'registered';
                const statusEl = document.getElementById(`status-${v.id}`);
                if (statusEl) statusEl.innerText = 'registered';
            });
        } else {
            alert('登録失敗: ' + data.error);
        }
    } catch (e) {
        alert('通信エラー: ' + e);
    }
};

function renderArtistsView(container) {
    container.innerHTML = `
        <h1>歌手</h1>
        <div style="display:flex; gap:16px; margin-bottom:16px;">
            <input type="text" id="new-artist-name" placeholder="歌手名">
            <input type="text" id="new-artist-phonetic" placeholder="ふりがな">
            <input type="number" id="new-artist-rating" placeholder="好き度" value="0">
            <button class="btn btn-primary" onclick="addArtist()">追加</button>
        </div>
        <div id="artists-list" class="table-container"></div>
    `;
    loadArtists();
}

window.loadArtists = async function() {
    try {
        const res = await fetch('/api/artists');
        const artists = await res.json();
        
        let html = \`<table><thead><tr><th>ID</th><th>歌手名</th><th>ふりがな</th><th>好き度</th><th>メモ</th></tr></thead><tbody>\`;
        artists.forEach(a => {
            html += \`<tr>
                <td>\${a.id}</td>
                <td>\${a.name}</td>
                <td>\${a.phonetic_name || ''}</td>
                <td>\${a.rating}</td>
                <td>\${a.memo || ''}</td>
            </tr>\`;
        });
        html += \`</tbody></table>\`;
        document.getElementById('artists-list').innerHTML = html;
    } catch(e) {
        document.getElementById('artists-list').innerHTML = 'エラー: ' + e;
    }
};

window.addArtist = async function() {
    const name = document.getElementById('new-artist-name').value;
    const phonetic = document.getElementById('new-artist-phonetic').value;
    const rating = document.getElementById('new-artist-rating').value;
    
    if(!name) {
        alert('歌手名は必須です'); return;
    }
    
    await fetch('/api/artists', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: name, phonetic_name: phonetic, rating: parseInt(rating)})
    });
    
    document.getElementById('new-artist-name').value = '';
    document.getElementById('new-artist-phonetic').value = '';
    loadArtists();
};

function renderExcludedView(container) {
    container.innerHTML = '<h1>除外動画</h1><p>実装予定</p>';
}

function renderBackupView(container) {
    container.innerHTML = `
        <h1>設定とバックアップ</h1>
        <div style="margin-bottom: 24px;">
            <h2>データのエクスポート</h2>
            <p>現在のデータをJSON形式でバックアップとしてダウンロードします。</p>
            <button class="btn btn-primary" onclick="exportData()">エクスポート</button>
        </div>
        <div>
            <h2>データの復元 (インポート)</h2>
            <p>※注意: 現在のデータベース内容は完全に消去され、JSONファイルの内容で全置換されます。</p>
            <input type="file" id="backup-file-input" accept=".json">
            <button class="btn" style="background-color: var(--danger-color); color: white;" onclick="importData()">復元を実行</button>
        </div>
        <div style="margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border-color);">
            <h2>システム操作</h2>
            <p>バックグラウンドで動作しているサーバーを終了します。アプリを完全に閉じる際に使用してください。</p>
            <button class="btn" style="background-color: #333; color: white;" onclick="shutdownServer()">サーバーを終了する</button>
        </div>
    `;
}

window.shutdownServer = async function() {
    if(!confirm('サーバーを終了しますか？（画面を閉じても起動しなくなります）')) return;
    try {
        await fetch('/api/shutdown', { method: 'POST' });
        document.body.innerHTML = '<h1>サーバーを終了しました</h1><p>このウィンドウ（タブ）を閉じてください。</p>';
    } catch(e) {
        alert('終了要求の送信に失敗しました（既に終了している可能性があります）。');
    }
};

window.exportData = async function() {
    try {
        const res = await fetch('/api/backup/export');
        const data = await res.json();
        if(data.success) {
            const blob = new Blob([data.data], {type: "application/json"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0,19);
            a.download = \`karaoke_backup_\${dateStr}.json\`;
            a.href = url;
            a.click();
        } else {
            alert('エクスポート失敗: ' + data.error);
        }
    } catch (e) {
        alert('通信エラー: ' + e);
    }
};

window.importData = function() {
    const fileInput = document.getElementById('backup-file-input');
    if(fileInput.files.length === 0) {
        alert('復元するJSONファイルを選択してください。');
        return;
    }
    
    if(!confirm('現在のデータは完全に上書きされます。本当によろしいですか？')) {
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const jsonStr = e.target.result;
            const res = await fetch('/api/backup/import', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({json_str: jsonStr})
            });
            const data = await res.json();
            if(data.success) {
                alert('復元が完了しました。');
            } else {
                alert('復元失敗: ' + data.error);
            }
        } catch(err) {
            alert('エラー: ' + err);
        }
    };
    reader.readAsText(file);
};

window.openSongDetail = async function(songId) {
    const peak = document.getElementById('side-peak');
    if(!peak) return;
    peak.style.display = 'flex';
    document.getElementById('side-peak-content').innerHTML = '読み込み中...';
    try {
        const res = await fetch(\`/api/songs/\${songId}\`);
        const data = await res.json();
        
        let html = \`<h2>\${data.song.title}</h2>\`;
        html += \`<p>歌手: \${data.main_artist ? data.main_artist.name : '未設定'}</p>\`;
        html += \`<p>合計再生数: \${data.song.total_views || 0}</p>\`;
        html += \`<p>DL状況: 
            <select id="song-dl-status">
                <option value="未DL" \${data.song.dl_status === '未DL' ? 'selected' : ''}>未DL</option>
                <option value="DL済" \${data.song.dl_status === 'DL済' ? 'selected' : ''}>DL済</option>
                <option value="不要" \${data.song.dl_status === '不要' ? 'selected' : ''}>不要</option>
            </select>
        </p>\`;
        html += \`<h3>動画</h3><ul>\`;
        data.videos.forEach(v => {
            html += \`<li>\${v.title} (\${v.view_count}回)</li>\`;
        });
        html += \`</ul>\`;
        html += \`<div style="margin-top:16px;">
            <button class="btn btn-primary" onclick="saveSongDetail(\${songId})">保存</button>
            <button class="btn" onclick="closeSidePeak()">閉じる</button>
        </div>\`;
        
        document.getElementById('side-peak-content').innerHTML = html;
    } catch(e) {
        document.getElementById('side-peak-content').innerHTML = 'エラー: ' + e;
    }
};

window.saveSongDetail = async function(songId) {
    const dlStatus = document.getElementById('song-dl-status').value;
    try {
        const res = await fetch(\`/api/songs/\${songId}\`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ dl_status: dlStatus })
        });
        const data = await res.json();
        if (data.success) {
            alert('保存しました');
            closeSidePeak();
            if(window.loadSongsView) loadSongsView(currentView);
        } else {
            alert('エラー: ' + data.error);
        }
    } catch (e) {
        alert('通信エラー: ' + e);
    }
};

window.closeSidePeak = function() {
    const peak = document.getElementById('side-peak');
    if(peak) peak.style.display = 'none';
};
