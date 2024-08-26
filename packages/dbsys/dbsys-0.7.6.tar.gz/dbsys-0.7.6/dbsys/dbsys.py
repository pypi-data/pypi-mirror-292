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
from redis.exceptions import ConnectionError, TimeoutError

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
                query = f"SELECT * FROM {self._table_name}"
                return pd.read_sql_query(query, self._engine)
            except ValueError as ve:
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
        return self._redis_client.publish(channel, message)

    def sub(self, channel: str, handler: Optional[Callable[[str, str], None]] = None, exiton: str = "") -> 'DatabaseManager':
        if self._pubsub is not None:
            self.unsub()  # Unsubscribe from any existing subscriptions

        self._pubsub = self._redis_client.pubsub()
        self._close_message = exiton

        def wrapped_handler(message):
            if message['type'] == 'message':
                data = message['data'].decode('utf-8')
                if data == exiton:
                    logger.info(f"Received close message: {exiton}")
                    self._close_flag.set()
                elif handler:
                    handler(channel, data)
                else:
                    logger.info(f"Received message on channel {channel}: {data}")

        self._pubsub.subscribe(**{channel: wrapped_handler})
        
        self._subscriber_thread = threading.Thread(target=self._message_handler_loop, daemon=True)
        self._subscriber_thread.start()

        return self

    def pubsub(self, pub_message: str, pub_channel: str, sub_channel: str, 
               handler: Optional[Callable[[str, str], None]] = None, 
               exiton: str = "CLOSE", 
               wait: Optional[int] = None,
               max_retries: int = 3,
               retry_delay: float = 1.0) -> 'DatabaseManager':
        for attempt in range(max_retries):
            try:
                self._close_flag.clear()
                
                def wrapped_handler(channel, message):
                    if hasattr(self, '_execon_trigger') and message == self._execon_trigger:
                        self._execon_func()
                    if handler:
                        handler(channel, message)
                    else:
                        self.message_handler(channel, message)

                self.sub(sub_channel, wrapped_handler, exiton)
                self.pub(pub_message, pub_channel)

                try:
                    if wait is not None:
                        self._close_flag.wait(timeout=wait)
                    else:
                        self._close_flag.wait()
                except Exception as e:
                    logger.error(f"Error while waiting for close flag: {str(e)}")
                finally:
                    self._close_flag.set()  # Ensure the flag is set even if an exception occurs

                break  # If we get here, the operation was successful
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached. Operation failed.")
                    raise
                time.sleep(retry_delay)
            finally:
                self.unsub(sub_channel)
                if self._pubsub:
                    try:
                        self._pubsub.close()
                    except Exception as e:
                        logger.warning(f"Error closing pubsub connection: {str(e)}")
                
                # Ensure the subscriber thread is terminated
                if self._subscriber_thread and self._subscriber_thread.is_alive():
                    self._subscriber_thread.join(timeout=2)
                    if self._subscriber_thread.is_alive():
                        logger.warning("Subscriber thread did not terminate within the timeout period.")
        
        return self

    def __del__(self):
        self.unsub()
        if hasattr(self, '_redis_client') and self._redis_client is not None:
            self._redis_client.close()

    def unsub(self, channel: Optional[str] = None) -> 'DatabaseManager':
        # Set the close flag to stop the message handler loop
        self._close_flag.set()

        # Wait for the subscriber thread to finish
        if self._subscriber_thread:
            self._subscriber_thread.join(timeout=2)  # Increased timeout for thread to finish
            if self._subscriber_thread.is_alive():
                logger.warning("Subscriber thread did not terminate within the timeout period.")
            self._subscriber_thread = None

        if self._pubsub is not None:
            try:
                # Unsubscribe from specific channel or all channels
                if channel:
                    self._pubsub.unsubscribe(channel)
                else:
                    self._pubsub.unsubscribe()
                    self._pubsub.punsubscribe()  # Unsubscribe from all pattern subscriptions as well
                
                # Close the pubsub connection
                self._pubsub.close()
            except Exception as e:
                logger.warning(f"Error during unsubscribe: {str(e)}")
            finally:
                self._pubsub = None

        # Clear the close flag
        self._close_flag.clear()

        # Clear message history for the unsubscribed channel(s)
        if channel:
            self._message_history.pop(channel, None)
        else:
            self._message_history.clear()

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
        try:
            while not self._close_flag.is_set():
                message = self._pubsub.get_message(timeout=1)
                if message:
                    if message['type'] == 'message':
                        channel = message['channel'].decode('utf-8')
                        data = message['data'].decode('utf-8')
                        if data == self._close_message:
                            logger.info(f"Received close message: {self._close_message}")
                            self._close_flag.set()
                            break
                        else:
                            self.message_handler(channel, data)
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Redis connection closed: {str(e)}")
        except Exception as e:
            logger.error(f"Error in message handler loop: {str(e)}")
        finally:
            logger.info("Message handler loop ended")
            if self._pubsub:
                try:
                    self._pubsub.close()
                except Exception as e:
                    logger.warning(f"Error closing pubsub connection: {str(e)}")

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

    def stream(self, stream_name: str) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("Stream operations are only available for Redis")
        self._stream_name = stream_name
        return self

    def stream_add(self, data: Dict[str, str]) -> 'DatabaseManager':
        if not hasattr(self, '_stream_name'):
            raise ValueError("Stream name not set. Use .stream() first.")
        self._redis_client.xadd(self._stream_name, data)
        return self

    def stream_read(self, count: int = 100, block: int = None) -> Dict[str, List[Dict[str, Any]]]:
        if not hasattr(self, '_stream_name'):
            raise ValueError("Stream name not set. Use .stream() first.")
        raw_data = self._redis_client.xread({self._stream_name: '0'}, count=count, block=block)
        
        # Process the raw data into a more user-friendly dictionary format
        result = {}
        for stream, messages in raw_data:
            stream_name = stream.decode('utf-8')
            result[stream_name] = []
            for message_id, message_data in messages:
                entry = {
                    'id': message_id.decode('utf-8'),
                    'data': {k.decode('utf-8'): v.decode('utf-8') for k, v in message_data.items()}
                }
                result[stream_name].append(entry)
        
        return result

    def json(self, key: str) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("JSON operations are only available for Redis")
        self._json_key = key
        return self

    def json_set(self, data: Dict[str, Any]) -> 'DatabaseManager':
        if not hasattr(self, '_json_key'):
            raise ValueError("JSON key not set. Use .json() first.")
        self._redis_client.json().set(self._json_key, '.', json.dumps(data))
        return self

    def json_get(self) -> Dict[str, Any]:
        if not hasattr(self, '_json_key'):
            raise ValueError("JSON key not set. Use .json() first.")
        result = self._redis_client.json().get(self._json_key)
        return json.loads(result) if result else None

    def list(self, key: str) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("List operations are only available for Redis")
        self._list_key = key
        return self

    def list_push(self, *values) -> 'DatabaseManager':
        if not hasattr(self, '_list_key'):
            raise ValueError("List key not set. Use .list() first.")
        self._redis_client.rpush(self._list_key, *values)
        return self

    def list_get(self, start: int = 0, end: int = -1) -> List[str]:
        if not hasattr(self, '_list_key'):
            raise ValueError("List key not set. Use .list() first.")
        return self._redis_client.lrange(self._list_key, start, end)

    def string(self, key: str) -> 'DatabaseManager':
        if self._base != 'redis':
            raise ValueError("String operations are only available for Redis")
        self._string_key = key
        return self

    def string_set(self, value: str) -> 'DatabaseManager':
        if not hasattr(self, '_string_key'):
            raise ValueError("String key not set. Use .string() first.")
        self._redis_client.set(self._string_key, value)
        return self

    def string_get(self) -> Optional[str]:
        if not hasattr(self, '_string_key'):
            raise ValueError("String key not set. Use .string() first.")
        return self._redis_client.get(self._string_key)

    def execon(self, trigger: str, func: Callable[..., Any], *args, **kwargs) -> 'DatabaseManager':
        """
        Set up a function to be executed when a specific message is received during pubsub.

        Args:
            trigger (str): The message that triggers the function execution.
            func (Callable[..., Any]): The function to be executed when the trigger is received.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            DatabaseManager: The current instance for method chaining.
        """
        self._execon_trigger = trigger
        self._execon_func = lambda: func(*args, **kwargs)
        return self