from math import ceil
from math import floor

def replaceMacros(lines, macro_defs):
    for k,v in macro_defs.items():
        lines = lines.replace("%" + k + "%", v)
    return lines

BOARD_ROWS=6
BOARD_COLS=14
INDEX_BITS=3
CHARS_PER_CELL=80

NUM_LAYERS=ceil((BOARD_ROWS * BOARD_COLS) / (2**INDEX_BITS))

# The bits per layer are:
#   8 bits: letter selection (256 possible letters per slot)
#   3 bits: slot selection (each layer controls 8 slots)
#   1 bit: enable bit (turns layer off while we index to a new slot)
NUM_PARAM_BITS=(NUM_LAYERS * (8 + INDEX_BITS + 1))

def getDummyParam():
    return "TaSTT_Dummy"

# Each layer controls a group of cells. There's only one letter per layer, thus
# this is also the name of the parameter which sets the letter for a layer.
def getLayerParam(which_layer):
    return "TaSTT_L%02d" % which_layer

def getSelectParam(which_layer, which_select):
    return "TaSTT_L%02d_S%02d" % (which_layer, which_select)

def getEnableParam(which_layer):
    return "TaSTT_L%02d_E" % which_layer

def getBoardIndex(which_layer, s0, s1, s2):
    # TODO(yum_food) because we divide the board into a multiple of 8 cells,
    # some cells describe animations which don't exist. We work around this by
    # simply wrapping those animations back to the top of the board, and rely
    # on the OSC controller to simply not reference those cells. Clean this up.
    return ((s0 * 4 + s1 * 2 + s2) * NUM_LAYERS + which_layer) % (BOARD_ROWS * BOARD_COLS)

# Mapping from layer to shader param.
def getShaderParam(which_layer, s0, s1, s2):
    index = getBoardIndex(which_layer, s0, s1, s2)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)
    return "_Letter_Row%02d_Col%02d" % (row, col)

# Returns the path to the animation for the given shader parameter + letter.
def getAnimationPath(shader_param, letter):
    return "generated/animations/%s_Letter%02d.anim" % (shader_param, letter)
