import pytest
from services.stats_service import calculate_top70_thresholds

def test_top70_under_6_songs():
    stats = {
        i: {'main_artist_id': 1, 'total_views': i*100, 'views_per_day': i*10, 'effective_base_date': '2023-01-01'}
        for i in range(1, 6)
    }
    thresholds = calculate_top70_thresholds(stats)
    assert 1 not in thresholds

def test_top70_6_songs():
    # floor(6 * 0.7) = 4 (index 3 of descending array)
    # 600, 500, 400, [300], 200, 100
    stats = {
        i: {'main_artist_id': 1, 'total_views': i*100, 'views_per_day': i*10, 'effective_base_date': '2023-01-01'}
        for i in range(1, 7)
    }
    thresholds = calculate_top70_thresholds(stats)
    assert 1 in thresholds
    assert thresholds[1]['view_threshold'] == 300
    assert thresholds[1]['vpd_threshold'] == 30

def test_top70_9_songs():
    # floor(9 * 0.7) = 6 (index 5)
    # 900, 800, 700, 600, 500, [400]...
    stats = {
        i: {'main_artist_id': 1, 'total_views': i*100, 'views_per_day': i*10, 'effective_base_date': '2023-01-01'}
        for i in range(1, 10)
    }
    thresholds = calculate_top70_thresholds(stats)
    assert thresholds[1]['view_threshold'] == 400

def test_top70_10_songs():
    # floor(10 * 0.7) = 7 (index 6)
    # 1000..500..[400]...
    stats = {
        i: {'main_artist_id': 1, 'total_views': i*100, 'views_per_day': i*10, 'effective_base_date': '2023-01-01'}
        for i in range(1, 11)
    }
    thresholds = calculate_top70_thresholds(stats)
    assert thresholds[1]['view_threshold'] == 400

def test_top70_11_songs():
    # floor(11 * 0.7) = 7 (index 6)
    # 1100, 1000, 900, 800, 700, 600, [500]...
    stats = {
        i: {'main_artist_id': 1, 'total_views': i*100, 'views_per_day': i*10, 'effective_base_date': '2023-01-01'}
        for i in range(1, 12)
    }
    thresholds = calculate_top70_thresholds(stats)
    assert thresholds[1]['view_threshold'] == 500
