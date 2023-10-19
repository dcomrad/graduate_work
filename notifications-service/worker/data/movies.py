import json
from abc import ABC, abstractmethod

FILE_PATH = "data/json/movies.json"

class DataFetcher(ABC):
    @abstractmethod
    def fetch_movie_data(self, movie_id):
        pass


class JsonDataFetcher(DataFetcher):
    def __init__(self):
        self.file_path = FILE_PATH
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {self.file_path}")
            return {}

    def fetch_movie_data(self, movie_id):
        return self.data.get(movie_id)

# class ApiDataFetcher(DataFetcher):
#     def fetch_movie_data(self, movie_id):
#         # Запрос данных через API
#         # Вернуть данные в виде словаря
