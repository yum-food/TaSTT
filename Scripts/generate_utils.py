from math import ceil
from math import floor

def replaceMacros(lines, macro_defs):
    for k,v in macro_defs.items():
        lines = lines.replace("%" + k + "%", v)
    return lines

class Config():
    def __init__(self):
        self.BOARD_ROWS=4
        self.BOARD_COLS=48
        self.CHARS_PER_CELL=256
        self.BYTES_PER_CHAR=2
        self.CHARS_PER_SYNC=10

    def numRegions(self, which_layer):
        num_cells = self.BOARD_ROWS * self.BOARD_COLS
        layers_in_last_region = num_cells % self.CHARS_PER_SYNC
        float_result = num_cells / self.CHARS_PER_SYNC
        if which_layer >= layers_in_last_region:
            return floor(float_result)
        else:
            return ceil(float_result)

config = Config()

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

def getEnablePhonemeParam():
    return "TaSTT_Enable_Phoneme"

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

def getSoundParam(i: int):
    return f"TaSTT_Sound{str(i)}"

def getEllipsisParam():
    return "TaSTT_Ellipsis"

def getBoardIndex(which_layer, select):
    # Because we divide the board into a multiple of 8 cells, some cells may
    # describe animations which don't exist, depending on the size of the board.
    # We work around this by simply wrapping those animations back to the top
    # of the board, and rely on the OSC controller to simply not reference
    # those cells.
    return (select * config.CHARS_PER_SYNC + which_layer) % (config.BOARD_ROWS * config.BOARD_COLS)

def getShaderParamByRowColByte(row, col, byte):
    return "_Letter_Row%02d_Col%02d_Byte%01d" % (row, col, byte)

# Mapping from layer to shader param.
def getShaderParam(which_layer, select, byte):
    index = getBoardIndex(which_layer, select)

    col = index % config.BOARD_COLS
    row = floor(index / config.BOARD_COLS)

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

    col = index % config.BOARD_COLS
    row = floor(index / config.BOARD_COLS)

    return "R%02dC%02dL%02dB%01d" % (row, col, letter, nth_byte)

# Returns the path to the animation for the given shader parameter + letter.
def getAnimationPath(shader_param, letter):
    return "generated/animations/%s_Letter%02d.anim" % (shader_param, letter)
