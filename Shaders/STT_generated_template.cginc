#ifndef __STT_GENERATED_INC__
#define __STT_GENERATED_INC__

// %TEMPLATE__CG_ROW_COL_CONSTANTS%

// %TEMPLATE__CG_ROW_COL_PARAMS%

// Get the value of the parameter for the cell we're in.
uint GetLetterParameter(float2 uv)
{
  float CHAR_COL = floor(uv.x * BOARD_NCOLS);
  float CHAR_ROW = floor(uv.y * BOARD_NROWS);
  int res = 0;

  // %TEMPLATE__CG_LETTER_ACCESSOR%
  return res;
}

#endif  // __STT_GENERATED_INC__
