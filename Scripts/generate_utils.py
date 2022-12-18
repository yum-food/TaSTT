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
BOARD_COLS=48
NUM_REGIONS = 24
CHARS_PER_CELL=256
BYTES_PER_CHAR=2

NUM_LAYERS=ceil((BOARD_ROWS * BOARD_COLS) / NUM_REGIONS)

# Implementation detail. We use this parameter to return from the terminal
# state of the FX layer to the starting state.
def getDummyParam():
    return "TaSTT_Dummy"

def getHipToggleParam():
    return "TaSTT_Hip_Toggle"

def getHandToggleParam():
    return "TaSTT_Hand_Toggle"

def getToggleParam():
    return "TaSTT_Toggle"

def getScaleParam():
    return "TaSTT_Scale"

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
def getLayerParam(which_layer: int, byte: int) -> str:
    return "TaSTT_L%02dB%01d" % (which_layer, byte)

def getLayerName(which_layer: int, byte: int) -> str:
    return getLayerParam(which_layer, byte)

def getBlendParam(which_layer: int, byte: int) -> str:
    return "TaSTT_L%02dB%01d_Blend" % (which_layer, byte)

def getDefaultStateName(which_layer:int , byte: int):
    return "TaSTT_L%02dB%01d_Do_Nothing" % (which_layer, byte)

def getActiveStateName(which_layer: int, byte: int):
    return "TaSTT_L%02dB%01d_Active" % (which_layer, byte)

def getSelectStateName(which_layer, select):
    return "TaSTT_L%02d_S%02d_B%01d" % (which_layer, select, byte)

def getBlendStateName(which_layer, select, byte):
    return "TaSTT_L%02d_S%02d_B%01d_Blend" % (which_layer, select, byte)

def getLetterStateName(which_layer, select, letter, byte):
    return "TaSTT_L%02d_S%02d_L%03d_B%01d" % (which_layer, select, letter, byte)

def getSelectParam() -> str:
    return "TaSTT_Select"

def getEnableParam():
    return "TaSTT_Enable"

def getIndicator0Param():
    return "TaSTT_Indicator_0"

def getIndicator1Param():
    return "TaSTT_Indicator_1"

def getBoardIndex(which_layer, select):
    # Because we divide the board into a multiple of 8 cells, some cells may
    # describe animations which don't exist, depending on the size of the board.
    # We work around this by simply wrapping those animations back to the top
    # of the board, and rely on the OSC controller to simply not reference
    # those cells.
    return (select * NUM_LAYERS + which_layer) % (BOARD_ROWS * BOARD_COLS)

def getShaderParamByRowColByte(row, col, byte):
    return "_Letter_Row%02d_Col%02d_Byte%01d" % (row, col, byte)

# Mapping from layer to shader param.
def getShaderParam(which_layer, select, byte):
    index = getBoardIndex(which_layer, select)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)

    return getShaderParamByRowCol(row, col, byte)

# The name of the animation which writes `letter` at a specific position in the
# display.
def getLetterAnimationName(row, col, letter, nth_byte):
    return "R%02dC%02dL%02dB%01d" % (row, col, letter, nth_byte)

# The name of the animation which clears the entire board.
def getClearAnimationName():
    return "TaSTT_Clear_Board"

def getAnimationNameByLayerAndIndex(which_layer, select, letter, nth_byte):
    index = getBoardIndex(which_layer, select)

    col = index % BOARD_COLS
    row = floor(index / BOARD_COLS)

    return "R%02dC%02dL%02dB%01d" % (row, col, letter, nth_byte)

# Returns the path to the animation for the given shader parameter + letter.
def getAnimationPath(shader_param, letter):
    return "generated/animations/%s_Letter%02d.anim" % (shader_param, letter)