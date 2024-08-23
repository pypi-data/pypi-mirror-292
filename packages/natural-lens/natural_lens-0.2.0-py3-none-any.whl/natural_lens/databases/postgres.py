import os
import pandas as pd
from sqlalchemy import create_engine
from .base import BaseDatabase

class PostgreSQLDatabase(BaseDatabase):
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.engine = None

    def connect(self):
        # Create a SQLAlchemy engine
        self.engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}')

    def download_schema(self):
        schema_query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM
            information_schema.columns
        WHERE
            table_schema = 'public';
        """
        schema_df = pd.read_sql(schema_query, self.engine)
        schema_df.to_csv("schema.csv", index=False)
        print("Schema saved to schema.csv.")
        # Fetch sample data for each table
        for table in schema_df['table_name'].unique():
            sample_data = self.fetch_sample_data(table)
            os.makedirs("data", exist_ok=True)
            sample_data.to_csv(f"data/{table}.csv", index=False)
            print(f"Sample data for table {table} saved.")

    def fetch_sample_data(self, table_name):
        sample_query = f"SELECT * FROM {table_name} LIMIT 1000;"
        return pd.read_sql(sample_query, self.engine)

    def get_prompt(self):
        return f"This tables belongs to a Postgres database."

    def close(self):
        if self.engine:
            self.engine.dispose()  # Dispose of the SQLAlchemy engine