class BaseDatabase:
    def connect(self):
        raise NotImplementedError

    def download_schema(self):
        raise NotImplementedError

    def fetch_sample_data(self, table_name):
        raise NotImplementedError

    def get_prompt(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError