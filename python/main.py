import pandas as pd
from enum import Enum


csv_filepath = "glyph_positions.csv"
glyph_positions = pd.read_csv(csv_filepath, sep = ";")
n_rows = len(glyph_positions.index)
if n_rows == 0:
    raise Exception("CSV with glyph positions is empty!")

print(glyph_positions)


CURRENT_FONT_SIZE = 35
EM_UNIT = CURRENT_FONT_SIZE
SHRINK_FACTOR = (1 / 9)
STHRETCH_FACTOR = (1 / 6)
DEFAULT_SPACE_BETWEEN_LINES = 30


class ItemType(Enum):
	GLUE = 1
	BLOCK = 2
	PENALTY = 3


class ParagraphItem:
    def __init__(self, type, char, width,
                 penalty_factor = 0.0, flag = 0,
                 shrink_factor = SHRINK_FACTOR, sthretch_factor = STHRETCH_FACTOR):

        self.char = char
        self.type = type
        self.width = width
        self.penalty_factor = penalty_factor
        self.flag = flag
        self.shrink_factor = shrink_factor 
        self.sthretch_factor = sthretch_factor


    def print(self):
        message = "[BLOCK]:\n"
        message += f"- Type: {self.type}\n"
        message += f"- Width: {self.width}\n"
        message += f"- Char: {self.char}\n"
        print(message)


    def is_glue(self):
        return self.type == ItemType(1)

    def is_block(self):
        return self.type == ItemType(2)

    def is_penalty(self):
        return self.type == ItemType(3)




def glue(width,
         shrink_factor = SHRINK_FACTOR,
         sthretch_factor = STHRETCH_FACTOR):

    return ParagraphItem(
        type = ItemType(1),
        char = " ",
        width = width,
        shrink_factor = width * shrink_factor,
        sthretch_factor = width * sthretch_factor
    )



def block(char, width):

    return ParagraphItem(
        type = ItemType(2),
        char = char,
        width = width,
        shrink_factor = 0,
        sthretch_factor = 0
    )


def penalty(penalty_factor, flag, width = 0.0):

    return ParagraphItem(
        type = ItemType(3),
        char = None,
        width = width,
        shrink_factor = 0.0,
        sthretch_factor = 0.0,
        penalty_factor = penalty_factor,
        flag = flag
    )

def is_penalty_item(item):
    return item.type == ItemType(3)

def is_block_item(item):
    return item.type == ItemType(2)

def is_glue_item(item):
    return item.type == ItemType(1)

symbols = set([
    '.', '!', '$', ',',
    '&', '#', '@', '(',
    ')', ';', ';', '>',
    '<', '|', '\\', '/',
    '?', '{', '}', '[',
    ']', '+', '=', '*'
])


chars = glyph_positions["character"]
glyph_widths = glyph_positions["x_advance"]
paragraph_items = list()
for index in range(n_rows - 1):
    current_width = glyph_widths[index]
    current_char = chars[index]
    next_char = chars[index + 1]

    if current_char == " ":
        paragraph_items.append(glue(current_width))
        continue
    
    elif current_char != " " and next_char == " ":
        paragraph_items.append(penalty(0.0, 0, 0.0))
        continue

    else:
        paragraph_items.append(block(current_char, current_width))
        continue

# Including the final penalty item in the paragraph which needs to
# be a forced breakpoint
paragraph_items.append(penalty(-1000, 0, 0.0))



def get_total_width_at_range(start_index, end_index):
    items = paragraph_items[start_index:end_index]
    widths, stretchs, shrinks = list(), list(), list()
    for item in items:
        widths.append(item.width)
        stretchs.append(item.sthretch_factor)
        shrinks.append(item.shrink_factor)

    return {
        'total_width': sum(widths),
        'total_stretch': sum(stretchs),
        'total_shrink': sum(shrinks),
    }


start_index_of_current_line = 0
for index in range(len(paragraph_items)):
    current_item = paragraph_items[index]
    if is_penalty_item(current_item):
        current_line_width = get_total_width_at_range(
            start_index_of_current_line,
            index
        )



[item.print() for item in paragraph_items]
