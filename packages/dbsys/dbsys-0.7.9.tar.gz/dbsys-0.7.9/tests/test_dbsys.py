import pytest
import pandas as pd
from sqlalchemy import create_engine, text
from dbsys.dbsys import DatabaseManager, TableNotFoundError, DatabaseError

@pytest.fixture
def db_manager():
    # Use an in-memory SQLite database for testing
    return DatabaseManager('sqlite:///:memory:')

def test_table_creation(db_manager):
    data = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    db_manager.table('test_table').create(data)
    
    # Verify the table was created
    result = db_manager.table('test_table').read()
    pd.testing.assert_frame_equal(result, data)

def test_table_write(db_manager):
    initial_data = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    db_manager.table('test_table').create(initial_data)
    
    new_data = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    db_manager.table('test_table').write(new_data)
    
    # Verify the table was overwritten
    result = db_manager.table('test_table').read()
    pd.testing.assert_frame_equal(result, new_data)

def test_delete_table(db_manager):
    data = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    db_manager.table('test_table').create(data)
    
    db_manager.table('test_table').delete_table()
    
    # Verify the table was deleted
    with pytest.raises(TableNotFoundError):
        db_manager.table('test_table').read()

def test_delete_row(db_manager):
    data = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    db_manager.table('test_table').create(data)
    
    db_manager.table('test_table').delete_row({'id': 2})
    
    result = db_manager.table('test_table').read()
    expected = pd.DataFrame({'id': [1, 3], 'name': ['Alice', 'Charlie']})
    pd.testing.assert_frame_equal(result, expected)

def test_search(db_manager):
    data = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    db_manager.table('test_table').create(data)
    
    result = db_manager.table('test_table').search({'name': 'ob'})
    expected = pd.DataFrame({'id': [2], 'name': ['Bob']})
    pd.testing.assert_frame_equal(result, expected)

def test_backup_and_restore(db_manager, tmp_path):
    data = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    db_manager.table('test_table').create(data)
    
    backup_file = tmp_path / "backup.json"
    db_manager.table('test_table').backup(str(backup_file))
    
    # Clear the table
    db_manager.table('test_table').delete_table()
    db_manager.table('test_table').create(pd.DataFrame())
    
    # Restore from backup
    db_manager.table('test_table').restore(str(backup_file))
    
    result = db_manager.table('test_table').read()
    pd.testing.assert_frame_equal(result, data)

def test_execute_query(db_manager):
    data = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    db_manager.table('test_table').create(data)
    
    result = db_manager.execute_query("SELECT * FROM test_table WHERE id > :id", {'id': 1})
    expected = pd.DataFrame({'id': [2, 3], 'name': ['Bob', 'Charlie']})
    pd.testing.assert_frame_equal(result, expected)

def test_invalid_table_name(db_manager):
    with pytest.raises(ValueError):
        db_manager.read()

def test_table_not_found(db_manager):
    with pytest.raises(TableNotFoundError):
        db_manager.table('non_existent_table').read()

def test_invalid_search_conditions(db_manager):
    db_manager.table('test_table').create(pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']}))
    
    with pytest.raises(ValueError):
        db_manager.table('test_table').search({})

    with pytest.raises(ValueError):
        db_manager.table('test_table').search("")

def test_database_error_handling(db_manager):
    with pytest.raises(DatabaseError):
        db_manager.execute_query("INVALID SQL QUERY")