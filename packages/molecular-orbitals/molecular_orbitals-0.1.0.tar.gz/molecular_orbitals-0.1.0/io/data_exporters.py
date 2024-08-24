# molecular_orbitals/io/data_exporters.py

import json

class JSONExporter:
    def __init__(self, data):
        """
        Initializes the JSONExporter with data to export.

        :param data: The data to be exported, typically a list or dictionary.
        """
        self.data = data

    def export(self, filepath: str):
        """
        Exports the data to a JSON file.

        :param filepath: The path to the file where the data will be saved.
        """
        with open(filepath, 'w') as file:
            json.dump(self.data, file, indent=4)


class CSVExporter:
    def __init__(self, data):
        """
        Initializes the CSVExporter with data to export.

        :param data: The data to be exported, typically a list or dictionary.
        """
        self.data = data

    def export(self, filepath: str):
        """
        Exports the data to a CSV file.

        :param filepath: The path to the file where the data will be saved.
        """
        import csv
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            if isinstance(self.data, list):
                for row in self.data:
                    writer.writerow(row)
            else:
                writer.writerow(self.data.keys())
                writer.writerow(self.data.values())
