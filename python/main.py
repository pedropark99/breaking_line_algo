import pandas as pd
import numpy as np
from enum import Enum
import math


csv_filepath = "glyph_positions.csv"
glyph_positions = pd.read_csv(csv_filepath, sep = ";")
n_rows = len(glyph_positions.index)
if n_rows == 0:
    raise Exception("CSV with glyph positions is empty!")

print(glyph_positions)


DESIRED_LINE_WIDTH = 1200
CURRENT_FONT_SIZE = 35
EM_UNIT = CURRENT_FONT_SIZE
SHRINK_FACTOR = (1 / 3)
STHRETCH_FACTOR = (1 / 2)
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
potential_breaks_indexes = list()
for index in range(n_rows - 1):
    current_width = glyph_widths[index]
    current_char = chars[index]
    next_char = chars[index + 1]

    if current_char == " ":
        paragraph_items.append(glue(current_width))
        continue
    
    elif current_char != " " and next_char == " ":
        paragraph_items.append(block(current_char, current_width))
        paragraph_items.append(penalty(0.0, 0, 0.0))
        potential_breaks_indexes.append(len(paragraph_items) - 1)
        continue

    else:
        paragraph_items.append(block(current_char, current_width))
        continue

# Including the final penalty item in the paragraph which needs to
# be a forced breakpoint
paragraph_items.append(penalty(-1000, 0, 0.0))
potential_breaks_indexes.append(len(paragraph_items) - 1)

print(potential_breaks_indexes)

def calc_total_width_at_range(start_index, end_index):
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



def possible_line_break(break_position_index,
                        line_start_index,
                        penalty_factor,
                        current_line_width):

    return {
        'line_start_index': line_start_index,
        'break_position_index': break_position_index,
        'penalty_factor': penalty_factor,
        'total_width': current_line_width['total_width'],
        'total_stretch': current_line_width['total_stretch'],
        'total_shrink': current_line_width['total_shrink']
    }


def calc_adjustment_ratio(total_width, total_stretch, total_shrink):
    adjustment_ratio = 0.0

    if total_width < DESIRED_LINE_WIDTH:
        if total_stretch > 0:
            adjustment_ratio = (DESIRED_LINE_WIDTH - total_width) / total_stretch
        else:
            adjustment_ratio = 10000
    
    if total_width > DESIRED_LINE_WIDTH:
        if total_shrink > 0:
            adjustment_ratio = (DESIRED_LINE_WIDTH - total_width) / total_shrink
        else:
            adjustment_ratio = -10000
    
    return adjustment_ratio


def calc_badness_factor(adjustment_ratio):
    badness_factor = 1000

    if adjustment_ratio >= -1:
        badness_factor = 100 * abs(adjustment_ratio)
    
    return badness_factor




def calc_optimum_factor(badness_factor, penalty_factor, hyphen_flag):

    if penalty_factor >= 0.0:
        optimum_factor = ((1 + badness_factor + penalty_factor) ** 2) + hyphen_flag

    elif penalty_factor > -1000 and penalty_factor < 0:
        optimum_factor = ((1 + badness_factor) ** 2) - (penalty_factor ** 2) + hyphen_flag

    else:
        optimum_factor = ((1 + badness_factor) ** 2) + hyphen_flag

    return optimum_factor



total_width = np.cumsum([item.width for item in paragraph_items])
total_sthretch = np.cumsum([item.sthretch_factor for item in paragraph_items])
total_shrink = np.cumsum([item.shrink_factor for item in paragraph_items])


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insertAtBegin(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        else:
            new_node.next = self.head
            self.head = new_node

# for i in range(10):
#     active_nodes.insertAtBegin(i + 1)

# current_node = active_nodes.head
# for i in range(10):
#     print(current_node.data)
#     current_node = current_node.next

class BreakpointNode:
    def __init__(self, index):
        self.index = index
    

active_nodes = LinkedList()
active_nodes.insertAtBegin({
    'current_line': 0,
    'line_start_position': 0,
    'line_width': 0.0,
    'line_sthretch': 0.0,
    'line_shrink': 0.0,
    'cumulative_optimum_factor': 0.0
})


active_node = active_nodes.head
while(True):
    line_start_position = active_node.data['line_start_position']
    # The for loop below should start from the beginning of the current line being analyzed
    index = line_start_position
    for index in range(len(total_width)):

        current_item = paragraph_items[index]
        current_width = total_width[index] - active_node.data['line_width']
        current_stretch = total_sthretch[index] - active_node.data['line_sthretch']
        current_shrink = total_shrink[index] - active_node.data['line_shrink']

        if (current_width - current_shrink) > DESIRED_LINE_WIDTH:
            # Line is much longer than the ideal, break
            print("Line is too long, going to check options for next active node")
            break

        if (is_penalty_item(current_item)):
            adjustment_ratio = calc_adjustment_ratio(
                current_width, current_stretch, current_shrink
            )
            badness_factor = calc_badness_factor(adjustment_ratio)
            optimum_factor = calc_optimum_factor(
                badness_factor,
                current_item.penalty_factor,
                current_item.flag
            )



    if active_node.next == None:
        break
    
    active_node = active_node.next


