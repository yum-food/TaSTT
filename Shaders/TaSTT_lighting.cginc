#ifndef TASTT_LIGHTING
#define TASTT_LIGHTING

#include "AutoLight.cginc"
#include "UnityPBSLighting.cginc"
#include "ray_march.cginc"
#include "pbr.cginc"
#include "poi.cginc"
#include "stt_generated.cginc"
#include "stt_text.cginc"

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

  o.uv = v.uv;
  getVertexLightColor(o);

  return o;
}

fixed4 frag(v2f i, out float depth : SV_DepthLessEqual) : SV_Target
{
  depth = -1000.0;

  return stt_ray_march(i, depth);
}

#endif  // TASTT_LIGHTING
