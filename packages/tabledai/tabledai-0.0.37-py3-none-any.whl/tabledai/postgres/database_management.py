import hashlib
import logging
import warnings
import os
import re
import pandas as pd
from sqlalchemy import create_engine, exc, text, Column, MetaData, Table as SQLTable
from sqlalchemy.dialects.postgresql import insert
import chardet
from .utils import disable_logging, map_types
import time

class DatabaseManagement:
    def __init__(self, engine):
        self.engine = engine

    def create_tables(self, data_directory: str) -> None:
        """
        Create or update tables from CSV or Excel files in the specified directory.

        Args:
            data_directory (str): The directory containing the data files.
        """
        for file_name in os.listdir(data_directory):
            if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
                table_name = os.path.splitext(file_name)[0].lower().strip().replace(' ', '_')
                file_path = os.path.join(data_directory, file_name)
                # logging.info(f"Creating or updating table '{table_name}' from file '{file_name}'...")
                print(f"Creating or updating table '{table_name}' from file '{file_name}'...")
                try:
                    self._create_or_update_table(table_name, file_path)
                except Exception as e:
                    # logging.error(f"Error creating or updating table '{table_name}'")
                    print(f"Error creating or updating table '{table_name}'")
                    with open('error.log', 'a') as log_file:
                        log_file.write(f"Error creating or updating table '{table_name}':\n\n{str(e)}\n")




    def _create_or_update_table(self, table_name: str, file_path: str) -> None:
        @disable_logging
        def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
            df.columns = [
                re.sub(r'[^a-z0-9_]', '', col.replace('%', '_percent').replace('+', '_plus').replace('-', '_minus').replace('/', '_per_').strip().lower().replace(' ', '_'))
                for col in df.columns
            ]
            return df

        @disable_logging
        def _convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
            def _is_datetime_column(column):
                if column.dtype != object:
                    return False
                date_patterns = [
                    r'\d{2}/\d{2}/\d{2}',
                    r'\d{2}/\d{2}/\d{4}',
                    r'\d{4}/\d{2}/\d{2}',
                    r'\d{2}-\d{2}-\d{4}',
                    r'\d{4}-\d{2}-\d{2}',
                    r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
                    r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',
                    r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}',
                    r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                ]
                for pattern in date_patterns:
                    if column.str.match(pattern).any():
                        try:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", UserWarning)
                                pd.to_datetime(column, errors='raise', dayfirst=True)
                            return True
                        except (ValueError, TypeError):
                            continue
                return False

            datetime_columns = [col for col in df.columns if _is_datetime_column(df[col])]
            
            for column in datetime_columns:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    df[column] = pd.to_datetime(df[column], errors='coerce', infer_datetime_format=True)
            
            return df

        try:
            start_time = time.time()

            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path, encoding=encoding, low_memory=False)
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path, engine='openpyxl')
            else:
                # logging.error(f"Unsupported file format for file '{file_path}'.")
                print(f"Unsupported file format for file '{file_path}'.")
                return

            data = _clean_column_names(data)
            data = _convert_datetime_columns(data)

            metadata = MetaData()
            columns = [Column(column_name, map_types(dtype)) for column_name, dtype in data.dtypes.items()]
            table = SQLTable(table_name, metadata, *columns)
            metadata.create_all(self.engine)

            with self.engine.connect() as connection:
                try:
                    existing_data = pd.read_sql_table(table_name, connection)
                except Exception:
                    existing_data = pd.DataFrame()

            if not existing_data.empty:
                existing_data['_hash'] = existing_data.apply(lambda row: hashlib.md5(pd.util.hash_pandas_object(row, index=True).values).hexdigest(), axis=1)
                data['_hash'] = data.apply(lambda row: hashlib.md5(pd.util.hash_pandas_object(row, index=True).values).hexdigest(), axis=1)

                non_duplicate_data = data[~data['_hash'].isin(existing_data['_hash'])].drop(columns=['_hash'])
            else:
                non_duplicate_data = data

            if not non_duplicate_data.empty:
                # logging.info(f"Inserting {len(non_duplicate_data)} new rows into '{table_name}'...")
                print(f"Inserting {len(non_duplicate_data)} new rows into '{table_name}'...")
                non_duplicate_data.to_sql(table_name, self.engine, if_exists='append', index=False, method='multi', chunksize=1000)
                # logging.info(f"New data has been successfully inserted for table '{table_name}'.")
                print(f"New data has been successfully inserted for table '{table_name}'.")

            end_time = time.time()
            elapsed_time = end_time - start_time
            # logging.info(f"Time taken to process and insert data for table '{table_name}': {elapsed_time:.2f} seconds")
            print(f"Time taken to process and insert data for table '{table_name}': {elapsed_time:.2f} seconds")

        except Exception as e:
            # logging.error(f"Error processing file '{file_path}'...")
            print(f"Error processing file '{file_path}'...")
            raise

    def delete_tables(self, tables: list = [], all: bool = False, confirm: bool = True) -> None:
        """
        Delete the specified tables or all tables if 'all' is set to True.

        Args:
            tables (list): List of table names to delete.
            all (bool): Flag to indicate if all tables should be deleted.
            confirm (bool): Flag to indicate if confirmation is required before deleting.
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        tables = tables if not all else list(metadata.tables.keys())

        def _delete_table(connection, table):
            try:
                table = metadata.tables[table]
                # logging.info(f"Dropping table '{table}'...")
                print(f"Dropping table '{table}'...")
                table.drop(connection)
                # logging.info(f"Table {table} dropped successfully.")
                print(f"Table {table} dropped successfully.")
            except Exception as e:
                # logging.error(f"Error deleting table {table}...")
                print(f"Error deleting table {table}...")

        with self.engine.begin() as connection:
            for table in tables:
                if confirm:
                    response = input(f"Are you sure you want to delete table '{table}'? This action can't be undone. (y/n): ")
                    if response.lower().strip() == 'y':
                        _delete_table(connection, table)
                    else:
                        # logging.info(f"Table '{table}' deletion aborted.")
                        print(f"Table '{table}' deletion aborted.")
                else:
                    _delete_table(connection, table)

    def check_primary_key(self, table_name: str) -> None:
        """
        Check if the specified table has a primary key.

        Args:
            table_name (str): The name of the table to check.
        """
        with self.engine.connect() as con:
            try:
                result = con.execute(text(f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
                """))
                primary_keys = result.fetchall()
                result_dict = {'exists': len(primary_keys) > 0, 'field': primary_keys[0][0] if primary_keys else None}
                # logging.info(f"Primary key check for table '{table_name}': {result_dict}")
                print(f"Primary key check for table '{table_name}': {result_dict}")
            except Exception as e:
                # logging.error(f"Error checking primary key for table '{table_name}'...")
                print(f"Error checking primary key for table '{table_name}'...")
                raise

    def add_primary_key(self, table_name: str, field: str) -> None:
        """
        Add a primary key to the specified table.

        Args:
            table_name (str): The name of the table.
            field (str): The name of the field to set as the primary key.
        """
        with self.engine.connect() as con:
            try:
                result = con.execute(text(f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
                """))
                existing_primary_keys = [row[0] for row in result.fetchall()]

                if len(existing_primary_keys) == 1 and existing_primary_keys[0] == field:
                    return

                fk_constraints = []

                for existing_pk in existing_primary_keys:
                    fk_result = con.execute(text(f"""
                        SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name, tc.constraint_name
                        FROM information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name='{table_name}' AND ccu.column_name='{existing_pk}';
                    """))
                    fk_constraints = fk_result.fetchall()

                    for fk in fk_constraints:
                        fk_constraint_name = fk[4]
                        fk_table_name = fk[0]
                        con.execute(text(f"""
                            ALTER TABLE {fk_table_name} DROP CONSTRAINT {fk_constraint_name};
                        """))
                        # logging.info(f"Dropped foreign key constraint '{fk_constraint_name}' from table '{fk_table_name}'.")
                        print(f"Dropped foreign key constraint '{fk_constraint_name}' from table '{fk_table_name}'.")

                    con.execute(text(f"""
                        ALTER TABLE {table_name} DROP CONSTRAINT {existing_pk};
                    """))
                    # logging.info(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")
                    print(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")

                con.execute(text(f"""
                    ALTER TABLE {table_name}
                    ADD PRIMARY KEY ({field});
                """))
                # logging.info(f"Primary key '{field}' added to table '{table_name}'.")
                print(f"Primary key '{field}' added to table '{table_name}'.")

                for fk in fk_constraints:
                    fk_constraint_name = fk[4]
                    fk_table_name = fk[0]
                    fk_column_name = fk[1]
                    foreign_table_name = fk[2]
                    foreign_column_name = fk[3]
                    con.execute(text(f"""
                        ALTER TABLE {fk_table_name}
                        ADD CONSTRAINT {fk_constraint_name}
                        FOREIGN KEY ({fk_column_name})
                        REFERENCES {foreign_table_name} ({foreign_column_name});
                    """))
                    # logging.info(f"Recreated foreign key constraint '{fk_constraint_name}' on table '{fk_table_name}'.")
                    print(f"Recreated foreign key constraint '{fk_constraint_name}' on table '{fk_table_name}'.")
                con.commit()
            except Exception as e:
                # logging.error(f"Failed to update primary key '{field}' for table '{table_name}'...")
                print(f"Failed to update primary key '{field}' for table '{table_name}'...")
                raise

    def drop_primary_key(self, table_name: str) -> None:
        """
        Drop the primary key from the specified table.

        Args:
            table_name (str): The name of the table.
        """
        with self.engine.connect() as con:
            try:
                result = con.execute(text(f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
                """))
                existing_primary_keys = [row[0] for row in result.fetchall()]

                for existing_pk in existing_primary_keys:
                    con.execute(text(f"""
                        ALTER TABLE {table_name} DROP CONSTRAINT {existing_pk};
                    """))
                    # logging.info(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")
                    print(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")
            except Exception as e:
                # logging.error(f"Failed to drop primary key constraints from table '{table_name}'...")
                print(f"Failed to drop primary key constraints from table '{table_name}'...")
                raise

    def check_foreign_keys(self, table_name: str) -> bool:
        """
        Check if the specified table has foreign keys.

        Args:
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table has foreign keys, False otherwise.
        """
        with self.engine.connect() as con:
            try:
                result = con.execute(text(f"""
                    SELECT tc.constraint_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
                """))
                foreign_keys = result.fetchall()
                result_dict = {'exists': len(foreign_keys) > 0, 'constraints': [fk[0] for fk in foreign_keys]}
                # logging.info(f"Foreign key check for table '{table_name}': {result_dict}")
                print(f"Foreign key check for table '{table_name}': {result_dict}")
                return result_dict['exists']
            except Exception as e:
                # logging.error(f"Error checking foreign keys for table '{table_name}'...")
                print(f"Error checking foreign keys for table '{table_name}'...")
                raise

    def add_foreign_key(self, table_name: str, field: str, reference_table: str, reference_field: str) -> None:
        """
        Add a foreign key to the specified table.

        Args:
            table_name (str): The name of the table.
            field (str): The field to set as the foreign key.
            reference_table (str): The referenced table.
            reference_field (str): The referenced field.
        """
        with self.engine.connect() as con:
            try:
                self.add_primary_key(reference_table, reference_field)

                result = con.execute(text(f"""
                    SELECT tc.constraint_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = '{field}';
                """))
                existing_constraints = result.fetchall()

                for constraint in existing_constraints:
                    constraint_name = constraint[0]
                    con.execute(text(f"""
                        ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name};
                    """))
                    # logging.info(f"Dropped existing foreign key constraint '{constraint_name}' from table '{table_name}'.")
                    print(f"Dropped existing foreign key constraint '{constraint_name}' from table '{table_name}'.")

                con.execute(text(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT fk_{table_name}_{field}
                    FOREIGN KEY ({field})
                    REFERENCES {reference_table} ({reference_field});
                """))
                con.commit()
                # logging.info(f"Foreign key '{field}' added to table '{table_name}' referencing '{reference_table}({reference_field})'.")
                print(f"Foreign key '{field}' added to table '{table_name}' referencing '{reference_table}({reference_field})'.")
            except Exception as e:
                # logging.error(f"Failed to update foreign key '{field}' for table '{table_name}'...")
                print(f"Failed to update foreign key '{field}' for table '{table_name}'...")
                raise

    def drop_foreign_key(self, table_name: str, field: str = None, all: bool = False) -> None:
        """
        Drop the foreign key from the specified table.

        Args:
            table_name (str): The name of the table.
            field (str): The field to drop the foreign key from.
            all (bool): Flag to indicate if all foreign keys should be dropped.
        """
        if not field and not all:
            # logging.error("Please provide a field or set 'all' to True to drop all foreign key constraints.")
            print("Please provide a field or set 'all' to True to drop all foreign key constraints.")
            return
        with self.engine.begin() as connection:
            try:
                if all:
                    result = connection.execute(text(f"""
                        SELECT tc.constraint_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
                    """))
                    foreign_keys = result.fetchall()
                    for fk in foreign_keys:
                        connection.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT {fk[0]}"))
                        # logging.info(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")
                        print(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")
                else:
                    result = connection.execute(text(f"""
                        SELECT tc.constraint_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY' AND kcu.column_name = '{field}';
                    """))
                    foreign_keys = result.fetchall()
                    for fk in foreign_keys:
                        connection.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT {fk[0]}"))
                        # logging.info(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")
                        print(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")
            except Exception as e:
                # logging.error(f"Failed to drop foreign key constraints from table '{table_name}'...")
                print(f"Failed to drop foreign key constraints from table '{table_name}'...")
                raise

    def _query_db(self, sql: str) -> dict:
        """
        Execute the specified SQL query on the database.

        Args:
            sql (str): The SQL query to execute.

        Returns:
            dict: The result of the query execution.
        """
        with self.engine.connect() as con:
            try:
                result = con.execute(text(sql))
                data = result.fetchall()
                columns = result.keys()
                df = pd.DataFrame(data, columns=columns)
                if df.empty:
                    return {'success': False, 'data': df, 'message': "No data returned."}
                else:
                    return {'success': True, 'data': df, 'message': None}
            except Exception as e:
                # logging.error(f"Error querying the database...")
                return {'success': False, 'data': None, 'message': f'{e}'}
