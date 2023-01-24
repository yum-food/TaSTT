Shader "Unlit/TaSTT"
{
  Properties
  {
    Text_Color ("Text Color", Color) = (1, 1, 1, 1)
    Background_Color ("Background Color", Color) = (0, 0, 0, 1)
    Margin_Color ("Margin color", Color) = (1, 1, 1, 1)

    [MaterialToggle] Render_Margin("Render margin", float) = 1
    [MaterialToggle] Render_Visual_Indicator("Render visual speech indicator", float) = 1
    Margin_Scale("Margin scale", float) = 0.03
    Margin_Rounding_Scale("Margin rounding scale", float) = 0.03
    [MaterialToggle] Enable_Margin_Effect_Squares(
        "Enable margin effect: Squares", float) = 0

    [MaterialToggle] Use_Custom_Background("Enable custom background", float) = 0
    Custom_Background("Custom background", 2D) = "black" {}

    _Font_0x0000_0x1FFF ("_Font 0 (unicode 0x0000 - 0x1FFFF)", 2D) = "white" {}
    _Font_0x2000_0x3FFF ("_Font 1 (unicode 0x2000 - 0x3FFFF)", 2D) = "white" {}
    _Font_0x4000_0x5FFF ("_Font 2 (unicode 0x4000 - 0x5FFFF)", 2D) = "white" {}
    _Font_0x6000_0x7FFF ("_Font 3 (unicode 0x6000 - 0x7FFFF)", 2D) = "white" {}
    _Font_0x8000_0x9FFF ("_Font 4 (unicode 0x8000 - 0x9FFFF)", 2D) = "white" {}
    _Font_0xA000_0xBFFF ("_Font 5 (unicode 0xA000 - 0xBFFFF)", 2D) = "white" {}
    _Font_0xC000_0xDFFF ("_Font 6 (unicode 0xC000 - 0xDFFFF)", 2D) = "white" {}
    _Img_0xE000_0xE03F  ("_Images 0", 2D) = "white" {}
    _TaSTT_Indicator_0("_TaSTT_Indicator_0", float) = 0
    _TaSTT_Indicator_1("_TaSTT_Indicator_1", float) = 0

    // %TEMPLATE__UNITY_ROW_COL_PARAMS%
  }
  SubShader
  {
    Tags { "RenderType"="Opaque" "Queue"="AlphaTest"}
    LOD 100

    Pass
    {
      Blend SrcAlpha OneMinusSrcAlpha

      CGPROGRAM
      #pragma vertex vert
      #pragma fragment frag
      #pragma multi_compile

      //#include "UnityCG.cginc"

      struct appdata
      {
        float4 vertex : POSITION;
        float2 uv : TEXCOORD0;
        float3 normal : NORMAL;
      };

      struct v2f
      {
        float2 uv : TEXCOORD0;
        float4 vertex : SV_POSITION;
      };

      SamplerState sampler_linear_repeat;

      Texture2D _Font_0x0000_0x1FFF;
      Texture2D _Font_0x2000_0x3FFF;
      Texture2D _Font_0x4000_0x5FFF;
      Texture2D _Font_0x6000_0x7FFF;
      Texture2D _Font_0x8000_0x9FFF;
      Texture2D _Font_0xA000_0xBFFF;
      Texture2D _Font_0xC000_0xDFFF;
      Texture2D _Img_0xE000_0xE03F;

      fixed4 Text_Color;
      fixed4 Background_Color;
      fixed4 Margin_Color;

      float Render_Margin;
      float Render_Visual_Indicator;
      float Margin_Scale;
      float Margin_Rounding_Scale;
      float Enable_Margin_Effect_Squares;

      // %TEMPLATE__CG_ROW_COL_CONSTANTS%

      float3 HUEtoRGB(in float H)
      {
        float R = abs(H * 6 - 3) - 1;
        float G = 2 - abs(H * 6 - 2);
        float B = 2 - abs(H * 6 - 4);
        return saturate(float3(R, G, B));
      }

      float3 HSVtoRGB(in float3 HSV)
      {
        float3 RGB = HUEtoRGB(HSV.x);
        return ((RGB - 1) * HSV.y + 1) * HSV.z;
      }

      float _TaSTT_Indicator_0;
      float _TaSTT_Indicator_1;
      static const float3 TaSTT_Indicator_Color_0 = HSVtoRGB(float3(0.00, 0.7, 1.0));
      static const float3 TaSTT_Indicator_Color_1 = HSVtoRGB(float3(0.07, 0.7, 1.0));
      static const float3 TaSTT_Indicator_Color_2 = HSVtoRGB(float3(0.30, 0.7, 1.0));

      fixed4 float3tofixed4(in float3 f3, in float alpha)
      {
        return fixed4(
          f3.r,
          f3.g,
          f3.b,
          alpha);
      }

      float Use_Custom_Background;
      Texture2D Custom_Background;

      // %TEMPLATE__CG_ROW_COL_PARAMS%

      v2f vert (appdata v)
      {
        v2f o;
        o.vertex = UnityObjectToClipPos(v.vertex);
        o.uv = 1.0 - v.uv;
        return o;
      }

      float2 AddMarginToUV(float2 uv, float2 margin)
      {
        float2 lo = float2(-margin.x / 2, -margin.y / 2);
        float2 hi = float2(1.0 + margin.x / 2, 1.0 + margin.y / 2);

        return clamp(lerp(lo, hi, uv), 0.0, 1.0);
      }

      // dist = sqrt(dx^2 + dy^2) = sqrt(<dx,dy> * <dx,dy>)
      bool InRadius2(float2 uv, float2 pos, float radius2)
      {
        float2 delta = uv - pos;
        return dot(delta, delta) < radius2;
      }

      bool InMargin(float2 uv, float2 margin)
      {
        if (uv.x < margin.x ||
            uv.x > 1 - margin.x ||
            uv.y < margin.y ||
            uv.y > 1 - margin.y) {
            return true;
        }

        return false;
      }

      bool InSpeechIndicator(float2 uv, float2 margin)
      {
        if (!Render_Visual_Indicator) {
          return false;
        }

        // Margin is uv_margin/2 wide/tall.
        // We want a circle whose radius is ~80% of that.
        float radius_factor = 0.95;
        float radius = margin.x * radius_factor;
        // We want this circle to be centered halfway through the margin
        // vertically, and at 1.5x the margin width horizontally.
        float2 indicator_center = float2(margin.x + radius, margin.y * 0.5);
        // Finally, translate it to the top of the board instead of the
        // bottom.
        indicator_center.y = 1.0 - indicator_center.y;

        if (InRadius2(uv, indicator_center, radius * radius)) {
          return true;
        }

        return false;
      }

      bool InMarginRounding(float2 uv, float2 margin, float rounding, bool interior)
      {
        if (!interior) {
          rounding += margin.x;
          margin = float2(0, 0);
        }

        // This is the center of a circle whose perimeter touches the
        // upper left corner of the margin.
        float2 c0 = float2(rounding + margin.x, rounding + margin.y);
        if (uv.x < c0.x && uv.y < c0.y && uv.x > margin.x && uv.y > margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(rounding + margin.x, 1 - (rounding + margin.y));
        if (uv.x < c0.x && uv.y > c0.y && uv.x > margin.x && uv.y < 1 - margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(1 - (rounding + margin.x), 1 - (rounding + margin.y));
        if (uv.x > c0.x && uv.y > c0.y && uv.x < 1 - margin.x && uv.y < 1 - margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }
        c0 = float2(1 - (rounding + margin.x), rounding + margin.y);
        if (uv.x > c0.x && uv.y < c0.y && uv.x < 1 - margin.x && uv.y > margin.y && !InRadius2(uv, c0, rounding * rounding)) {
            return true;
        }

        return false;
      }

      // Write the nth letter in the current cell and return the value of the
      // pixel.
      // `texture_rows` and `texture_cols` indicate how many rows and columns are
      // in the texture being sampled.
      float2 GetLetter(float2 uv, int nth_letter,
          float texture_cols, float texture_rows,
          float board_cols, float board_rows)
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
        if (CHAR_FRAC_ROW < 0.01 ||
            CHAR_FRAC_COL < 0.01 ||
            CHAR_FRAC_ROW > 0.99 ||
            CHAR_FRAC_COL > 0.99) {
          return float2(0, 0);
        }

        float LETTER_COL = fmod(nth_letter, floor(texture_cols));
        float LETTER_ROW = floor(texture_rows) - floor(nth_letter / floor(texture_cols));

        float LETTER_UV_ROW = (LETTER_ROW + CHAR_FRAC_ROW - 1.00) / texture_rows;
        float LETTER_UV_COL = (LETTER_COL + CHAR_FRAC_COL) / texture_cols;

        float2 result;
        result.x = LETTER_UV_COL;
        result.y = LETTER_UV_ROW;

        return result;
      }

      Texture2D GetTexture(int which_letter) {
        int which_texture = (int) floor(which_letter / (64 * 64));

        [forcecase] switch (which_letter)
        {
          case 0:
            return _Font_0x0000_0x1FFF;
          case 1:
            return _Font_0x2000_0x3FFF;
          case 2:
            return _Font_0x4000_0x5FFF;
          case 3:
            return _Font_0x6000_0x7FFF;
          case 4:
            return _Font_0x8000_0x9FFF;
          case 5:
            return _Font_0xA000_0xBFFF;
          case 6:
            return _Font_0xC000_0xDFFF;
          default:
            return _Font_0x0000_0x1FFF;
        }
      }

      // Get the value of the parameter for the cell we're in.
      int GetLetterParameter(float2 uv)
      {
        float CHAR_COL = floor(uv.x * NCOLS);
        float CHAR_ROW = floor(uv.y * NROWS);
        int res = 0;

        // %TEMPLATE__CG_LETTER_ACCESSOR%
        return res;
      }

      fixed sq_dist(fixed2 p0, fixed2 p1)
      {
        fixed2 delta = p1 - p0;
        //return abs(delta.x) + abs(delta.y);
        return max(abs(delta.x), abs(delta.y));
      }

      fixed4 effect_squares (v2f i)
      {
        const fixed time = _Time.y;

        #define PI 3.1415926535
        fixed theta = PI/4 + sin(time / 4) * 0.1;
        fixed2x2 rot =
          fixed2x2(cos(theta), -1 * sin(theta),
          sin(theta), cos(theta));

        #define NSQ_X 9.0
        #define NSQ_Y 5.0

        // Map uv from [0, 1] to [-.5, .5].
        fixed2 p = i.uv - 0.5;
        p *= fixed2(NSQ_X, NSQ_Y);
        p = mul(rot, p);
        p -= 0.5;

        // See how far we are from the nearest grid point
        fixed2 intra_pos = frac(p);
        fixed2 intra_center = fixed2(0.5, 0.5);
        fixed intra_dist = sq_dist(intra_pos, intra_center);

        fixed st0 = (sin(time) + 1) / 2;
        fixed st1 = (sin(time + PI/8) + 1) / 2;
        fixed st2 = (sin(time + PI/2) + 1) / 2;
        fixed st3 = (sin(time + PI/2 + PI/8) + 1) / 2;

        fixed2 center = fixed2(0, 0);
        center = mul(rot, center);
        center -= 0.5;
        fixed2 rot_lim = fixed2(NSQ_X, NSQ_Y);
        rot_lim = mul(rot, rot_lim);
        rot_lim -= 0.5;

        float v = 0;
        float x = 0;

        if (intra_dist > 0.5 * (0.5 + sin(time * 1.5) * 0.1)) {
          v = intra_dist;
        } else {
          v = 0;
        }

        fixed extra_dist = sq_dist(p, center);
        fixed check = max(rot_lim.x, rot_lim.y) / 2;
        if (extra_dist > check * st0) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st1) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st2) {
          v = 1.0 - v;
        }
        if (extra_dist > check * st3) {
          v = 1.0 - v;
        } else {
          x = 0.50;
        }

        fixed3 hsv;
        hsv[0] = (v * 0.2 * (1 - x * .8) + 0.55) - x;
        hsv[1] = 0.7;
        hsv[2] = 0.8;

        fixed3 col = HSVtoRGB(hsv);

        return fixed4(col, 1.0);
      }

      fixed4 margin_effect(v2f i)
      {
        if (Enable_Margin_Effect_Squares) {
          return effect_squares(i);
        } else {
          return Margin_Color;
        }
      }

      fixed4 frag (v2f i) : SV_Target
      {
        float2 uv = i.uv;

        // Derived from github.com/pema99/shader-knowledge (MIT license).
        if (unity_CameraProjection[2][0] != 0.0 ||
            unity_CameraProjection[2][1] != 0.0) {
          uv.x = 1.0 - uv.x;
        }

        float2 uv_margin = float2(Margin_Scale, Margin_Scale * 2) / 2;
        if (Render_Margin) {
          if (Margin_Rounding_Scale > 0.0) {
            if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/true)) {
              return margin_effect(i);
            }
            if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/false)) {
              return fixed4(0, 0, 0, 0);
            }
          }
          if (InMargin(uv, uv_margin)) {
            if (InSpeechIndicator(uv, uv_margin)) {
              if (floor(_TaSTT_Indicator_0) == 1.0) {
                // Actively speaking
                return float3tofixed4(TaSTT_Indicator_Color_2, 1.0);
              } else if (floor(_TaSTT_Indicator_1) == 1.0) {
                // Done speaking, waiting for paging.
                return float3tofixed4(TaSTT_Indicator_Color_1, 1.0);
              } else {
                // Neither speaking nor paging.
                return float3tofixed4(TaSTT_Indicator_Color_0, 1.0);
              }
            }

            if (Render_Margin) {
              return margin_effect(i);
            }
          }
        }

        uv_margin *= 4;
        float2 uv_with_margin = AddMarginToUV(uv, uv_margin);

        fixed4 text = fixed4(0, 0, 0, 0);
        {
          int letter = GetLetterParameter(uv_with_margin);

          float texture_cols;
          float texture_rows;
          float2 letter_uv;
          if (letter < 0xE000) {
            texture_cols = 128.0;
            texture_rows = 64.0;
            letter_uv = GetLetter(uv_with_margin, letter, texture_cols, texture_rows, NCOLS, NROWS);
          } else {
            texture_cols = 8.0;
            texture_rows = 8.0;
            letter_uv = GetLetter(uv_with_margin, letter, texture_cols, texture_rows, 8, 4);
          }

          int which_texture = (int) floor(letter / (64 * 128));
          [forcecase] switch (which_texture)
          {
            case 0:
              text = _Font_0x0000_0x1FFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 1:
              text = _Font_0x2000_0x3FFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 2:
              text = _Font_0x4000_0x5FFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 3:
              text = _Font_0x6000_0x7FFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 4:
              text = _Font_0x8000_0x9FFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 5:
              text = _Font_0xA000_0xBFFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            case 6:
              text = _Font_0xC000_0xDFFF.Sample(sampler_linear_repeat, letter_uv);
              break;
            default:
              text = _Img_0xE000_0xE03F.Sample(sampler_linear_repeat, letter_uv);
              break;
          }
        }
        fixed4 black = fixed4(0,0,0,1);
        if (text.r == black.r && text.g == black.g && text.b == black.b && text.a == black.a) {
          if (Use_Custom_Background) {
            return Custom_Background.Sample(sampler_linear_repeat, uv);
          } else {
            return Background_Color;
          }
        } else {
          return Text_Color;
        }
      }
      ENDCG
    }
  }
}
