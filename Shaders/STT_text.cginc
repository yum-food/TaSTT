#ifndef __STT_TEXT_INC__
#define __STT_TEXT_INC__

#include "stt_generated.cginc"

float Enable_Dithering;

SamplerState linear_clamp_sampler;

Texture2D _Font_0x0000_0x1FFF;
float4 _Font_0x0000_0x1FFF_TexelSize;
Texture2D _Font_0x2000_0x3FFF;
float4 _Font_0x2000_0x3FFF_TexelSize;
Texture2D _Font_0x4000_0x5FFF;
float4 _Font_0x4000_0x5FFF_TexelSize;
Texture2D _Font_0x6000_0x7FFF;
float4 _Font_0x6000_0x7FFF_TexelSize;
Texture2D _Font_0x8000_0x9FFF;
float4 _Font_0x8000_0x9FFF_TexelSize;
Texture2D _Font_0xA000_0xBFFF;
float4 _Font_0xA000_0xBFFF_TexelSize;
Texture2D _Font_0xC000_0xDFFF;
float4 _Font_0xC000_0xDFFF_TexelSize;
Texture2D _Img_0xE000_0xE03F;
float4 _Img_0xE000_0xE03F_TexelSize;

float2 AddMarginToUV(float2 uv, float2 margin)
{
  float2 lo = float2(-margin.x / 2, -margin.y / 2);
  float2 hi = float2(1.0 + margin.x / 2, 1.0 + margin.y / 2);

  return clamp(lerp(lo, hi, uv), 0.0, 1.0);
}

// Generate a random number on [0, 1].
float prng(float2 p)
{
  return frac(sin(dot(p, float2(561.0, 885.0))) * 776.2) / 2.0;
}

bool f3ltf3(float3 a, float3 b)
{
  return (a[0] < b[0]) *
    (a[1] < b[1]) *
    (a[2] < b[2]);
}

// Write the nth letter in the current cell and return the value of the
// pixel.
// `texture_rows` and `texture_cols` indicate how many rows and columns are
// in the texture being sampled.
float2 GetLetterUV(float2 uv, int nth_letter,
    float texture_cols, float texture_rows,
    float board_cols, float board_rows,
    float margin)
{
  // UV spans from [0,1] to [0,1].
  // 'U' is horizontal; cols.
  // 'V' is vertical; rows.
  //
  // I want to divide the mesh into an m x n grid.
  // I want to know what grid cell I'm in. This is simply u * m, v * n.

  // OK, I know what cell I'm in. Now I need to know how far across it I
  // am. Produce a float in the range [0, 1).
  float CHAR_FRAC_COL = uv.x * board_cols - floor(uv.x * board_cols);
  float CHAR_FRAC_ROW = uv.y * board_rows - floor(uv.y * board_rows);

  // Avoid rendering pixels right on the edge of the slot. If we were to
  // do this, then that value would get stretched due to clamping
  // (AddMarginToUV), resulting in long lines on the edge of the display.
  float lo = margin / 2;
  float hi = 1.0 - margin / 2;
  bool skip_result = (margin != 0) *
      !(CHAR_FRAC_ROW > lo *
        CHAR_FRAC_COL > lo *
        CHAR_FRAC_ROW < hi *
        CHAR_FRAC_COL < hi);

  float LETTER_COL = fmod(nth_letter, floor(texture_cols));
  float LETTER_ROW = floor(texture_rows) - floor(nth_letter / floor(texture_cols));

  float LETTER_UV_ROW = (LETTER_ROW + CHAR_FRAC_ROW - 1.00) / texture_rows;
  float LETTER_UV_COL = (LETTER_COL + CHAR_FRAC_COL) / texture_cols;

  float2 result;
  result.x = LETTER_UV_COL;
  result.y = LETTER_UV_ROW;

  return lerp(result, -1, skip_result);;
}

float4 GetLetter(float2 uv) {
  uint letter = GetLetterParameter(uv);

  float texture_cols;
  float texture_rows;
  float2 letter_uv;
  bool is_emote = false;

  if (letter < 0xE000) {
    letter_uv = GetLetterUV(uv, letter % 0x2000, TEXTURE_NCOLS, TEXTURE_NROWS, BOARD_NCOLS, BOARD_NROWS, /*margin=*/0);
  } else {
    is_emote = true;
    texture_cols = 16.0;
    texture_rows = 8.0;
    // This will need to be updated if we create multiple emote textures.
    letter_uv = GetLetterUV(uv, letter % 0x2000, texture_cols, texture_rows, BOARD_NCOLS, BOARD_NROWS, /*margin=*/0);
  }

  bool discard_text = (letter_uv.x == -1) * (letter_uv.y == -1);

  const float iddx = ddx(uv.x);
  const float iddy = ddy(uv.y);

  float4 text = float4(0, 0, 0, 0);
  int which_texture = (int) floor(letter / (uint) (64 * 128));
  [forcecase] switch (which_texture)
  {
    case 0:
      text = _Font_0x0000_0x1FFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 1:
      text = _Font_0x2000_0x3FFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 2:
      text = _Font_0x4000_0x5FFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 3:
      text = _Font_0x6000_0x7FFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 4:
      text = _Font_0x8000_0x9FFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 5:
      text = _Font_0xA000_0xBFFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 6:
      text = _Font_0xC000_0xDFFF.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    case 7:
      text = _Img_0xE000_0xE03F.SampleGrad(linear_clamp_sampler,
          letter_uv, iddx, iddy);
      break;
    default:
      // Return some distinctive pattern that will look like a bug.
      return float4(1, 0, _SinTime[0], 1);
  }

  // The edges of each letter cell can be slightly grey due to mip maps.
  // Detect this and shade it as the background.
  float3 grey = 0.7;
  bool disc = !(!f3ltf3(text.rgb, grey) * !discard_text * !is_emote);
  return lerp(float4(text.rgb, 1), 0, disc);
}

#endif //  __STT_TEXT_INC__

