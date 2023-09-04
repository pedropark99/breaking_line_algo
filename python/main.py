import pandas as pd
from enum import Enum

csv_filepath = "glyph_positions.csv"
glyph_positions = pd.read_csv(csv_filepath, sep = ";")
print(glyph_positions)



class BlockType(Enum):
	GLUE = 1
	BLOCK = 2
	PENALTY = 3


class BlockIndexes:
	block_type = BlockType(1)
	block_width = 0.0
	shrink_factor = 0.0
	stretch_factor = 0.0
	penalty_factor = 0.0
	flag = 0



