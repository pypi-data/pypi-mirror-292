from data_loader import load_csv, load_json, load_sql

def test_load_csv():
    dataframe = load_csv('test_archives/test.csv')
    assert dataframe is not None
    assert not dataframe.empty

def test_load_json():
    dataframe = load_json('test_archives/test.json')
    assert dataframe is not None
    assert not dataframe.empty

def test_load_sql():
    query = 'SELECT * FROM people'
    dataframe = load_sql('test_archives/test.db', query)
    assert dataframe is not None