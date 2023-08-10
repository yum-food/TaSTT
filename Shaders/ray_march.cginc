#ifndef __RAY_MARCH_INC__
#define __RAY_MARCH_INC__

#include "eyes_data.cginc"
#include "iq_sdf.cginc"
#include "math.cginc"
#include "Motion.cginc"
#include "pbr.cginc"
#include "pema99.cginc"
#include "poi.cginc"
#include "stt_text.cginc"

float Ray_March_Emerge;

float get_phase_fraction(float r, float nth_phase, float n_phases) {
  float stride = 1.0 / n_phases;

  // Prevent boundary condition where saturated values get set to 0 by the
  // glsl_mod below.
  r = min(.9999 * (nth_phase + 1) * stride, r);

  float r0 = clamp(r, nth_phase * stride, (nth_phase + 1) * stride);
  r0 = glsl_mod(r0, stride);

  return r0 / stride;
}

float stt_map(float3 p, out float3 hsv, out float smoothness, out float alpha, out float2 text_uv)
{
  hsv[0] = 0;
  hsv[1] = 1;
  hsv[2] = 1;
  smoothness = 0.3;
  alpha = 0;

  float p0r = get_phase_fraction(Ray_March_Emerge, 0, 3);
  float p1r = get_phase_fraction(Ray_March_Emerge, 1, 3);
  float p2r = get_phase_fraction(Ray_March_Emerge, 2, 3);

  float dist = 1000 * 1000 * 1000;
  {
    float3 pp = p;

    pp.x -= 0.02;
    pp.z -= 0.01;

    float box_thck = .0002;

    float3 box_sz = float3(6, .5, 3) * .003;
    box_sz.y = lerp(box_thck, box_sz.y, p0r) * p0r;
    box_sz.x = lerp(box_thck, box_sz.x, p1r) * p0r;
    box_sz.z = lerp(box_thck, box_sz.z, p2r) * p0r;

    float d = distance_from_box_frame(pp, box_sz, box_thck);

    alpha = (d < dist) * 1 + (d >= dist) * alpha;
    dist = min(dist, d);
  }
  {
    float3 pp = p;

    pp.x -= 0.02;
    pp.z -= 0.01;

    float3 box_scale = float3(.01, .0001, .005) * 1.6;

    float p3r = get_phase_fraction(Ray_March_Emerge, 3, 4);
    box_scale.x *= ceil(p3r);
    box_scale.y *= ceil(p3r);
    box_scale.z = lerp(0, box_scale.z, p3r);

    float d = distance_from_box(pp, box_scale);

    text_uv = (clamp(pp.xz, -1 * box_scale.xz, box_scale.xz) / box_scale.xz);
    text_uv = (text_uv + 1) / 2;

    alpha = (d < dist) * 1 + (d >= dist) * alpha;
    hsv[1] = (d < dist) * 0 + (d >= dist) * hsv[1];
    hsv[2] = (d < dist) * 0 + (d >= dist) * hsv[2];
    dist = min(dist, d);
  }

  return dist;
}

float3 stt_calculate_normal(in float3 p)
{
    // Setting a very low value makes the surface normals look noisy. In this
    // case. that's desired, since it produces a glittery effect.
    const float3 small_step = float3(0.0001, 0.0, 0.0);

    // Calculate the 3D gradient. By definition, the gradient is orthogonal
    // (normal) to the surface.
    float3 hsv;
    float smoothness;
    float alpha;
    float2 text_uv;
    float gradient_x = stt_map(p + small_step.xyy, hsv, smoothness, alpha, text_uv) - stt_map(p - small_step.xyy, hsv, smoothness, alpha, text_uv);
    float gradient_y = stt_map(p + small_step.yxy, hsv, smoothness, alpha, text_uv) - stt_map(p - small_step.yxy, hsv, smoothness, alpha, text_uv);
    float gradient_z = stt_map(p + small_step.yyx, hsv, smoothness, alpha, text_uv) - stt_map(p - small_step.yyx, hsv, smoothness, alpha, text_uv);

    float3 normal = float3(gradient_x, gradient_y, gradient_z);

    return normalize(normal);
}

float4 stt_ray_march(float3 ro, float3 rd, inout v2f v2f_i, inout float depth)
{
    float total_distance_traveled = 0.0;
    const float MINIMUM_HIT_DISTANCE = 1.0 / (1000 * 20);
    const float MAXIMUM_TRACE_DISTANCE = 1000.0;
    float3 current_position = 0;
    float distance_to_closest = 1;

    #define STT_RAY_MARCH_STEPS 32
    float4 color = 0;
    float metallic = 0.5;
    float smoothness;
    float alpha;
    float3 hsv;
    float2 text_uv;

    for (int i = 0; i < STT_RAY_MARCH_STEPS &&
        distance_to_closest > MINIMUM_HIT_DISTANCE &&
        total_distance_traveled < MAXIMUM_TRACE_DISTANCE; i++)
    {
        current_position = ro + total_distance_traveled * rd;
        distance_to_closest = stt_map(current_position, hsv, smoothness, alpha, text_uv);
        total_distance_traveled += distance_to_closest;
    }

    float3 normal = stt_calculate_normal(current_position);
    v2f_i.normal = normalize(mul(unity_ObjectToWorld, normal));

    float epsilon = .005;
    if (text_uv.x > epsilon && text_uv.x < 1 - epsilon &&
        text_uv.y > epsilon && text_uv.y < 1 - epsilon) {
      text_uv.y = 1.0 - text_uv.y;
      // Make backside render left-to-right.
      text_uv.x = lerp(text_uv.x, 1.0 - text_uv.x, (normal.y + 1) / 2);
      hsv[0] = 0;
      text_uv = AddMarginToUV(1.0 - text_uv, .01);
      hsv[1] = 0;
      hsv[2] = GetLetter(text_uv);
    }

    depth = getWorldSpaceDepth(mul(unity_ObjectToWorld, float4(current_position, 1.0)).xyz);
    color.xyz = HSVtoRGB(hsv);
    color.w = alpha;

    depth = lerp(-1000, depth, distance_to_closest < MINIMUM_HIT_DISTANCE);
    return lerp(0, light(v2f_i, color, metallic, smoothness), distance_to_closest < MINIMUM_HIT_DISTANCE);
}

float4 stt_ray_march(inout v2f v2f_i, inout float depth)
{
  float4 ray_march_color;
  {
    float3 camera_position = mul(unity_WorldToObject, float4(_WorldSpaceCameraPos, 1.0)).xyz;
    float3 ro = camera_position;
    float3 rd = normalize(mul(unity_WorldToObject, float4(v2f_i.worldPos, 1.0)).xyz - ro);
    float3 old_normal = v2f_i.normal;
    ray_march_color = stt_ray_march(ro, rd, v2f_i, depth);
    //v2f_i.normal = old_normal;
  }

  return ray_march_color;
}

#endif  // __RAY_MARCH_INC__

