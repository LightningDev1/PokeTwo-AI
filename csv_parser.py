import os
import csv

from pokemon import Pokemon


class Parser:
    def __init__(self) -> None:
        self.csv_path = os.path.join(os.path.dirname(__file__), "data", "csv", "pokemon.csv")

    def parse_reader(self, reader: csv.DictReader) -> list[Pokemon]:
        columns = next(reader)

        return [
            Pokemon(
                id=int(row[columns.index("id")]),
                slug=row[columns.index("slug")],
            )
            for row in reader
        ]

    def parse(self) -> list[Pokemon]:
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            return self.parse_reader(reader)
