import logging
import pandas as pd
import json
from typing import Dict, Any, Optional, Union, List, Callable
from sqlalchemy import create_engine, text, MetaData, Table, Column, exc as sa_exc
from sqlalchemy.engine import Engine
from pathlib import Path
import redis
from urllib.parse import urlparse
import threading
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class TableNotFoundError(DatabaseError):
    """Raised when a specified table is not found in the database."""
    pass

class ColumnNotFoundError(DatabaseError):
    """Raised when a specified column is not found in the table."""
    pass

class InvalidOperationError(DatabaseError):
    """Raised when an invalid operation is attempted."""
    pass

class DatabaseManager:
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._table_name = None
        self._pubsub = None
        self._subscriber_thread = None
        self._close_flag = threading.Event()
        self._close_message = None
        self._message_history = defaultdict(list)

        parsed_url = urlparse(connection_string)
        if parsed_url.scheme == 'redis':
            self._base = 'redis'
            self._redis_client = redis.Redis.from_url(connection_string)
            self._engine = None
        elif parsed_url.scheme in ['postgresql', 'mysql', 'sqlite']:
            self._base = 'sql'
            self._engine = create_engine(connection_string)
            self._redis_client = None
        else:
            raise ValueError(f"Unsupported database type: {parsed_url.scheme}")

    def table(self, table_name: str) -> 'DatabaseManager':
        self._table_name = f'"{table_name}"'
        return self

    def read(self) -> pd.DataFrame:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            try:
                return pd.read_sql_table(self._table_name, self._engine)
            except ValueError as ve:
                if "Table not found" in str(ve):
                    raise TableNotFoundError(f"Table '{self._table_name}' not found in the database.")
                raise DatabaseError(f"Error reading table: {str(ve)}")
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Database operation failed: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Read operation not implemented for Redis")

    def write(self, data: pd.DataFrame) -> bool:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            try:
                data.to_sql(self._table_name, self._engine, if_exists='replace', index=False)
                return True
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Failed to write to table: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Write operation not implemented for Redis")

    def create(self, data: pd.DataFrame) -> bool:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            try:
                data.to_sql(self._table_name, self._engine, if_exists='fail', index=False)
                return True
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Failed to create table: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Create operation not implemented for Redis")

    def delete_table(self) -> bool:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            try:
                with self._engine.connect() as connection:
                    connection.execute(text(f"DROP TABLE IF EXISTS {self._table_name}"))
                return True
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Failed to delete table: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Delete table operation not implemented for Redis")

    def delete_row(self, row_identifier: Dict[str, Any]) -> int:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            if not row_identifier:
                raise ValueError("Row identifier must be provided for delete row operation")
            
            try:
                conditions = []
                for key, value in row_identifier.items():
                    if value is None:
                        conditions.append(f'"{key}" IS NULL')
                    else:
                        conditions.append(f'"{key}" = :{key}')
                
                where_clause = " AND ".join(conditions)
                query = f"DELETE FROM {self._table_name} WHERE {where_clause}"
                
                with self._engine.connect() as connection:
                    result = connection.execute(
                        text(query),
                        {k: v for k, v in row_identifier.items() if v is not None}
                    )
                    connection.commit()
                    return result.rowcount
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Failed to delete row: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Delete row operation not implemented for Redis")

    def search(self, conditions: Union[Dict[str, Any], str], limit: Optional[int] = None, case_sensitive: bool = False) -> pd.DataFrame:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")
            
            try:
                if isinstance(conditions, dict):
                    if not conditions:
                        raise ValueError("Search conditions dictionary cannot be empty")
                    where_clauses = []
                    search_conditions = {}
                    for i, (col, val) in enumerate(conditions.items()):
                        if val is None:
                            raise ValueError(f"Search value for column '{col}' cannot be None")
                        param_name = f"param_{i}"
                        if case_sensitive:
                            where_clauses.append(f'"{col}" LIKE :{param_name}')
                        else:
                            where_clauses.append(f'LOWER("{col}"::text) LIKE LOWER(:{param_name})')
                        search_conditions[param_name] = f"%{val}%"
                    where_clause = " AND ".join(where_clauses)
                elif isinstance(conditions, str):
                    if not conditions.strip():
                        raise ValueError("Search string cannot be empty")
                    where_clause = conditions
                    search_conditions = {}
                else:
                    raise ValueError("conditions must be either a non-empty dictionary or a non-empty string")

                query = f"SELECT * FROM {self._table_name} WHERE {where_clause}"
                if limit is not None:
                    query += f" LIMIT {limit}"
                
                logger.debug(f"Executing SQL: {query}")
                logger.debug(f"With parameters: {search_conditions}")
                
                with self._engine.connect() as connection:
                    result = connection.execute(text(query), search_conditions)
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Search operation failed: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Search operation not implemented for Redis")

    def backup(self, file_path: str, columns: Optional[List[str]] = None) -> bool:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")

            try:
                data = self.read()

                if columns:
                    missing_columns = set(columns) - set(data.columns)
                    if missing_columns:
                        raise ValueError(f"Columns not found in table: {', '.join(missing_columns)}")
                    data_to_backup = data[columns]
                else:
                    data_to_backup = data

                json_data = data_to_backup.to_json(orient='records', date_format='iso')

                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, 'w') as f:
                    f.write(json_data)

                logger.info(f"{self._table_name}: Backup created successfully at {file_path}")
                return True

            except (sa_exc.SQLAlchemyError, IOError) as e:
                raise DatabaseError(f"Failed to create backup: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Backup operation not implemented for Redis")

    def restore(self, file_path: str, mode: str = 'replace') -> bool:
        if self._base == 'sql':
            if not self._table_name:
                raise ValueError("Table name not set. Use .table() first.")

            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")

            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)

                df = pd.DataFrame(json_data)

                if mode == 'replace':
                    return self.write(df)
                elif mode == 'append':
                    df.to_sql(self._table_name, self._engine, if_exists='append', index=False)
                    return True
                elif mode == 'upsert':
                    metadata = MetaData()
                    table = Table(self._table_name, metadata, autoload_with=self._engine)
                    pk_columns = [key.name for key in table.primary_key]

                    if not pk_columns:
                        raise ValueError("Cannot perform upsert without primary key")

                    for _, row in df.iterrows():
                        query = f"""
                        INSERT INTO {self._table_name} ({', '.join(df.columns)})
                        VALUES ({', '.join([':' + col for col in df.columns])})
                        ON CONFLICT ({', '.join(pk_columns)})
                        DO UPDATE SET {', '.join([f"{col} = excluded.{col}" for col in df.columns if col not in pk_columns])}
                        """
                        with self._engine.connect() as conn:
                            conn.execute(text(query), row.to_dict())
                            conn.commit()
                    return True
                else:
                    raise ValueError("Invalid mode. Use 'replace', 'append', or 'upsert'.")

            except (sa_exc.SQLAlchemyError, IOError, json.JSONDecodeError) as e:
                raise DatabaseError(f"Failed to restore from backup: {str(e)}")
        elif self._base == 'redis':
            raise NotImplementedError("Restore operation not implemented for Redis")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Union[pd.DataFrame, int]:
        if self._base == 'sql':
            try:
                with self._engine.connect() as connection:
                    result = connection.execute(text(query), params or {})
                    if query.strip().upper().startswith('SELECT'):
                        return pd.DataFrame(result.fetchall(), columns=result.keys())
                    else:
                        connection.commit()
                        return result.rowcount
            except sa_exc.SQLAlchemyError as e:
                raise DatabaseError(f"Query execution failed: {str(e)}")
        else:
            raise ValueError("execute_query method is only available for SQL databases")

    # Redis-specific methods remain largely unchanged
    def pub(self, message: str, channel: str) -> int:
        if self._base != 'redis':
            raise ValueError("pub method is only available for Redis")
        return self._redis_client.publish(channel, message)

    def sub(self, channel: str, handler: Optional[Callable[[str, str], None]] = None, exiton: str = "") -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("sub method is only available for Redis")

        if self._pubsub is None:
            self._pubsub = self._redis_client.pubsub()

        wrapped_handler = self._message_handler_wrapper(handler, exiton)
        self._pubsub.subscribe(**{channel: wrapped_handler})
        
        if self._subscriber_thread is None or not self._subscriber_thread.is_alive():
            self._subscriber_thread = threading.Thread(target=self._message_handler_loop, daemon=True)
            self._subscriber_thread.start()

        return self

    def pubsub(self, pub_message: str, pub_channel: str, sub_channel: str, 
               handler: Optional[Callable[[str, str], None]] = None, 
               exiton: str = "CLOSE", 
               wait: Optional[int] = None) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("pubsub method is only available for Redis")

        self._close_flag.clear()
        self._close_message = exiton

        self.sub(sub_channel, handler, exiton)
        publish_result = self.pub(pub_message, pub_channel)
        logger.info(f"Published message to {publish_result} subscribers")

        if wait is not None:
            self._close_flag.wait(timeout=wait)
        else:
            self._close_flag.wait()

        self.unsub(sub_channel)

        return self

    def unsub(self, channel: Optional[str] = None) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("unsub method is only available for Redis")

        if self._pubsub is not None:
            if channel:
                self._pubsub.unsubscribe(channel)
            else:
                self._pubsub.unsubscribe()

            if not self._pubsub.channels:
                self._subscriber_thread = None

        self._close_flag.clear()
        return self

    def get_stored_messages(self, channel: str) -> List[str]:
        return self._message_history.get(channel, [])

    def clear_stored_messages(self, channel: Optional[str] = None) -> 'DatabaseManager':
        if channel:
            self._message_history[channel] = []
        else:
            self._message_history.clear()
        return self

    def _message_handler_wrapper(self, user_handler: Optional[Callable[[str, str], None]], exiton: str) -> Callable[[dict], None]:
        def wrapper(message):
            if message['type'] == 'message':
                channel = message['channel'].decode('utf-8')
                data = message['data'].decode('utf-8')
                self._message_history[channel].append(data)
                if data == exiton:
                    logger.info(f"Received close message: {exiton}")
                    self._close_flag.set()
                else:
                    if user_handler:
                        user_handler(channel, data)
                    else:
                        self.message_handler(channel, data)
        return wrapper

    def _message_handler_loop(self):
        for message in self._pubsub.listen():
            if self._close_flag.is_set():
                logger.info("Closing message handler loop")
                break

    def message_handler(self, channel: str, message: str):
        """
        Default message handler for received messages.

        Args:
            channel (str): The channel on which the message was received.
            message (str): The received message.
        """
        logger.info(f"Received message on channel {channel}: {message}")

    def __str__(self) -> str:
        base_type = self._base
        table_name = self._table_name or "Not set"
        redis_info = f", subscribed channels: {list(self._pubsub.channels) if self._pubsub else None}" if self._base == 'redis' else ""
        return f"DatabaseManager(base={base_type}, table={table_name}{redis_info})"