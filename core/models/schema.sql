PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phonetic_name TEXT,
    rating INTEGER DEFAULT 0,
    memo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    main_artist_id INTEGER,
    tag_a TEXT,
    tag_b TEXT, -- JSON array string
    dl_status TEXT DEFAULT 'NOT_DOWNLOADED',
    auto_base_date TEXT, -- YYYY-MM-DD
    manual_base_date TEXT, -- YYYY-MM-DD
    use_manual_date INTEGER DEFAULT 0, -- boolean 0 or 1
    memo TEXT,
    is_archived INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(main_artist_id) REFERENCES artists(id)
);

CREATE TABLE IF NOT EXISTS song_sub_artists (
    song_id INTEGER,
    artist_id INTEGER,
    PRIMARY KEY(song_id, artist_id),
    FOREIGN KEY(song_id) REFERENCES songs(id) ON DELETE CASCADE,
    FOREIGN KEY(artist_id) REFERENCES artists(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY, -- YouTube Video ID
    song_id INTEGER,
    title TEXT,
    url TEXT,
    view_count INTEGER DEFAULT 0,
    published_at TEXT, -- ISO8601 string or YYYY-MM-DD
    channel_id TEXT,
    channel_name TEXT,
    duration_sec INTEGER DEFAULT 0,
    formatted_duration TEXT,
    thumbnail_url TEXT,
    status TEXT DEFAULT 'unjudged', -- 'unjudged', 'active', 'excluded'
    last_api_update DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(song_id) REFERENCES songs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS excluded_videos (
    id TEXT PRIMARY KEY, -- YouTube Video ID
    reason TEXT,
    excluded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    search_keyword TEXT,
    old_title TEXT,
    old_url TEXT,
    old_channel_name TEXT,
    is_manual_exclusion INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT,
    min_views INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS merge_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_song_id INTEGER,
    target_song_id INTEGER,
    merged_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
