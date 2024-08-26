import hashlib
import logging
import warnings
import os
import re
import pandas as pd
from sqlalchemy import create_engine, exc, text, Column, MetaData, Table as SQLTable, types
from dotenv import load_dotenv
from openai import OpenAI
from decimal import Decimal
import chardet

load_dotenv(override=True)
client = OpenAI()
logging.basicConfig(level=logging.INFO, format='%(message)s')

def disable_logging(func):
    def wrapper(*args, **kwargs):
        logging.disable(logging.CRITICAL)
        try:
            return func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)
    return wrapper

class PostgresDB:
    def __init__(self, name: str = 'db', postgres_username: str = None, postgres_password: str = None, postgres_host: str = None) -> None:
        self.name = name
        self.postgres_username = postgres_username or os.getenv("POSTGRES_DB_USERNAME")
        self.postgres_password = postgres_password or os.getenv("POSTGRES_DB_PASSWORD")
        self.postgres_host = postgres_host or os.getenv("POSTGRES_DB_HOST")
        if not self.postgres_password or not self.postgres_host:
            raise ValueError("Please provide a password and host for the database either by passing them in or providing them in a .env file.")

        self.engine = create_engine(f'postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}/{self.name}')
        self.metadata = MetaData()
        logging.info(f"Connecting to database '{self.name}'...")
        self.connection = self._connect_to_database()

    def _connect_to_database(self):
        try:
            connection = self.engine.connect()
            logging.info("Successfully connected to the database.")
            return connection
        except exc.OperationalError as e:
            if 'FATAL' in str(e):
                if 'password authentication failed' in str(e):
                    logging.error("Password authentication failed. Please check your username and password.")
                    raise ValueError("Password authentication failed. Please check your username and password.")
                elif 'does not exist' in str(e):
                    logging.info(f"Database '{self.name}' does not exist. Creating it...")
                    self._create_database(self.name)
                    self.engine = create_engine(f'postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}/{self.name}')
                    return self._connect_to_database()
            else:
                logging.error(f"Failed to connect to the database: {e}")
                raise

    def _create_database(self, db_name: str) -> None:
        engine = create_engine(f'postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}/postgres')
        conn = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
        try:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            logging.info(f"Database '{db_name}' created successfully.")
        except exc.ProgrammingError as e:
            if 'already exists' in str(e):
                logging.info(f"Database '{db_name}' already exists.")
            else:
                raise
        except exc.OperationalError:
            logging.error("The 'postgres' database does not exist. Please create it or use another default database.")
            raise
        finally:
            conn.close()

    def create_tables(self, data_directory: str) -> None:
        for file_name in os.listdir(data_directory):
            if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
                table_name = os.path.splitext(file_name)[0]
                file_path = os.path.join(data_directory, file_name)
                logging.info(f"Creating or updating table '{table_name}' from file '{file_name}'...")
                self._create_or_update_table(table_name, file_path)

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
                    df[column] = pd.to_datetime(df[column], dayfirst=True).dt.strftime('%Y-%m-%d %H:%M:%S')
            return df

        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        data = pd.read_csv(file_path, encoding=encoding)
        data = _clean_column_names(data)
        data = _convert_datetime_columns(data)

        metadata = MetaData()
        columns = [Column(column_name, self._map_types(dtype)) for column_name, dtype in data.dtypes.items()]
        table = SQLTable(table_name, metadata, *columns)
        table.metadata.create_all(self.engine)

        with self.engine.connect() as connection:
            try:
                existing_data = pd.read_sql_table(table_name, connection)
            except Exception:
                existing_data = pd.DataFrame()

        existing_data['_hash'] = existing_data.apply(lambda row: hashlib.md5(pd.util.hash_pandas_object(row, index=True).values).hexdigest(), axis=1)
        data['_hash'] = data.apply(lambda row: hashlib.md5(pd.util.hash_pandas_object(row, index=True).values).hexdigest(), axis=1)

        non_duplicate_data = data[~data['_hash'].isin(existing_data['_hash'])].drop(columns=['_hash'])

        if not non_duplicate_data.empty:
            with self.engine.connect() as connection:
                try:
                    non_duplicate_data.to_sql(table_name, connection, if_exists='append', index=False)
                    logging.info(f"New data has been successfully inserted for table '{table_name}'.")
                except Exception as e:
                    logging.error(f"Error inserting non-duplicate data for table {table_name}: {e}")

    def delete_tables(self, tables: list = [], all: bool = False, confirm: bool = True) -> None:
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        tables = tables if not all else list(metadata.tables.keys())

        def _delete_table(connection, table):
            try:
                table = metadata.tables[table]
                logging.info(f"Dropping table '{table}'...")
                table.drop(connection)
                logging.info(f"Table {table} dropped successfully.")
            except Exception as e:
                logging.error(f"Error deleting table {table}: {e}")

        with self.engine.begin() as connection:
            for table in tables:
                if confirm:
                    response = input(f"Are you sure you want to delete table '{table}'? This action can't be undone. (y/n): ")
                    if response.lower().strip() == 'y':
                        _delete_table(connection, table)
                    else:
                        logging.info(f"Table '{table}' deletion aborted.")
                else:
                    _delete_table(connection, table)

    def delete(self, confirm: bool = True) -> None:
        engine = create_engine(f'postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}/postgres')
        conn = engine.connect().execution_options(isolation_level="AUTOCOMMIT")

        def _delete_db():
            try:
                conn.execute(text(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{self.name}' AND pid <> pg_backend_pid();
                """))
                conn.execute(text(f"DROP DATABASE {self.name}"))
                logging.info(f"Database '{self.name}' deleted successfully.")
            except exc.ProgrammingError as e:
                if 'does not exist' in str(e):
                    logging.info(f"Database '{self.name}' does not exist.")
                else:
                    raise
            except exc.OperationalError:
                logging.error("The 'postgres' database does not exist. Please create it or use another default database.")
                raise
            finally:
                conn.close()

        if confirm:
            response = input(f"Are you sure you want to delete database '{self.name}'? This action can't be undone. (y/n): ")
            if response.lower().strip() == 'y':
                _delete_db()
            else:
                logging.info(f"Database '{self.name}' deletion aborted.")
        else:
            _delete_db()

    def check_primary_key(self, table_name: str) -> None:
        with self.engine.connect() as con:
            result = con.execute(text(f"""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
            """))
            primary_keys = result.fetchall()
            result_dict = {'exists': len(primary_keys) > 0, 'field': primary_keys[0][0] if primary_keys else None}
            logging.info(f"Primary key check for table '{table_name}': {result_dict}")

    def add_primary_key(self, table_name: str, field: str) -> None:
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
                        logging.info(f"Dropped foreign key constraint '{fk_constraint_name}' from table '{fk_table_name}'.")

                    con.execute(text(f"""
                        ALTER TABLE {table_name} DROP CONSTRAINT {existing_pk};
                    """))
                    logging.info(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")

                con.execute(text(f"""
                    ALTER TABLE {table_name}
                    ADD PRIMARY KEY ({field});
                """))
                logging.info(f"Primary key '{field}' added to table '{table_name}'.")

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
                    logging.info(f"Recreated foreign key constraint '{fk_constraint_name}' on table '{fk_table_name}'.")
                con.commit()
            except Exception as e:
                logging.error(f"Failed to update primary key '{field}' for table '{table_name}': {e}")

    def drop_primary_key(self, table_name: str) -> None:
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
                    logging.info(f"Dropped existing primary key constraint '{existing_pk}' from table '{table_name}'.")
            except Exception as e:
                logging.error(f"Failed to drop primary key constraints from table '{table_name}': {e}")

    def check_foreign_keys(self, table_name: str) -> bool:
        with self.engine.connect() as con:
            result = con.execute(text(f"""
                SELECT tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
            """))
            foreign_keys = result.fetchall()
            result_dict = {'exists': len(foreign_keys) > 0, 'constraints': [fk[0] for fk in foreign_keys]}
            logging.info(f"Foreign key check for table '{table_name}': {result_dict}")
            return result_dict

    def add_foreign_key(self, table_name: str, field: str, reference_table: str, reference_field: str) -> None:
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
                    logging.info(f"Dropped existing foreign key constraint '{constraint_name}' from table '{table_name}'.")

                con.execute(text(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT fk_{table_name}_{field}
                    FOREIGN KEY ({field})
                    REFERENCES {reference_table} ({reference_field});
                """))
                con.commit()
                logging.info(f"Foreign key '{field}' added to table '{table_name}' referencing '{reference_table}({reference_field})'.")
            except Exception as e:
                logging.error(f"Failed to update foreign key '{field}' for table '{table_name}': {e}")

    def drop_foreign_key(self, table_name: str, field: str = None, all: bool = False) -> None:
        if not field and not all:
            logging.error("Please provide a field or set 'all' to True to drop all foreign key constraints.")
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
                        logging.info(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")
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
                        logging.info(f"Dropped foreign key constraint '{fk[0]}' from table '{table_name}'.")

            except Exception as e:
                logging.error(f"Failed to drop foreign key constraints from table '{table_name}': {e}")

    def _build_sql_prompt(self, query: str, starter_prompt: str = '') -> str:
        prompt = starter_prompt
        prompt += f"""You are a Postgres SQL expert who has been tasked with writing a SQL query to extract data from the database based on this query: '{query}'."""
        with self.engine.connect() as con:
            columns_result = con.execute(text("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, column_name;
            """))
            table_columns = columns_result.fetchall()

            primary_keys_result = con.execute(text("""
                SELECT kcu.table_name, tco.constraint_name, kcu.column_name 
                FROM information_schema.table_constraints tco
                JOIN information_schema.key_column_usage kcu 
                    ON kcu.constraint_name = tco.constraint_name
                    AND kcu.constraint_schema = tco.constraint_schema
                    AND kcu.constraint_name = tco.constraint_name
                WHERE tco.constraint_type = 'PRIMARY KEY' AND kcu.table_schema = 'public'
                ORDER BY kcu.table_name, kcu.column_name;
            """))
            primary_keys = primary_keys_result.fetchall()

            foreign_keys_result = con.execute(text("""
                SELECT 
                    kcu.table_name AS foreign_table,
                    rel_kcu.table_name AS primary_table,
                    kcu.column_name AS foreign_column,
                    rel_kcu.column_name AS primary_column
                FROM 
                    information_schema.table_constraints tco
                    JOIN information_schema.key_column_usage kcu
                    ON tco.constraint_schema = kcu.constraint_schema
                    AND tco.constraint_name = kcu.constraint_name
                    JOIN information_schema.referential_constraints rco
                    ON tco.constraint_schema = rco.constraint_schema
                    AND tco.constraint_name = rco.constraint_name
                    JOIN information_schema.key_column_usage rel_kcu
                    ON rco.unique_constraint_schema = rel_kcu.constraint_schema
                    AND rco.unique_constraint_name = rel_kcu.constraint_name
                    AND kcu.ordinal_position = rel_kcu.ordinal_position
                WHERE tco.constraint_type = 'FOREIGN KEY' AND kcu.table_schema = 'public'
                ORDER BY kcu.table_name, kcu.column_name;
            """))
            foreign_keys = foreign_keys_result.fetchall()

            prompt += f"\n\nHere is the information about the database tables:\n\n"
            for table in table_columns:
                prompt += f"Table: {table[0]}, Column: {table[1]}, Data Type: {table[2]}\n"

            prompt += f"\nPrimary Keys:\n"
            for pk in primary_keys:
                prompt += f"Table: {pk[0]}, Column: {pk[2]}, Constraint: {pk[1]}\n"

            prompt += f"\nForeign Keys:\n"
            for fk in foreign_keys:
                prompt += f"Foreign Table: {fk[0]}, Foreign Column: {fk[2]}, Primary Table: {fk[1]}, Primary Column: {fk[3]}\n"

        prompt += f"""
            The query will be run against a Postgres database.

            CONTEXTUAL INSTRUCTIONS:
            - Understand the context of the request to ensure the SQL query correctly identifies and filters for the relevant entities.
            - Maintain context from previous questions and ensure the current query builds on previous results when needed.
            - Be mindful of pronouns and ambiguous terms, ensuring they are mapped to the correct entities and columns.

            SQL INSTRUCTIONS:
            - The query must be written specifically for PostgreSQL.
            - Do not use parameterized queries.
            - Only use the columns from the provided table information.
            - Round computation results to two decimal places.
            - Avoid symbols such as '?', '(', ')', '%', '$', ':' in comparisons.
            - Use 'LIKE' for string comparisons instead of '='.
            - Use wildcard characters with 'LIKE' for partial matches (e.g., '%value%').
            - Write a SQL query adhering to general SQL standards.
            - Ensure the query does not exceed the LLM's context length.
            - Ensure the query is syntactically correct for PostgreSQL.
            - Format date comparisons as 'YYYY-MM-DD HH:MM:SS' and consider PostgreSQL's date functions.
            - Use case-insensitive comparisons (e.g., 'WHERE LOWER(column_name) LIKE ...').
            - Optimize the query to return only the necessary data using clauses like 'DISTINCT', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', 'JOIN', 'UNION'.
            - Avoid casting non-numeric fields to numeric types. Ensure numeric operations like AVG, SUM are only performed on numeric fields.

            RESPONSE INSTRUCTIONS:
            - Return ONLY the following key-value pairs: 'sql': "your sql query here" and 'in_domain': "boolean True or False if you think the query relates data in the database and will be answered with the SQL".
            - Only include the dictionary in the response. Don't include '```python' or '```' in the response.
            - The response should be a python dictionary that returns 'dict' when evaluated: type(eval(response)) == dict
            """
        return prompt

    @disable_logging
    def _sql_openai_call(self, prompt: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful research assistant and a SQL expert for Postgres databases."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        result = response.choices[0].message.content
        result = re.sub(r'```.*?```', '', result, flags=re.DOTALL)
        if isinstance(eval(result), dict) and 'sql' in eval(result) and 'in_domain' in eval(result):
            return eval(result)
        return None

    def _build_generative_prompt(self, query: str, df: pd.DataFrame) -> str:
        prompt = f"""
        Based on the question:\n\n**{query}**\n\n the following data was found:\n\n
        SQL Data in JSON format: {df.to_json()}\n

        Do not make reference to the data sources themselves, only reference the data. For example, don't mention 'the data', 'JSON', 'SQL data', 'databases', etc.\n

        Unless specified in the query, don't show your work for mathematical calculations. Only provide the final answer.\n

        **This is a retrieval-augmented generation task, so it is critical that you only generate the answer based on the data provided in this prompt.**
        **If you need to make any assumptions, please state them clearly.**
        **If you think the data provided is insufficient to generate the answer, please state that as well.**
        """
        return prompt

    @disable_logging
    def _generative_openai_call(self, prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant and a SQL expert for Postgres databases."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return None

    def _query_db(self, sql: str) -> dict:
        with self.engine.connect() as con:
            try:
                result = con.execute(text(sql))
                data = result.fetchall()
                columns = result.keys()
                df = pd.DataFrame(data, columns=columns)
                return {'success': True, 'data': df}
            except Exception as e:
                # logging.error(f"""Error querying the database: {e}""")
                return {'success': False, 'data': str(e)}

    def query(self, query: str, generative: bool = False) -> dict:
        result = {'success': False, 'message': None, 'sql': None, 'data': None, 'generation': None}
        prompt = self._build_sql_prompt(query)
        logging.info(f"Generating SQL for query: '{query}'...")
        sql_llm_result = self._sql_openai_call(prompt)

        if not sql_llm_result:
            logging.error("Failed to generate SQL query, please try again.")
            result['message'] = "Failed to generate SQL query."
            return result

        if not sql_llm_result.get('in_domain'):
            logging.info("The query is not in domain or cannot be answered with the provided data.")
            result['message'] = "The query is not in domain."
            return result

        sql = sql_llm_result.get('sql')
        result['sql'] = sql
        logging.info(f"SQL query generated successfully.")

        db_result_dict = self._query_db(sql)
        if not db_result_dict.get('success'):
            # logging.info("SQL query failed to execute.")
            retry_prompt = (
                f"The user query was {query}. The SQL query generated from OpenAI in the first call was: '{sql}'. "
                f"This SQL failed to execute due to the following error: '{db_result_dict.get('data')}'. "
                "Please try again, taking into account the error message."
            )
            prompt = self._build_sql_prompt(query, starter_prompt=retry_prompt)
            # logging.info(f"Retrying to generate SQL for query: '{query}'...")
            sql_llm_result = self._sql_openai_call(prompt)
            sql = sql_llm_result.get('sql')
            
            if not sql:
                # logging.error("Failed to generate SQL query on retry.")
                result['message'] = "Failed to generate SQL query."
                return result

            result['sql'] = sql
            db_result_dict = self._query_db(sql)

        if not db_result_dict.get('success'):
            logging.error(f"Failed to execute SQL query: {db_result_dict.get('data')}")
            result['message'] = "Failed to execute SQL query."
            return result

        result_df = db_result_dict.get('data')
        if result_df.empty:
            logging.info("Query returned no results.")
            result['message'] = "Query returned no results."
            return result

        logging.info("Query executed successfully.")
        for col in result_df.columns:
            if result_df[col].dtype == object and isinstance(result_df[col].iloc[0], Decimal):
                result_df[col] = result_df[col].astype(float)
                
        result['success'] = True
        result['message'] = "Query executed successfully."
        result['data'] = result_df.to_dict(orient='records')

        if generative:
            generative_prompt = self._build_generative_prompt(query, result_df)
            result['generation'] = self._generative_openai_call(generative_prompt)
        
        return result

    def _map_types(self, dtype: pd.api.types) -> types.TypeEngine:
        if pd.api.types.is_integer_dtype(dtype):
            return types.Integer()
        elif pd.api.types.is_float_dtype(dtype):
            return types.Float()
        elif pd.api.types.is_bool_dtype(dtype):
            return types.Boolean()
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return types.DateTime()
        else:
            return types.String()