import sys
import json

import csv_parser
import generation

parser = csv_parser.Parser()
generator = generation.DatasetGenerator()

pokemon_list = parser.parse()
generator.generate(pokemon_list)
