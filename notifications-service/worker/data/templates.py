import json
from abc import ABC, abstractmethod

FILE_PATH = "data/json/templates.json"

class DataFetcher(ABC):
    @abstractmethod
    def fetch_template_data(self, template_id):
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

    def fetch_template_data(self, template_id):
        return self.data.get(template_id)

# class ApiDataFetcher(DataFetcher):
#     def fetch_template_data(self, template_id):
#         # Запрос данных через API
#         # Вернуть данные в виде словаря
