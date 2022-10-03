from math import ceil
from math import floor

def replaceMacros(lines, macro_defs):
    for k,v in macro_defs.items():
        lines = lines.replace("%" + k + "%", v)
    return lines

# Note, (BOARD_ROWS * BOARD_COLS % NUM_LAYERS) must equal 0. If not, writing to
# the last cell will (with the current implementation) wrap around to the front
# of the board.
BOARD_ROWS=8
BOARD_COLS=22
INDEX_BITS=4
CHARS_PER_CELL=80

NUM_LAYERS=ceil((BOARD_ROWS * BOARD_COLS) / (2**INDEX_BITS))

# The bits per layer are:
#   8 bits: letter selection (256 possible letters per slot)
#   3 bits: slot selection (each layer controls 8 slots)
#   1 bit: enable bit (turns layer off while we index to a new slot)
NUM_PARAM_BITS=(NUM_LAYERS * (8 + INDEX_BITS + 1))

# Implementation detail. We use this parameter to return from the terminal
# state of the FX layer to the starting state.
def getDummyParam():
    return "TaSTT_Dummy"

def getResizeEnableParam():
    return "TaSTT_Resize_Enable"

def getResize0Param():
    return "TaSTT_Resize_0"

def getResize1Param():
    return "TaSTT_Resize_1"

# Each layer controls a group of cells. There's only one letter per layer, thus
# this is also the name of the parameter which sets the letter for a layer.
def getLayerParam(which_layer):
    return "TaSTT_L%02d" % which_layer

def getSelectParam(which_layer, which_select):
    return "TaSTT_L%02d_S%02d" % (which_layer, which_select)

def getEnableParam():
    return "TaSTT_Enable"

def getBoardIndex(which_layer, s0, s1, s2, s3):
    # Because we divide the board into a multiple of 8 cells, some cells may
    # describe animations which don't exist, depending on the size of the board.
    # We work around this by simply wrapping those animations back to the top
    # of the board, and rely on the OSC controller to simply not reference
    # those cells.
    return ((s0 * 8 + s1 * 4 + s2 * 2 + s3) * NUM_LAYERS + which_layer) % (BOARD_ROWS * BOARD_COLS)

# Mapping from layer to shader param.
def getShaderParam(which_layer, s0, s1, s2, s3):
    index = getBoardIndex(which_layer, s0, s1, s2, s3)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)
    return "_Letter_Row%02d_Col%02d" % (row, col)

# Returns the path to the animation for the given shader parameter + letter.
def getAnimationPath(shader_param, letter):
    return "generated/animations/%s_Letter%02d.anim" % (shader_param, letter)
