#!/usr/bin/env python3

import argparse
import generate_utils
import os
import sys

# A single parameter looks like this:
#   _Letter_Row00_Col00_Byte0("_Letter_Row00_Col00_Byte0", float) = 0
def generateUnityParams(nbytes: int, nrows: int, ncols: int, prefix: str = "") -> str:
    lines = []
    lines.append(prefix + "// BEGIN GENERATED CODE BLOCK")
    for byte in range(0, nbytes):
        for row in range(0, nrows):
            for col in range(0, ncols):
                param_name = generate_utils.getShaderParamByRowColByte(row, col, byte)
                line = prefix + """{}("{}", float) = 0""".format(param_name, param_name)
                lines.append(line)
    lines.append(prefix + "// END GENERATED CODE BLOCK")
    return '\n'.join(lines)

# A single parameter looks like this:
#   float _Letter_Row00_Col00_Byte0;
def generateCgParams(nbytes: int, nrows: int, ncols: int, prefix: str = "") -> str:
    lines = []
    lines.append(prefix + "// BEGIN GENERATED CODE BLOCK")
    for byte in range(0, nbytes):
        for row in range(0, nrows):
            for col in range(0, ncols):
                param_name = generate_utils.getShaderParamByRowColByte(row, col, byte)
                line = prefix + """float {};""".format(param_name)
                lines.append(line)
    lines.append(prefix + "// END GENERATED CODE BLOCK")
    return '\n'.join(lines)

# Define 3 constants:
#   uniform int BYTES_PER_CHAR = $nbytes;
#   uniform int NROWS = $nrows;
#   uniform int NCOLS = $ncols;
def generateCgConstants(nbytes: int, board_nrows: int, board_ncols: int,
        texture_nrows: int, texture_ncols: int, prefix: str = "") -> str:
    lines = []
    lines.append(prefix + "// BEGIN GENERATED CODE BLOCK")
    lines.append(prefix + "#define BYTES_PER_CHAR {}".format(nbytes))
    lines.append(prefix + "#define BOARD_NROWS {}".format(board_nrows))
    lines.append(prefix + "#define BOARD_NCOLS {}".format(board_ncols))
    lines.append(prefix + "#define TEXTURE_NROWS {}".format(texture_nrows))
    lines.append(prefix + "#define TEXTURE_NCOLS {}".format(texture_ncols))
    lines.append(prefix + "// END GENERATED CODE BLOCK")
    return '\n'.join(lines)

# This is the basic idea of what we're generating:
#      // Get the value of the parameter for the cell we're in.
#      uint GetLetterParameter(float2 uv)
#      {
#        float CHAR_COL = floor(uv.x * Cols);
#        float CHAR_ROW = floor(uv.y * Rows);
#        uint res = 0;
#
#          [forcecase] switch(CHAR_ROW) {
#            case n:
#            case n-1:
#            ...
#
#              [forcecase] switch (CHAR_COL) {
#              case 0:
#              case 1:
#              ...
#
#                res |= ((uint) _Letter_Row00_Col00_Byte0) << (0 * 8);
#                res |= ((uint) _Letter_Row00_Col00_Byte1) << (1 * 8);
#                continue;
#              }
#        }
#        return res;
#      }
# In English, this provides an accessor to the many (possibly thousands)
# float parameters which hold the text on the board.
def generateLetterAccessor(nbytes: int, nrows: int, ncols: int, prefix: str = "") -> str:
    lines = []
    lines.append(prefix + "// BEGIN GENERATED CODE BLOCK")
    lines.append(prefix + "[forcecase] switch (CHAR_ROW) {")
    for row in range(0, nrows):
        lines.append(prefix + "  case {}:".format(nrows - (row + 1)))
        lines.append(prefix + "    [forcecase] switch (CHAR_COL) {")
        for col in range(0, ncols):
            lines.append(prefix + "      case {}:".format(col))
            for byte in range(0, nbytes):
                param_name = generate_utils.getShaderParamByRowColByte(row, col, byte)
                lines.append(prefix + "        res |= ((uint) {}) << ({} * 8);".format(param_name, byte))
            lines.append(prefix + "        return res;")
        lines.append(prefix + "      default:")
        lines.append(prefix + "        return 0;")
        lines.append(prefix + "    }")
    lines.append(prefix + "}")
    lines.append(prefix + "// END GENERATED CODE BLOCK")
    return '\n'.join(lines)

# Replace any line containing `macro` with `replacement`.
def applyLineMacro(old_path: str, new_path: str, macro: str, replacement: str) -> bool:
    new_lines = []
    times_applied = 0
    with open(old_path, 'r', encoding="utf-8") as f:
        for line in f:
            if line[-1] == '\n':
                line = line[0:len(line)-1]
            if macro in line:
                new_lines.append(replacement)
                times_applied += 1
            else:
                new_lines.append(line)
    with open(new_path, 'w', encoding="utf-8") as f:
        f.write('\n'.join(new_lines))
    return times_applied

if __name__ == "__main__":
    print("args: {}".format(" ".join(sys.argv)))

    parser = argparse.ArgumentParser()
    parser.add_argument("--bytes_per_char", type=str, help="The number of bytes to use to represent each character")
    parser.add_argument("--board_rows", type=str, help="The number of rows on the board")
    parser.add_argument("--board_cols", type=str, help="The number of columns on the board")
    parser.add_argument("--texture_rows", type=str, help="The number of rows on the font textures")
    parser.add_argument("--texture_cols", type=str, help="The number of columns on the font textures")
    parser.add_argument("--shader_template", type=str, help="The path to the shader template")
    parser.add_argument("--shader_path", type=str, help="The path where the generated shader will be written")
    args = parser.parse_args()

    if not args.bytes_per_char or not args.board_rows or not args.board_cols \
            or not args.texture_rows or not args.texture_cols \
            or not args.shader_template or not args.shader_path:
        print(("--bytes_per_char, --board_rows, --board_cols, --texture_rows, "
                "--texture_cols, --shader_template, --shader_path required"), file=sys.stderr)
        sys.exit(1)

    nbytes = int(args.bytes_per_char)
    board_nrows = int(args.board_rows)
    board_ncols = int(args.board_cols)
    texture_nrows = int(args.texture_rows)
    texture_ncols = int(args.texture_cols)

    replacement = generateUnityParams(nbytes, board_nrows, board_ncols, prefix = "")
    #print(replacement)
    macro = "// %TEMPLATE__UNITY_ROW_COL_PARAMS%"
    applyLineMacro(args.shader_template, args.shader_path, macro, replacement)

    replacement = generateCgParams(nbytes, board_nrows, board_ncols, prefix = "  ")
    #print(replacement)
    macro = "// %TEMPLATE__CG_ROW_COL_PARAMS%"
    applyLineMacro(args.shader_path, args.shader_path, macro, replacement)

    replacement = generateCgConstants(nbytes, board_nrows, board_ncols,
            texture_nrows, texture_ncols, prefix = "  ")
    #print(replacement)
    macro = "// %TEMPLATE__CG_ROW_COL_CONSTANTS%"
    applyLineMacro(args.shader_path, args.shader_path, macro, replacement)

    replacement = generateLetterAccessor(nbytes, board_nrows, board_ncols, prefix = "      ")
    #print(replacement)
    macro = "// %TEMPLATE__CG_LETTER_ACCESSOR%"
    applyLineMacro(args.shader_path, args.shader_path, macro, replacement)
