import os
import trino
import logging
import pandas as pd
from .base import BaseDatabase

class TrinoDatabase(BaseDatabase):
    def __init__(self, catalog, schema, user, host, port):
        self.catalog = catalog
        self.schema = schema
        self.user = user
        self.host = host
        self.port = port
        self.conn = None
        

    def connect(self):
        self.conn = trino.dbapi.connect(
            host=self.host,
            port=self.port,
            catalog=self.catalog,
            http_scheme="https" if self.port == "443" else "http",
            auth=trino.auth.OAuth2Authentication(),
            user=self.user
        )

        print(self.conn.user)

    def download_schema(self):

        # Step 1: Get the list of tables
        tables_query = f"""
        SELECT
            table_name
        FROM
            {self.catalog}.information_schema.tables
        WHERE
            table_schema = '{self.schema}'
        """
        tables_df = pd.read_sql(tables_query, self.conn)

        # Prepare a list to hold schema information
        schema_data = []

        # Step 2: For each table, get the columns and their data types
        for table in tables_df['table_name']:
            schema_query = f"""
            SELECT
                column_name,
                data_type
            FROM
                {self.catalog}.information_schema.columns
            WHERE
                table_name = '{table}'
            """
            columns_df = pd.read_sql(schema_query, self.conn)

            # Append the table name with each column's data
            for _, row in columns_df.iterrows():
                schema_data.append({
                    'table_name': table,
                    'column_name': row['column_name'],
                    'data_type': row['data_type']
                })

        # Step 3: Create a DataFrame and save to CSV
        schema_df = pd.DataFrame(schema_data)
        schema_df.to_csv("schema.csv", index=False)
        print("Schema saved to schema.csv.")

        # Fetch sample data for each table
        for table in tables_df['table_name'].unique():
            try:
                sample_data = self.fetch_sample_data(table)
                os.makedirs("data", exist_ok=True)
                sample_data.to_csv(f"data/{table}.csv", index=False)
                print(f"Sample data for table {table} saved.")
            except Exception as e:
                logging.error(f"An error occurred while fetching sample data for table {table}. Error: {e}")

                    

    def fetch_sample_data(self, table_name):
        sample_query = f"SELECT * FROM {self.catalog}.{self.schema}.{table_name} LIMIT 1000"
        return pd.read_sql(sample_query, self.conn)
        
    def get_prompt(self):
        return f"This tables belong to a Trino database. Consider that tables are under the catalog={self.catalog} catalog and the schema={self.schema}."

    def close(self):
        if self.conn:
            self.conn.close()
