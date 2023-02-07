#ifndef PBS_LIGHTING
#define PBS_LIGHTING

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
  float4 uv : TEXCOORD0;
  float3 normal : TEXCOORD1;
  float3 worldPos : TEXCOORD2;

  #if defined(VERTEXLIGHT_ON)
  float3 vertexLightColor : TEXCOORD3;
  #endif
};

float BG_Enable;
sampler2D BG_BaseColor;
sampler2D BG_NormalMap;
sampler2D BG_Metallic;
sampler2D BG_Smoothness;
sampler2D BG_Emission_Mask;
float BG_Smoothness_Invert;
float BG_NormalStrength;
float3 BG_Emission_Color;
float4 BG_BaseColor_ST;
float4 BG_NormalMap_ST;
float4 BG_Metallic_ST;
float4 BG_Smoothness_ST;
float4 BG_Emission_Mask_ST;

float Enable_Custom_Cubemap;
UNITY_DECLARE_TEXCUBE(Custom_Cubemap);

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
  o.position = mul(UNITY_MATRIX_MVP, v.position);
  o.worldPos = mul(unity_ObjectToWorld, v.position);
  o.normal = UnityObjectToWorldNormal(v.normal);
  o.uv.xy = TRANSFORM_TEX(v.uv, BG_BaseColor);
  o.uv.zw = 1.0 - v.uv;
  getVertexLightColor(o);
  return o;
}

fixed sq_dist(fixed2 p0, fixed2 p1)
{
  fixed2 delta = p1 - p0;
  return max(abs(delta.x), abs(delta.y));
}

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

fixed4 effect_squares (v2f i)
{
  float2 uv = i.uv.zw;
  uv.y *= 2;  // Text box has 2:1 aspect ratio
  const fixed time = _Time.y;

  #define PI 3.1415926535
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
  return effect_squares(i);
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

UnityIndirect GetIndirect(v2f i, float3 view_dir, float smoothness) {
  UnityIndirect indirect;
  indirect.diffuse = 0;
  indirect.specular = 0;

  #if defined(VERTEXLIGHT_ON)
  indirect.diffuse = i.vertexLightColor;
  #endif

  #if defined(FORWARD_BASE_PASS)
  indirect.diffuse += max(0, ShadeSH9(float4(i.normal, 1)));
  float3 reflect_dir = reflect(-view_dir, i.normal);
  // There's a nonlinear relationship between mipmap level and roughness.
  float roughness = 1 - smoothness;
  roughness *= 1.7 - .7 * roughness;
  float3 env_sample;
  if (Enable_Custom_Cubemap) {
    env_sample = UNITY_SAMPLE_TEXCUBE_LOD(
        Custom_Cubemap,
        reflect_dir,
        roughness * UNITY_SPECCUBE_LOD_STEPS);
  } else {
    env_sample = UNITY_SAMPLE_TEXCUBE_LOD(
        unity_SpecCube0,
        reflect_dir,
        roughness * UNITY_SPECCUBE_LOD_STEPS);
  }
  indirect.specular = env_sample;
  #endif

  return indirect;
}

void initNormal(inout v2f i)
{
  if (BG_Enable) {
    i.normal = UnpackScaleNormal(
        tex2Dgrad(BG_NormalMap, i.uv.xy, ddx(i.uv.x), ddy(i.uv.y)),
        BG_NormalStrength);
    // Swap Y and Z
    i.normal = i.normal.xzy;
  }
  i.normal = normalize(i.normal);
}

fixed4 light(v2f i,
    sampler2D albedo_map,
    sampler2D normal_map,
    float normal_str,
    sampler2D metallic_map,
    sampler2D smoothness_map,
    float invert_smoothness,
    sampler2D emission_mask,
    float3 emission_color)
{
  initNormal(i);

  float2 iddx = ddx(i.uv.x);
  float2 iddy = ddy(i.uv.y);
  fixed4 albedo = tex2Dgrad(albedo_map, i.uv, iddx, iddy);

  fixed3 normal = UnpackScaleNormal(
        tex2Dgrad(normal_map, i.uv.xy, iddx, iddy),
        normal_str);
  // Swap Y and Z
  normal = normal.xzy;

  float3 view_dir = normalize(_WorldSpaceCameraPos - i.worldPos);

  float metallic = tex2Dgrad(metallic_map, i.uv.xy, iddx, iddy);

  float3 specular_tint;
  float one_minus_reflectivity;
  albedo.rgb = DiffuseAndSpecularFromMetallic(
    albedo, metallic, specular_tint, one_minus_reflectivity);

  UnityIndirect indirect_light;
  indirect_light.diffuse = 0;
  indirect_light.specular = 0;

  float smoothness = tex2Dgrad(smoothness_map, i.uv.xy, iddx, iddy);
  if (invert_smoothness) {
    smoothness = 1 - smoothness;
  }

  fixed3 emission = tex2Dgrad(emission_mask, i.uv.xy, iddx, iddy) * emission_color;

  fixed3 pbr = UNITY_BRDF_PBS(albedo, specular_tint,
      one_minus_reflectivity, smoothness,
      i.normal, view_dir, GetLight(i), GetIndirect(i, view_dir, smoothness)).rgb;
  pbr.rgb += emission;

  return fixed4(pbr, albedo.a);
}

fixed4 frag(v2f i) : SV_Target
{
  float2 uv = i.uv.zw;
  // Fix text orientation
  uv.y = 0.5 - uv.y;
  uv.x = 1.0 - uv.x;
  uv.y *= 2;  // Text box has 2:1 aspect ratio

  // Derived from github.com/pema99/shader-knowledge (MIT license).
  if (unity_CameraProjection[2][0] != 0.0 ||
      unity_CameraProjection[2][1] != 0.0) {
    uv.x = 1.0 - uv.x;
  }

  if (BG_Enable) {
    return light(i,
        BG_BaseColor,
        BG_NormalMap,
        BG_NormalStrength,
        BG_Metallic,
        BG_Smoothness,
        BG_Smoothness_Invert,
        BG_Emission_Mask,
        BG_Emission_Color);
  } else {
    return fixed4(1, 1, 1, 0);
  }
}

#endif  // PBS_LIGHTING

