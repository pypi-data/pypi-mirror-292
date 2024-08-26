import os
import logging
from typing import Optional
from sqlalchemy import create_engine, exc, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from .database_management import DatabaseManagement
from .llm_integration import LLMIntegration
from .query_handling import QueryHandling
from .utils import create_default_uri_from_env
from urllib.parse import urlparse, urlunparse

load_dotenv(override=True)
# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formatter for logs that includes datetime
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Handler for error logs
error_handler = logging.FileHandler("error_logs.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(log_formatter)

# Add handlers to the logger
logger.addHandler(error_handler)

# Optional: also log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

class PostgresDB(DatabaseManagement, LLMIntegration, QueryHandling):
    """
    A class to manage PostgreSQL database connections and operations,
    including database creation, connection, and deletion.

    Inherits from DatabaseManagement, LLMIntegration, and QueryHandling.
    """

    def __init__(
        self, 
        name: str = 'db', 
        postgres_connection_string: Optional[str] = None,
    ) -> None:
        """
        Initialize the PostgresDB instance.

        Args:
            name (str): The name of the database.
            postgres_connection_string (Optional[str]): The PostgreSQL connection string.

        Raises:
            ValueError: If the PostgreSQL connection string is not provided.
            Exception: For any other exceptions during initialization.
        """
        try:
            self.name = name

            if not postgres_connection_string:
                postgres_connection_string = (
                    os.getenv('POSTGRES_CONNECTION_STRING') or create_default_uri_from_env()
                )

            if not postgres_connection_string:
                raise ValueError("Missing parameters to construct the PostgreSQL connection string.")
            
            self.postgres_connection_string: str = postgres_connection_string
            self.default_engine: Engine = create_engine(self.postgres_connection_string, isolation_level="AUTOCOMMIT")

            self._check_connection(engine=self.default_engine)

            if self._database_exists():
                # logging.info(f"The database '{self.name}' already exists...")
                print(f"The database '{self.name}' already exists...")
            else:
                # logging.info(f"The database '{self.name}' does not exist. Creating database...")
                print(f"The database '{self.name}' does not exist. Creating database...")
                self._create_database()
            
            self._create_db_engine()
            self._check_connection(engine=self.engine)

        except Exception as e:
            # logging.error(f"Error initializing PostgresDB: {e}")
            print(f"Error initializing PostgresDB: {e}")
            raise

    def _check_connection(self, engine: Engine) -> None:
        """
        Check if the connection to the PostgreSQL database is successful.
        
        Raises:
            Exception: If the connection cannot be established.
        """
        try:
            if engine == self.default_engine:
                message = "Successfully connected to the default PostgreSQL database..."
            elif engine == self.engine:
                message = f"Successfully connected to database '{self.name}'..."
            with engine.connect() as connection:
                # logging.info(message)
                print(message)
        except exc.SQLAlchemyError as e:
            # logging.error(f"Error connecting to the PostgreSQL database: {e}")
            print(f"Error connecting to the PostgreSQL database: {e}")
            raise

    def _database_exists(self) -> bool:
        """
        Check if a database with the given name exists.

        Returns:
            bool: True if the database exists, False otherwise.
        """
        query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
        try:
            with self.default_engine.connect() as connection:
                result = connection.execute(query, {'dbname': self.name})
                exists = result.scalar() is not None
                return exists
        except SQLAlchemyError as e:
            # logging.error(f"Error checking if database '{self.name}' exists: {e}")
            print(f"Error checking if database '{self.name}' exists: {e}")
            raise

    def _create_database(self) -> None:
        """
        Create a new database with the given name.

        Raises:
            Exception: If there is an error creating the database.
        """
        create_db_query = text(f"CREATE DATABASE {self.name}")
        try:
            with self.default_engine.connect() as connection:
                connection.execute(create_db_query)
                # logging.info(f"Database '{self.name}' created successfully...")
                print(f"Database '{self.name}' created successfully...")
        except SQLAlchemyError as e:
            # logging.error(f"Error creating database '{self.name}': {e}")
            print(f"Error creating database '{self.name}': {e}")
            raise
    
    def _create_db_engine(self) -> str:
        """
        Create a new SQLAlchemy engine URI for the specified database.

        Args:
            dbname (str): The name of the database.

        Returns:
            str: The SQLAlchemy engine URI for the specified database.
        """
        try:
            parsed_url = urlparse(self.postgres_connection_string)
            new_path = f"/{self.name}"
            new_url = parsed_url._replace(path=new_path)
            self.db_uri = urlunparse(new_url)            
            self.engine = create_engine(self.db_uri, isolation_level="AUTOCOMMIT")
        except SQLAlchemyError as e:
            # logging.error(f"Error creating engine for database '{self.name}': {e}")
            print(f"Error creating engine for database '{self.name}': {e}")
            raise

    def _disconnect_all_users(self, dbname: str) -> None:
        """
        Disconnect all users from the specified database.

        Args:
            dbname (str): The name of the database from which to disconnect users.

        Raises:
            Exception: If there is an error disconnecting the users.
        """
        disconnect_query = text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = :dbname
              AND pid <> pg_backend_pid();
        """)
        try:
            with self.default_engine.connect() as connection:
                connection.execute(disconnect_query, {'dbname': dbname})
        except SQLAlchemyError as e:
            # logging.error(f"Error disconnecting users from database '{dbname}': {e}")
            print(f"Error disconnecting users from database '{dbname}': {e}")
            raise

    def delete_database(self, confirm: bool = True) -> None:
        """
        Delete a database with the given name.

        Args:
            confirm (bool): Whether to ask for confirmation before deleting the database.

        Raises:
            Exception: If there is an error deleting the database.
        """
        delete_db_query = text(f"DROP DATABASE {self.name}")
        try:
            if confirm:
                confirm_input = input(f"Are you sure you want to delete the database '{self.name}'? (y/n): ")
                if confirm_input.lower() != 'y':
                    # logging.info("Database deletion aborted.")
                    print("Database deletion aborted.")
                    return

            self._disconnect_all_users(self.name)
            with self.default_engine.connect() as connection:
                connection.execute(delete_db_query)
                # logging.info(f"Database '{self.name}' deleted successfully...")
                print(f"Database '{self.name}' deleted successfully...")
        except SQLAlchemyError as e:
            # logging.error(f"Error deleting database '{self.name}': {e}")
            print(f"Error deleting database '{self.name}': {e}")
            raise
