import sqlite3
from pathlib import Path
from typing import Union, Optional, Dict, List
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteDatabaseHandler:
    """
    A handler class for interacting with SQLite databases, including creating tables
    from CSV files, retrieving the database schema, and executing SQL queries.
    """

    def __init__(self, db_name: str) -> None:
        """
        Initialize the SQLiteDatabaseHandler with the specified database name.

        :param db_name: The name of the SQLite database (without .db extension).
        """
        self.db_name = Path(db_name).stem
        self.db_path = Path(f"{self.db_name}.db") if not db_name.endswith('.db') else Path(db_name)

        if not self.db_path.exists():
            logger.info(f"Creating and connecting to a new database at '{self.db_path}'...")
            self.db_path.touch()
        else:
            logger.info(f"Connecting to the existing database at '{self.db_path}'...")

        self._validate_connection()

    def create_tables_from_csv(self, csv_path: Union[str, Path]) -> None:
        """
        Creates tables in the SQLite database from the provided CSV file(s).

        :param csv_path: The path to a CSV file or a directory containing CSV files.
        :raises ValueError: If the provided path is not a .csv file or directory.
        """
        csv_path = Path(csv_path)
        with sqlite3.connect(self.db_path) as conn:
            if csv_path.is_file() and csv_path.suffix == '.csv':
                self._import_csv_to_db(conn, csv_path)
            elif csv_path.is_dir():
                for file in csv_path.glob('*.csv'):
                    self._import_csv_to_db(conn, file)
            else:
                raise ValueError("The provided path must be a .csv file or a directory containing .csv files.")

    def get_db_schema(self) -> Optional[Dict[str, Dict[str, List[Dict[str, Union[str, bool]]]]]]:
        """
        Retrieves the schema of the SQLite database, including columns, constraints, and sample data.

        :return: A dictionary representing the database schema, or None if the database does not exist.
        """
        if not self.db_path.exists():
            logger.warning(f"Database '{self.db_path}' does not exist.")
            return None

        schema = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                tables = self._get_tables(cursor)

                for table_name in tables:
                    schema[table_name] = {
                        'columns': self._get_columns(cursor, table_name),
                        'constraints': self._get_constraints(cursor, table_name),
                        'sample_data': self._get_sample_data(cursor, table_name),
                    }

        except sqlite3.Error as e:
            logger.error(f"An error occurred while retrieving the schema: {e}")
            return None

        return schema

    def execute_query(self, sql: str) -> Optional[str]:
        """
        Executes a SQL query on the SQLite database and returns the result as a JSON string.

        :param sql: The SQL query to execute.
        :return: The query result as a JSON string, or None if an error occurred.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(sql, conn)
                json_result = df.to_json(orient='records')
                logger.info("Query executed successfully.")
                return json_result
        except sqlite3.Error as e:
            logger.error(f"An error occurred while executing the query: {e}")
            return None

    def _validate_connection(self) -> None:
        """
        Validates the connection to the SQLite database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                logger.info(f"Successfully connected to database '{self.db_path}'")
        except sqlite3.Error as e:
            logger.error(f"An error occurred while connecting to the database: {e}")
            raise ConnectionError(f"Failed to connect to database '{self.db_path}': {e}")

    def _import_csv_to_db(self, conn: sqlite3.Connection, csv_file: Path) -> None:
        """
        Imports a CSV file into the SQLite database as a table.

        :param conn: The SQLite database connection.
        :param csv_file: The path to the CSV file.
        """
        table_name = csv_file.stem.lower().replace(" ", "_")

        if self._table_exists(conn, table_name):
            logger.info(f"Table '{table_name}' already exists. Skipping import...")
        else:
            df = pd.read_csv(csv_file)
            df.columns = [col.lower().replace(" ", "_") for col in df.columns]
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            logger.info(f"Table '{table_name}' created from file '{csv_file}'.")

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """
        Checks if a table exists in the SQLite database.

        :param conn: The SQLite database connection.
        :param table_name: The name of the table to check.
        :return: True if the table exists, False otherwise.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        cursor = conn.cursor()
        cursor.execute(query, (table_name,))
        return cursor.fetchone() is not None

    def _get_tables(self, cursor: sqlite3.Cursor) -> List[str]:
        """
        Retrieves the list of tables in the SQLite database.

        :param cursor: The SQLite database cursor.
        :return: A list of table names.
        """
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in cursor.fetchall()]

    def _get_columns(self, cursor: sqlite3.Cursor, table_name: str) -> List[Dict[str, Union[str, bool]]]:
        """
        Retrieves the columns of a table in the SQLite database.

        :param cursor: The SQLite database cursor.
        :param table_name: The name of the table.
        :return: A list of dictionaries representing the columns.
        """
        cursor.execute(f"PRAGMA table_info({table_name});")
        return [
            {'name': column[1], 'type': column[2], 'primary_key': bool(column[5])}
            for column in cursor.fetchall()
        ]

    def _get_constraints(self, cursor: sqlite3.Cursor, table_name: str) -> List[Dict[str, Union[str, List[str], bool]]]:
        """
        Retrieves the constraints of a table in the SQLite database.

        :param cursor: The SQLite database cursor.
        :param table_name: The name of the table.
        :return: A list of dictionaries representing the constraints.
        """
        constraints = []

        # Unique constraints
        cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = cursor.fetchall()
        for index in indexes:
            index_name = index[1]
            cursor.execute(f"PRAGMA index_info({index_name});")
            index_info = cursor.fetchall()
            if index_info:
                constraints.append({
                    'index_name': index_name,
                    'columns': [info[2] for info in index_info],
                    'unique': bool(index[2])
                })

        # Foreign key constraints
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        for fk in foreign_keys:
            constraints.append({
                'type': 'foreign_key',
                'from': fk[3],
                'to': fk[4],
                'table': fk[2]
            })

        return constraints

    def _get_sample_data(self, cursor: sqlite3.Cursor, table_name: str) -> List[tuple]:
        """
        Retrieves sample data from a table in the SQLite database.

        :param cursor: The SQLite database cursor.
        :param table_name: The name of the table.
        :return: A list of tuples representing the sample data (first 5 rows).
        """
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        return cursor.fetchall()
