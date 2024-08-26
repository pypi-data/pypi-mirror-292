# dbsys

dbsys is a comprehensive Python library for managing database operations using SQLAlchemy, pandas, and Redis. It provides a high-level interface for common database operations, including reading, writing, creating tables, deleting tables, columns, and rows, as well as advanced features like searching, backup, restore functionality, and Redis pub/sub support.

[![PyPI version](https://badge.fury.io/py/dbsys.svg)](https://badge.fury.io/py/dbsys)
[![Python Versions](https://img.shields.io/pypi/pyversions/dbsys.svg)](https://pypi.org/project/dbsys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What's New in Version 0.7.6

- Added new Redis-specific methods for working with streams, JSON, lists, and strings
- Introduced the `execon` method for executing functions on specific pubsub messages
- Enhanced error handling and retry logic in Redis operations
- Updated documentation with examples for new Redis features
- Minor bug fixes and performance improvements

## Features

- Easy-to-use interface for database operations
- Support for multiple database types through SQLAlchemy
- Redis support for pub/sub operations and key-value storage
- Integration with pandas for efficient data handling
- Comprehensive error handling and custom exceptions
- Backup and restore functionality
- Advanced search capabilities with case-sensitive option
- Deduplication of data
- Custom SQL query execution
- Support for Locksys objects as connection strings
- Improved Redis pub/sub functionality

## Installation

You can install the latest version of dbsys using pip:

```bash
pip install --upgrade dbsys
```

For development purposes, you can install the package with extra dependencies:

```bash
pip install dbsys[dev]
```

This will install additional packages useful for development, such as pytest, flake8, and mypy.

## Quick Start

Here's a comprehensive example of how to use dbsys with SQL databases:

```python
from dbsys import DatabaseManager
import pandas as pd

# Initialize the DatabaseManager
db = DatabaseManager("sqlite:///example.db")

# If you're using Locksys:
# from your_locksys_module import Locksys
# lock = Locksys("Promptsys")
# db = DatabaseManager(lock)

# Create a sample DataFrame
data = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [30, 25, 35, 28],
    'city': ['New York', 'San Francisco', 'London', 'Berlin']
})

# Create a new table and write data
success = db.table("users").create(data)
print(f"Table created successfully: {success}")

# Read the table
result = db.table("users").read()
print("Original data:")
print(result)

# Search for users from a specific city
result = db.table("users").search({"city": "London"})
print("\nUsers from London:")
print(result)

# Update data in the table
new_data = pd.DataFrame({
    'name': ['Eve', 'Frank'],
    'age': [22, 40],
    'city': ['Paris', 'Tokyo']
})
success = db.table("users").write(new_data)
print(f"\nData updated successfully: {success}")

# Read the updated table
result = db.table("users").read()
print("\nUpdated data:")
print(result)

# Delete a specific row
rows_deleted = db.table("users").delete_row({"name": "Frank"})
print(f"\nRows deleted: {rows_deleted}")

# Execute a custom SQL query
result = db.execute_query("SELECT AVG(age) as avg_age FROM users")
print("\nAverage age:")
print(result)

# Backup the table
success = db.table("users").backup("users_backup.json")
print(f"\nBackup created successfully: {success}")

# Delete the table
success = db.table("users").delete_table()
print(f"\nTable deleted successfully: {success}")

# Restore the table from backup
success = db.table("users").restore("users_backup.json")
print(f"\nTable restored successfully: {success}")

# Verify restored data
result = db.table("users").read()
print("\nRestored data:")
print(result)
```

Example of using dbsys with Redis:

```python
from dbsys import DatabaseManager
import time

# Initialize the DatabaseManager with Redis
db = DatabaseManager("redis://localhost:6379/0")

# Publish a message
subscribers = db.pub("Hello, Redis!", "test_channel")
print(f"Message published to {subscribers} subscribers")

# Subscribe to a channel and process messages
def message_handler(channel, message):
    print(f"Received on {channel}: {message}")

db.sub("test_channel", handler=message_handler)

# Publish and subscribe in one operation
db.pubsub("Test message", "pub_channel", "sub_channel", handler=message_handler, wait=5)

# Get stored messages
messages = db.get_stored_messages("sub_channel")
print("Stored messages:", messages)

# Clear stored messages
db.clear_stored_messages()
```

## API Reference

### DatabaseManager

The main class for interacting with the database. It supports both SQL databases and Redis.

#### Constructor

```python
DatabaseManager(connection_string: Union[str, 'Locksys'])
```

Initialize the DatabaseManager with a database URL or a Locksys object.

- `connection_string`: The connection string for the database or a Locksys object.
  - For SQL databases, use SQLAlchemy connection strings.
  - For Redis, use the format: "redis://[[username]:[password]]@localhost:6379/0"
  - For Locksys objects, ensure they have a `get_connection_string()` method.

#### Methods

- `table(table_name: str) -> DatabaseManager`
- `read() -> pd.DataFrame`
- `write(data: pd.DataFrame) -> bool`
- `create(data: pd.DataFrame) -> bool`
- `delete_table() -> bool`
- `delete_row(row_identifier: Dict[str, Any]) -> int`
- `search(conditions: Union[Dict[str, Any], str], limit: Optional[int] = None, case_sensitive: bool = False) -> pd.DataFrame`
- `backup(file_path: str, columns: Optional[List[str]] = None) -> bool`
- `restore(file_path: str, mode: str = 'replace') -> bool`
- `execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> Union[pd.DataFrame, int]`
- `pub(message: str, channel: str) -> int`
- `sub(channel: str, handler: Optional[Callable[[str, str], None]] = None, exiton: str = "") -> DatabaseManager`
- `pubsub(pub_message: str, pub_channel: str, sub_channel: str, handler: Optional[Callable[[str, str], None]] = None, exiton: str = "CLOSE", wait: Optional[int] = None) -> DatabaseManager`
- `unsub(channel: Optional[str] = None) -> DatabaseManager`
- `get_stored_messages(channel: str) -> List[str]`
- `clear_stored_messages(channel: Optional[str] = None) -> DatabaseManager`

For detailed usage of each method, including all parameters and return values, please refer to the docstrings in the source code.

## Error Handling

dbsys provides custom exceptions for better error handling:

- `DatabaseError`: Base exception for database operations.
- `TableNotFoundError`: Raised when a specified table is not found in the database.
- `ColumnNotFoundError`: Raised when a specified column is not found in the table.
- `InvalidOperationError`: Raised when an invalid operation is attempted.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/lifsys/dbsys/issues) on our GitHub repository.

## About Lifsys, Inc

Lifsys, Inc is an AI company dedicated to developing innovative solutions for data management and analysis. For more information, visit [www.lifsys.com](https://www.lifsys.com).

## Changelog

### 0.7.6
- Added new Redis-specific methods for working with streams, JSON, lists, and strings
- Introduced the `execon` method for executing functions on specific pubsub messages
- Enhanced error handling and retry logic in Redis operations
- Updated documentation with examples for new Redis features
- Minor bug fixes and performance improvements

### 0.7.5
- Added type hints and py.typed file for better IDE support
- Improved error handling in Redis operations
- Enhanced documentation with more detailed examples
- Minor bug fixes and performance optimizations
- Updated package metadata for better PyPI representation

### 0.6.0
- Added support for Locksys objects as connection strings
- Updated API to remove the need for `results()` method
- Enhanced error handling for connection string parsing
- Updated documentation and README

### 0.5.0
- Major refactoring of the codebase
- Updated API for better consistency and ease of use
- Enhanced Redis support with pubsub operations
- Improved error handling and logging
- Added case-sensitive option for search operations
- Updated documentation and README

(... previous changelog entries ...)
