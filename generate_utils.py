from math import ceil
from math import floor

def replaceMacros(lines, macro_defs):
    for k,v in macro_defs.items():
        lines = lines.replace("%" + k + "%", v)
    return lines

# Note, (BOARD_ROWS * BOARD_COLS % NUM_LAYERS) must equal 0. If not, writing to
# the last cell will (with the current implementation) wrap around to the front
# of the board.
BOARD_ROWS=4
BOARD_COLS=44
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

def getHipToggleParam():
    return "TaSTT_Hip_Toggle"

def getHandToggleParam():
    return "TaSTT_Hand_Toggle"

def getToggleParam():
    return "TaSTT_Toggle"

# When this is set to true, the board will emit a soft beep sound. It's used to
# grab attention when speaking.
def getSpeechNoiseToggleParam():
    return "TaSTT_Speech_Noise_Toggle"

# This is used to disable speaking noises.
def getSpeechNoiseEnableParam():
    return "TaSTT_Speech_Noise_Enable"

# When this is set to true, the board clears.
def getClearBoardParam():
    return "TaSTT_Clear_Board"

def getLockWorldParam():
    return "TaSTT_Lock_World"

# Each layer controls a group of cells. There's only one letter per layer, thus
# this is also the name of the parameter which sets the letter for a layer.
def getLayerParam(which_layer: int) -> str:
    return "TaSTT_L%02d" % which_layer

def getLayerName(which_layer: int) -> str:
    return getLayerParam(which_layer)

def getDefaultStateName(which_layer):
    return "TaSTT_L%02d_Do_Nothing" % which_layer

def getActiveStateName(which_layer):
    return "TaSTT_L%02d_Active" % which_layer

def getS0StateName(which_layer, s0):
    return "TaSTT_L%02d_S%02d" % (which_layer, s0)

def getS1StateName(which_layer, s0, s1):
    return "TaSTT_L%02d_S%02d_S%02d" % (which_layer, s0, s1)

def getS2StateName(which_layer, s0, s1, s2):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d" % (which_layer, s0, s1, s2)

def getS3StateName(which_layer, s0, s1, s2, s3):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d_S%02d" % (which_layer, s0, s1, s2, s3)

def getLetterStateName(which_layer, s0, s1, s2, s3, letter):
    return "TaSTT_L%02d_S%02d_S%02d_S%02d_S%02d_L%03d" % (which_layer, s0, s1, s2, s3, letter)

def getSelectParam(which_layer: int, which_select: int) -> str:
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

def getShaderParamByRowCol(row, col):
    return "_Letter_Row%02d_Col%02d" % (row, col)

# Mapping from layer to shader param.
def getShaderParam(which_layer, s0, s1, s2, s3):
    index = getBoardIndex(which_layer, s0, s1, s2, s3)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)

    return getShaderParamByRowCol(row, col)

# The name of the animation which writes `letter` at a specific position in the
# display.
def getLetterAnimationName(row, col, letter):
    return "R%02dC%02dL%02d" % (row, col, letter)

# The name of the animation which clears the entire board.
def getClearAnimationName():
    return "TaSTT_Clear_Board"

def getAnimationNameByLayerAndIndex(which_layer, s0, s1, s2, s3, letter):
    index = getBoardIndex(which_layer, s0, s1, s2, s3)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)

    return "R%02dC%02dL%02d" % (row, col, letter)

# Returns the path to the animation for the given shader parameter + letter.
def getAnimationPath(shader_param, letter):
    return "generated/animations/%s_Letter%02d.anim" % (shader_param, letter)
