import pandas as pd
from enum import Enum

csv_filepath = "glyph_positions.csv"
glyph_positions = pd.read_csv(csv_filepath, sep = ";")
print(glyph_positions)



class BlockType(Enum):
	GLUE = 1
	BLOCK = 2
	PENALTY = 3


class Block:
    def __init__(self, char, width):
        self.char = char
        self.block_width = width
        self.penalty_factor = 0.0
        self.flag = 0

        if char == " ":
            self.block_type = BlockType(1)
            self.shrink_factor = 0.3
            self.stretch_factor = 0.6
        else:
            self.block_type = BlockType(2)
            self.stretch_factor = 0.0
            self.shrink_factor = 0.0

    def print(self):
        message = "[BLOCK]:\n"
        message += f"- Type: {self.block_type}\n"
        message += f"- Width: {self.block_width}\n"
        message += f"- Char: {self.char}\n"
        print(message)


blocks = list()
for index, row in glyph_positions.iterrows():
    current_char = row["character"]
    width = row["x_advance"]
    blocks.append(Block(current_char, width))


# for block in blocks:
#     block.print()

