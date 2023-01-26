#ifndef TASTT_LIGHTING
#define TASTT_LIGHTING

#include "AutoLight.cginc"
#include "UnityPBSLighting.cginc"

struct appdata
{
  float4 position : POSITION;
  float2 uv : TEXCOORD0;
  float3 normal : NORMAL;
};

struct v2f
{
  float4 position : SV_POSITION;
  float2 uv : TEXCOORD0;
  float3 normal : TEXCOORD1;
  float3 worldPos : TEXCOORD2;

  #if defined(VERTEXLIGHT_ON)
  float3 vertexLightColor : TEXCOORD3;
  #endif
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
fixed4 Specular_Tint;

float Metallic;
float Smoothness;
float Emissive;

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

void getVertexLightColor(inout v2f i)
{
  #if defined(VERTEXLIGHT_ON)
  float3 light_pos = float3(unity_4LightPosX0.x, unity_4LightPosY0.x,
      unity_4LightPosZ0.x);
  float3 light_vec = light_pos - i.worldPos;
  float3 light_dir = normalize(light_vec);
  float ndotl = DotClamped(i.normal, light_dir);
  // Light fills an expanding sphere with surface area 4 * pi * r^2.
  // By conservation of energy, this means that at distance r, light intensity
  // is proportional to 1/(r^2).
  float attenuation = 1 / (1 + dot(light_vec, light_vec) * unity_4LightAtten0.x);
  i.vertexLightColor = unity_LightColor[0].rgb * ndotl * attenuation;

  i.vertexLightColor = Shade4PointLights(
    unity_4LightPosX0, unity_4LightPosY0, unity_4LightPosZ0,
    unity_LightColor[0].rgb,
    unity_LightColor[1].rgb,
    unity_LightColor[2].rgb,
    unity_LightColor[3].rgb,
    unity_4LightAtten0, i.worldPos, i.normal
  );
  #endif
}

v2f vert (appdata v)
{
  v2f o;
  o.position = mul(UNITY_MATRIX_MVP, v.position);
  o.worldPos = mul(unity_ObjectToWorld, v.position);
  o.uv = 1.0 - v.uv;
  o.normal = UnityObjectToWorldNormal(v.normal);
  getVertexLightColor(o);
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

UnityLight GetLight(v2f i)
{
  UNITY_LIGHT_ATTENUATION(attenuation, 0, i.worldPos);
  float3 light_color = _LightColor0.rgb * attenuation;

  UnityLight light;
  light.color = light_color;
  #if defined(POINT) || defined(POINT_COOKIE) || defined(SPOT)
  light.dir = normalize(_WorldSpaceLightPos0.xyz - i.worldPos);
  #else
  light.dir = _WorldSpaceLightPos0.xyz;
  #endif
  light.ndotl = DotClamped(i.normal, light.dir);

  return light;
}

UnityIndirect GetIndirect(v2f i) {
  UnityIndirect indirect;
  indirect.diffuse = 0;
  indirect.specular = 0;

  #if defined(VERTEXLIGHT_ON)
  indirect.diffuse = i.vertexLightColor;
  #endif

  #if defined(FORWARD_BASE_PASS)
  indirect.diffuse += max(0, ShadeSH9(float4(i.normal, 1)));
  #endif

  return indirect;
}

fixed4 light(v2f i, fixed4 unlit)
{
  // Get color in spherical harmonics
  fixed3 albedo = unlit.rgb;

  float3 view_dir = normalize(_WorldSpaceCameraPos - i.worldPos);

  float3 specular_tint;
  float one_minus_reflectivity;
  albedo = DiffuseAndSpecularFromMetallic(
    albedo, Metallic, specular_tint, one_minus_reflectivity);

  UnityIndirect indirect_light;
  indirect_light.diffuse = 0;
  indirect_light.specular = 0;

  fixed3 pbr = UNITY_BRDF_PBS(albedo, specular_tint,
      one_minus_reflectivity, Smoothness,
      i.normal, view_dir, GetLight(i), GetIndirect(i)).rgb;

  pbr = lerp(pbr.rgb, unlit.rgb, Emissive);

  return fixed4(pbr, unlit.a);
}

fixed4 frag (v2f i) : SV_Target
{
  float2 uv = i.uv;
  i.normal = normalize(i.normal);

  // Derived from github.com/pema99/shader-knowledge (MIT license).
  if (unity_CameraProjection[2][0] != 0.0 ||
      unity_CameraProjection[2][1] != 0.0) {
    uv.x = 1.0 - uv.x;
  }

  float2 uv_margin = float2(Margin_Scale, Margin_Scale * 2) / 2;
  if (Render_Margin) {
    if (Margin_Rounding_Scale > 0.0) {
      if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/true)) {
        return light(i, margin_effect(i));
      }
      if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/false)) {
        return light(i, fixed4(0, 0, 0, 0));
      }
    }
    if (InMargin(uv, uv_margin)) {
      if (InSpeechIndicator(uv, uv_margin)) {
        if (floor(_TaSTT_Indicator_0) == 1.0) {
          // Actively speaking
          return light(i, float3tofixed4(TaSTT_Indicator_Color_2, 1.0));
        } else if (floor(_TaSTT_Indicator_1) == 1.0) {
          // Done speaking, waiting for paging.
          return light(i, float3tofixed4(TaSTT_Indicator_Color_1, 1.0));
        } else {
          // Neither speaking nor paging.
          return light(i, float3tofixed4(TaSTT_Indicator_Color_0, 1.0));
        }
      }

      if (Render_Margin) {
        return light(i, margin_effect(i));
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
      return light(
          i,
          Custom_Background.Sample(sampler_linear_repeat, uv));
    } else {
      return light(i, Background_Color);
    }
  } else {
    return light(i, Text_Color);
  }
}

#endif  // TASTT_LIGHTING
