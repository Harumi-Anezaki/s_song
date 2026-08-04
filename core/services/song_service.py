from typing import List, Optional
from database import get_db

def merge_songs(source_ids: List[int], target_id: Optional[int], new_title: str, main_artist_id: Optional[int], sub_artist_ids: List[int]) -> int:
    """
    複数の曲を1つの曲に統合します。
    
    Args:
        source_ids (List[int]): 統合元となる曲のIDリスト。
        target_id (Optional[int]): 統合先の曲ID。Noneの場合は新しく作成します。
        new_title (str): 統合後の曲タイトル。
        main_artist_id (Optional[int]): 統合後のメインアーティストID。
        sub_artist_ids (List[int]): 統合後のサブアーティストIDのリスト。
        
    Returns:
        int: 統合後の最終的な曲ID。
        
    Raises:
        Exception: データベース更新中にエラーが発生した場合にロールバックして送出します。
    """
    with get_db() as conn:
        try:
            if not target_id:
                cursor = conn.execute(
                    "INSERT INTO songs (title, main_artist_id, tag_b) VALUES (?, ?, '[]')", 
                    (new_title, main_artist_id)
                )
                target_id = cursor.lastrowid
            else:
                conn.execute(
                    "UPDATE songs SET title = ?, main_artist_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_title, main_artist_id, target_id)
                )

            conn.execute("DELETE FROM song_sub_artists WHERE song_id = ?", (target_id,))
            if sub_artist_ids:
                for a_id in sub_artist_ids:
                    if a_id != main_artist_id:
                        conn.execute("INSERT INTO song_sub_artists (song_id, artist_id) VALUES (?, ?)", (target_id, a_id))
            
            for s_id in source_ids:
                if s_id == target_id:
                    continue
                
                conn.execute("UPDATE videos SET song_id = ?, updated_at = CURRENT_TIMESTAMP WHERE song_id = ?", (target_id, s_id))
                conn.execute("UPDATE songs SET is_archived = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (s_id,))
                conn.execute("INSERT INTO merge_history (source_song_id, target_song_id) VALUES (?, ?)", (s_id, target_id))

            conn.commit()
            return target_id
        except Exception as e:
            conn.rollback()
            raise e
