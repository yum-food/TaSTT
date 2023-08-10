#ifndef TASTT_LIGHTING
#define TASTT_LIGHTING

#include "AutoLight.cginc"
#include "UnityPBSLighting.cginc"
#include "ray_march.cginc"
#include "pbr.cginc"
#include "poi.cginc"
#include "stt_generated.cginc"
#include "stt_text.cginc"

SamplerState linear_repeat_sampler;

float BG_Enable;
Texture2D BG_BaseColor;
Texture2D BG_NormalMap;
Texture2D BG_Metallic;
Texture2D BG_Smoothness;
float BG_Smoothness_Invert;
float BG_NormalStrength;
float4 BG_BaseColor_ST;
float4 BG_NormalMap_ST;
float4 BG_Metallic_ST;
float4 BG_Smoothness_ST;

fixed4 Text_Color;
fixed4 Background_Color;
fixed4 Margin_Color;

float Metallic;
float Smoothness;
float Emissive;

float Render_Margin;
float Render_Visual_Indicator;
float Margin_Scale;
float Margin_Rounding_Scale;
float Enable_Margin_Effect_Squares;
float Enable_Ray_March;

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

v2f vert(appdata v)
{
  v2f o;
  o.position = UnityObjectToClipPos(v.position);
  o.worldPos = mul(unity_ObjectToWorld, v.position);
  o.normal = UnityObjectToWorldNormal(v.normal);

  o.uv.xy = TRANSFORM_TEX(v.uv, BG_BaseColor);
  o.uv.zw = 1.0 - v.uv;
  getVertexLightColor(o);

  return o;
}

// dist = sqrt(dx^2 + dy^2) = sqrt(<dx,dy> * <dx,dy>)
bool InRadius2(float2 uv, float2 pos, float radius2)
{
  float2 delta = uv - pos;
  return dot(delta, delta) < radius2;
}

bool InMargin(float2 uv, float2 margin)
{
  bool b0 = uv.x < margin.x;
  bool b1 = uv.x > 1 - margin.x;
  bool b2 = uv.y < margin.y;
  bool b3 = uv.y >  1 - margin.y;

  // De Morgan's law:
  //  a OR b = !(!a AND !b)
  return !(!b0 * !b1 * !b2 * !b3);
}

bool InSpeechIndicator(float2 uv, float2 margin)
{
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

  return Render_Visual_Indicator && InRadius2(uv, indicator_center, radius * radius);
}

bool InMarginRounding(float2 uv, float2 margin, float rounding, bool interior)
{
  if (!interior) {
    rounding += margin.x;
    margin = float2(0, 0);
    float err_margin = 0.001;
    if (uv.x < err_margin || uv.x > 1.0 - err_margin ||
        uv.y < err_margin || uv.y > 1.0 - err_margin) {
      return true;
    }
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

fixed sq_dist(fixed2 p0, fixed2 p1)
{
  fixed2 delta = p1 - p0;
  //return abs(delta.x) + abs(delta.y);
  return max(abs(delta.x), abs(delta.y));
}

fixed4 effect_squares (v2f i)
{
  float2 uv = i.uv.zw;
  uv.y *= 2;  // Text box has 2:1 aspect ratio
  const fixed time = _Time.y;

  fixed theta = PI/4 + sin(time / 4) * 0.1;
  fixed2x2 rot =
    fixed2x2(cos(theta), -1 * sin(theta),
    sin(theta), cos(theta));

  #define NSQ_X 9.0
  #define NSQ_Y 5.0

  // Map uv from [0, 1] to [-.5, .5].
  fixed2 p = uv - 0.5;
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

fixed4 light(v2f i,
    Texture2D albedo_map,
    Texture2D normal_map,
    float normal_str,
    Texture2D metallic_map,
    Texture2D smoothness_map,
    float invert_smoothness,
    Texture2D emission_mask,
    float3 emission_color,
    out float depth)
{
  initNormal(i);

  depth = getWorldSpaceDepth(i.worldPos);

  float2 iddx = ddx(i.uv.x);
  float2 iddy = ddy(i.uv.y);
  fixed4 albedo = albedo_map.SampleGrad(linear_repeat_sampler, i.uv.xy,
      iddx, iddy);

  fixed3 normal = UnpackScaleNormal(
        normal_map.SampleGrad(linear_repeat_sampler, i.uv.xy,
            iddx, iddy),
        normal_str);
  // Swap Y and Z
  normal = normal.xzy;

  float3 view_dir = normalize(_WorldSpaceCameraPos - i.worldPos);

  float metallic = metallic_map.SampleGrad(linear_repeat_sampler, i.uv.xy,
      iddx, iddy);

  float3 specular_tint;
  float one_minus_reflectivity;
  albedo.rgb = DiffuseAndSpecularFromMetallic(
    albedo, metallic, specular_tint, one_minus_reflectivity);

  UnityIndirect indirect_light;
  indirect_light.diffuse = 0;
  indirect_light.specular = 0;

  float smoothness = smoothness_map.SampleGrad(linear_repeat_sampler, i.uv.xy,
      iddx, iddy);
  if (invert_smoothness) {
    smoothness = 1 - smoothness;
  }

  fixed3 emission = emission_mask.SampleGrad(linear_repeat_sampler, i.uv.xy,
      iddx, iddy);

  fixed3 pbr = UNITY_BRDF_PBS(albedo, specular_tint,
      one_minus_reflectivity, smoothness,
      i.normal, view_dir, GetLight(i), GetIndirect(i, view_dir, smoothness)).rgb;
  pbr.rgb += emission;

  return fixed4(pbr, albedo.a);
}

fixed4 light(v2f i, fixed4 unlit, out float depth)
{
  depth = getWorldSpaceDepth(i.worldPos);

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
      i.normal, view_dir, GetLight(i), GetIndirect(i, view_dir, Smoothness)).rgb;

  pbr = lerp(pbr.rgb, unlit.rgb, Emissive);

  return fixed4(pbr, unlit.a);
}

fixed4 frag(v2f i, out float depth : SV_DepthLessEqual) : SV_Target
{
  float2 uv = i.uv.zw;
  depth = -1000.0;

  if (Enable_Ray_March) {
    return stt_ray_march(i, depth);
  }

  // Fix text orientation
  uv.y = 0.5 - uv.y;
  uv.x = 1.0 - uv.x;
  uv.y *= 2;  // Text box has 2:1 aspect ratio

  // Derived from github.com/pema99/shader-knowledge (MIT license).
  if (unity_CameraProjection[2][0] != 0.0 ||
      unity_CameraProjection[2][1] != 0.0) {
    uv.x = 1.0 - uv.x;
  }

  float2 uv_margin = float2(Margin_Scale, Margin_Scale * 2) / 2;
  if (Render_Margin) {
    if (Margin_Rounding_Scale > 0.0) {
      if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/true)) {
        return light(i, margin_effect(i), depth);
      }
      if (InMarginRounding(uv, uv_margin, Margin_Rounding_Scale, /*interior=*/false)) {
        return fixed4(0, 0, 0, 0);
      }
    }
    if (InMargin(uv, uv_margin)) {
      if (InSpeechIndicator(uv, uv_margin)) {
        if (floor(_TaSTT_Indicator_0) == 1.0) {
          // Actively speaking
          return light(i, float3tofixed4(TaSTT_Indicator_Color_2, 1.0), depth);
        } else if (floor(_TaSTT_Indicator_1) == 1.0) {
          // Done speaking, waiting for paging.
          return light(i, float3tofixed4(TaSTT_Indicator_Color_1, 1.0), depth);
        } else {
          // Neither speaking nor paging.
          return light(i, float3tofixed4(TaSTT_Indicator_Color_0, 1.0), depth);
        }
      }

      if (Render_Margin) {
        return light(i, margin_effect(i), depth);
      }
    }
  }

  uv_margin *= 4;
  float2 uv_with_margin = AddMarginToUV(uv, uv_margin);

  fixed4 text = GetLetter(uv_with_margin);

  if (text.a == 0) {
    fixed4 bg;
    if (BG_Enable) {

#if 0
fixed4 light(inout v2f i,
    fixed4 albedo,
    float metallic,
    float smoothness)
#endif

      const float iddx = ddx(i.uv.x);
      const float iddy = ddy(i.uv.y);
      fixed4 albedo = BG_BaseColor.SampleGrad(linear_repeat_sampler, i.uv.xy,
          iddx, iddy);
      float metallic = BG_Metallic.SampleGrad(linear_repeat_sampler, i.uv.xy,
          iddx, iddy);
      float smoothness = BG_Smoothness.SampleGrad(linear_repeat_sampler, i.uv.xy,
          iddx, iddy);

      bg = light(i,
          albedo, metallic, smoothness);
    } else {
      bg = light(i, Background_Color, depth);
    }
    // Hack: If alpha (text.w) is less than 0.5, don't render it. This
    // eliminates outlines around simple emotes with transparent backgrounds.
    if (text.w > 0.5) {
      // Use emote alpha to mix emote color with background color (compositing).
      text.rgb = lerp(bg.rgb, text.rgb, text.w);
      bg = light(i, fixed4(text.rgb, 1.0), depth);
    }
    return bg;
  } else {
    return light(i, Text_Color, depth);
  }
}

#endif  // TASTT_LIGHTING
