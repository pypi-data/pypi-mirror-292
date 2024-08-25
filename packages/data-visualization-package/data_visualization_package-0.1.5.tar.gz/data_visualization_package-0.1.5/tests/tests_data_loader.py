from data_loader import load_csv, load_json, load_sql

def test_load_csv():
    dataframe = load_csv('path/to/archive.csv')
    assert dataframe is not None
    assert not dataframe.empty

def test_load_json():
    dataframe = load_json('path/to/archive.json')
    assert dataframe is not None
    assert not dataframe.empty

def test_load_sql():
    dataframe = load_sql('path/to/base.db', 'SELECT * FROM table')
    assert dataframe is not None
    assert not dataframe.empty