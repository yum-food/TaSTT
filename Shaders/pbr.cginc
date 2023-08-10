#ifndef __PBR_INC__
#define __PBR_INC__

#include "AutoLight.cginc"
#include "eyes_data.cginc"
#include "UnityPBSLighting.cginc"

static float BG_Effect_Bias = 0.0;
static float BG_Effect_Weight = 1.0;

float BG_Effect_Emission_Strength;
float Enable_Custom_Cubemap;
UNITY_DECLARE_TEXCUBE(Custom_Cubemap);

sampler2D BG_Emission_Mask;
sampler2D BG_Emission_Color;

float BG_Emission_Strength;
float4 BG_Emission_Mask_ST;


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

void initNormal(inout v2f i)
{
  i.normal = normalize(i.normal);
}

fixed4 light(inout v2f i,
    fixed4 albedo,
    float metallic,
    float smoothness)
{
  initNormal(i);

  float2 iddx = ddx(i.uv.x);
  float2 iddy = ddy(i.uv.y);

  bool is_ray_hit = (albedo.r > 0 || albedo.g > 0 || albedo.b > 0);
  if (is_ray_hit) {
    albedo.rgb *= BG_Effect_Weight;
    albedo.rgb += BG_Effect_Bias;
  } else {
    albedo.rgb = float3(0, 0, 0);
  }

  float3 specular_tint;
  float one_minus_reflectivity;
  albedo.rgb = DiffuseAndSpecularFromMetallic(
    albedo, metallic, specular_tint, one_minus_reflectivity);

  float emission_mask_sample = tex2Dgrad(BG_Emission_Mask, i.uv.xy, iddx, iddy);
  fixed3 emission = emission_mask_sample *
      tex2Dgrad(BG_Emission_Color, i.uv.xy, iddx, iddy) * BG_Emission_Strength;

  float3 view_dir = normalize(_WorldSpaceCameraPos - i.worldPos);
  fixed3 pbr = UNITY_BRDF_PBS(albedo,
      specular_tint,
      one_minus_reflectivity,
      smoothness,
      i.normal,
      view_dir,
      GetLight(i),
      GetIndirect(i, view_dir, smoothness)).rgb;
  pbr.rgb += emission;
  pbr.rgb += albedo.rgb * BG_Effect_Emission_Strength;

  return fixed4(saturate(pbr), albedo.a);
}

float getWorldSpaceDepth(in float3 world_pos)
{
  float4 clip_pos = mul(UNITY_MATRIX_VP, float4(world_pos, 1.0));
  return clip_pos.z / clip_pos.w;
}

#endif  // __PBR_INC__

