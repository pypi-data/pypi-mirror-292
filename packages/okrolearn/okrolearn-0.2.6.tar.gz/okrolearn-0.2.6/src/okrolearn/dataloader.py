import json
import sqlite3
from okrolearn.okrolearn import Tensor, np


class DataLoader:
    @staticmethod
    def load_json(file_path):
        """
        Load data from a JSON file and convert it to a Tensor.

        Parameters:
        - file_path: str, path to the JSON file

        Returns:
        - Tensor: A tensor containing the data from the JSON file
        """
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Convert the JSON data to a numpy array
        if isinstance(data, list):
            # If it's a list of lists or list of dictionaries
            if all(isinstance(item, list) for item in data):
                np_data = np.array(data)
            elif all(isinstance(item, dict) for item in data):
                # Extract all keys
                keys = set().union(*data)
                np_data = np.array([[item.get(key, None) for key in keys] for item in data])
        elif isinstance(data, dict):
            # If it's a dictionary of key-value pairs
            np_data = np.array(list(data.values()))
        else:
            raise ValueError("Unsupported JSON structure")

        return Tensor(np_data)

    @staticmethod
    def load_sql(db_path, query):
        """
        Load data from a SQL database and convert it to a Tensor.

        Parameters:
        - db_path: str, path to the SQLite database file
        - query: str, SQL query to execute

        Returns:
        - Tensor: A tensor containing the data from the SQL query
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()

        # Convert the SQL data to a numpy array
        np_data = np.array(data)

        return Tensor(np_data)

    @staticmethod
    def load_csv(file_path, delimiter=',', skip_header=False):
        """
        Load data from a CSV file and convert it to a Tensor.

        Parameters:
        - file_path: str, path to the CSV file
        - delimiter: str, delimiter used in the CSV file (default is ',')
        - skip_header: bool, whether to skip the first row (header) of the CSV file

        Returns:
        - Tensor: A tensor containing the data from the CSV file
        """
        if skip_header:
            np_data = np.genfromtxt(file_path, delimiter=delimiter, skip_header=1)
        else:
            np_data = np.genfromtxt(file_path, delimiter=delimiter)

        return Tensor(np_data)
