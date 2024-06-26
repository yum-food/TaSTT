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

float _Emerge;
float _Ellipsis;

float4 _Text_Color;
float _Text_Metallic;
float _Text_Smoothness;
float _Text_Emissive;

float4 _BG_Color;
float _BG_Metallic;
float _BG_Smoothness;
float _BG_Emissive;

float4 _Frame_Color;
float _Frame_Metallic;
float _Frame_Smoothness;
float _Frame_Emissive;

#define MY_COORD_SCALE 100
#define MY_COORD_SCALE_INV 1.0 / MY_COORD_SCALE
#define OBJ_SPACE_TO_MINE \
  float4x4( \
      MY_COORD_SCALE, 0, 0, 0, \
      0, MY_COORD_SCALE, 0, 0, \
      0, 0, MY_COORD_SCALE, 0, \
      0, 0, 0, MY_COORD_SCALE \
      )
#define WORLD_SPACE_TO_MINE \
  mul(unity_WorldToObject, OBJ_SPACE_TO_MINE)
#define MY_SPACE_TO_OBJ \
  float4x4( \
      MY_COORD_SCALE_INV, 0, 0, 0, \
      0, MY_COORD_SCALE_INV, 0, 0, \
      0, 0, MY_COORD_SCALE_INV, 0, \
      0, 0, 0, MY_COORD_SCALE_INV \
      )
#define MY_SPACE_TO_WORLD \
  mul(MY_SPACE_TO_OBJ, unity_ObjectToWorld)

#define MINIMUM_HIT_DISTANCE .00002 * MY_COORD_SCALE
#define MAXIMUM_TRACE_DISTANCE 2 * MY_COORD_SCALE

// Allows us to divide [0,1] into `n_phases` equal-sized slices and remap `r`
// onto the `nth_phase`.
//
// A few examples:
//  get_phase_fraction(0.9, 0, 2) = 1.0
//  get_phase_fraction(0.9, 1, 2) = 0.8
//  get_phase_fraction(0.5, 0, 3) = 1.0
//  get_phase_fraction(0.5, 1, 3) = 0.5
//  get_phase_fraction(0.5, 2, 3) = 0.0
//
// So if `r` is past the slice we're looking at, it returns 1; if it's before
// the slice we're looking at, it returns 0; if it's on the slice we're looking
// at, it gets remapped onto [0,1].
float get_phase_fraction(float r, float nth_phase, float n_phases) {
  float stride = 1.0 / n_phases;

  // Prevent boundary condition where saturated values get set to 0 by the
  // glsl_mod below.
  r = min(.9999 * (nth_phase + 1) * stride, r);

  float r0 = clamp(r, nth_phase * stride, (nth_phase + 1) * stride);
  r0 = glsl_mod(r0, stride);

  return r0 / stride;
}

// d = base edge length
// h = height
// e = frame thickness
// Pyramid base is on xy plane.
float distance_from_rect_pyramid_frame(float3 p, float dx, float dy, float h, float e, float skew)
{
  float3 p0 = float3(dx/2, dy/2, 0);
  float3 p1 = float3(dx/2, -dy/2, 0);
  float3 p3 = float3(-dx/2, dy/2, 0);
  float3 p4 = float3(skew, 0, h);

  float3 pp = p;
  // Symmetry
  pp.x = abs(pp.x);
  float d01 = distance_from_line_segment(pp, p0, p1, e);

  pp = p;
  pp.y = abs(pp.y);
  float d03 = distance_from_line_segment(pp, p0, p3, e);
  float d04 = distance_from_line_segment(pp, p0, p4, e);
  float d14 = distance_from_line_segment(pp, p3, p4, e);

  float dist = 1000;
  dist = min(dist, d01);
  dist = min(dist, d04);
  dist = min(dist, d03);
  dist = min(dist, d14);

  return dist;
}

#define OBJ_ID_NONE 0
#define OBJ_ID_FRAME 1
#define OBJ_ID_BG 2

float stt_map(float3 p, out int obj_id, out float2 text_uv)
{
  obj_id = OBJ_ID_NONE;

  float p0r = get_phase_fraction(_Emerge, 0, 4);
  float p1r = get_phase_fraction(_Emerge, 1, 4);
  float p2r = get_phase_fraction(_Emerge, 2, 4);
  float p3r = get_phase_fraction(_Emerge, 3, 4);

  float dist = 1000 * 1000 * 1000;
  float3 box_scale_g = float3(1, 1, .85) * MY_COORD_SCALE;
  float3 box_center_g = float3(.020, 0, .0122) * MY_COORD_SCALE;
  {
    float3 pp = p;
    pp -= box_center_g;

    float box_thck = .0002 * MY_COORD_SCALE;

    float3 box_sz = float3(6, .5, 3) * .003 * box_scale_g;

    // Use this to make the box grow out of the bottom left corner instead of the
    // middle.
    float3 emerge_offset = 0;
    emerge_offset.x = lerp(box_sz.x, box_thck, p1r);
    emerge_offset.z = lerp(box_sz.z, box_thck, p2r);
    pp += emerge_offset;

    box_sz.y = lerp(box_thck, box_sz.y, p0r) * p0r;
    box_sz.x = lerp(box_thck, box_sz.x, p1r) * p0r;
    box_sz.z = lerp(box_thck, box_sz.z, p2r) * p0r;

    float d = distance_from_box_frame(pp, box_sz, box_thck);

    obj_id = lerp(obj_id, OBJ_ID_FRAME, d < dist);
    dist = min(dist, d);
  }
  {
    float3 pp = p;
    pp -= box_center_g;
    //pp -= float3(-0.00018, .0013, -.0002) * MY_COORD_SCALE;
    pp -= float3(-0.00018, 0, -.0002) * MY_COORD_SCALE;

    float3 box_scale = float3(10, 0.1, 4.9) * .00175 * box_scale_g;
    float3 box_pad = float3(.001, 0, .001) * MY_COORD_SCALE;
    box_scale -= box_pad;

    // Use this to make the board grow out of the left edge instead of from the
    // center.
    float3 emerge_offset = 0;
    emerge_offset.x = lerp(box_scale.x, 0, p3r);
    pp += emerge_offset;

    box_scale.x = lerp(0, box_scale.x, p3r);
    box_scale.y *= ceil(p3r);
    box_scale.z *= ceil(p3r);

    // Only use calculation when in phase 3.
    float d = lerp(1000, distance_from_box(pp, box_scale), ceil(p3r));

    text_uv = (clamp(pp.xz, -1 * box_scale.xz, box_scale.xz) / box_scale.xz);
    text_uv = (text_uv + 1) / 2;

    bool in_mirror = !((unity_CameraProjection[2][0] == 0.0) * (unity_CameraProjection[2][1] == 0.0));
    text_uv = lerp(text_uv, float2(1.0 - text_uv.x, text_uv.y), in_mirror);

    obj_id = lerp(obj_id, OBJ_ID_BG, d < dist);
    dist = min(dist, d);
  }
  {
    float3 pp = p;

    pp -= box_center_g - float3(6, 0, 3) * .003 * box_scale_g;

    float scale = .0025 + .0002;
    scale *= MY_COORD_SCALE;
    pp.x -= scale/2;

    float edgex = 1 * scale;
    float edgey = 1 * scale;
    float height = -1.3 * scale;
    float r = .06 * scale;
    float skew = -.75 * scale;

    pp.z += lerp(0, .0008 * MY_COORD_SCALE, p0r) * p0r;
    r = lerp(0, r, p0r) * p0r;
    edgey = lerp(0, edgey, p0r) * p0r;

    pp.x += lerp(edgex/2, 0, p1r);
    edgex = lerp(0, edgex, p1r);

    height = lerp(0, height, p2r);
    skew = lerp(0, skew, p3r);

    float d = distance_from_rect_pyramid_frame(pp, edgex, edgey, height, r, skew);
    obj_id = lerp(obj_id, OBJ_ID_FRAME, d < dist);
    dist = min(dist, d);
  }
  if (_Ellipsis > 0.1 && _Emerge > .99) {
    float3 pp = p;

    float3 xoff = float3(.003, 0, 0) * MY_COORD_SCALE;

    float r_small = .0005 * MY_COORD_SCALE;
    float r_big = .001 * MY_COORD_SCALE;
    float r_phase = glsl_mod(_Time[1], 1.0);

    float r0_p0r = get_phase_fraction(r_phase, 0, 8);
    float r0_p2r = get_phase_fraction(r_phase, 3, 8);
    float r1_p0r = get_phase_fraction(glsl_mod(r_phase + .25, 1.0), 0, 8);
    float r1_p2r = get_phase_fraction(glsl_mod(r_phase + .25, 1.0), 3, 8);
    float r2_p0r = get_phase_fraction(glsl_mod(r_phase + .50, 1.0), 0, 8);
    float r2_p2r = get_phase_fraction(glsl_mod(r_phase + .50, 1.0), 3, 8);

    float r0 = lerp(r_small, r_big, r0_p0r * (1 - r0_p2r));
    float r1 = lerp(r_small, r_big, r1_p0r * (1 - r1_p2r));
    float r2 = lerp(r_small, r_big, r2_p0r * (1 - r2_p2r));

    pp -= box_center_g;

    float d = distance_from_sphere(pp - xoff, 0, r0);
    d = min(d, distance_from_sphere(pp, 0, r1));
    d = min(d, distance_from_sphere(pp + xoff, 0, r2));

    obj_id = lerp(obj_id, OBJ_ID_FRAME, d < dist);
    dist = min(dist, d);
  }

  return dist;
}

// Calculate normals for ray-marched STT structure.
float3 stt_calculate_normal(in float3 p)
{
    const float3 small_step = float3(0.0001, 0.0, 0.0);

    // Calculate the 3D gradient. By definition, the gradient is orthogonal
    // (normal) to the surface.
    int obj_id;
    float2 text_uv;
    float gradient_x = stt_map(p + small_step.xyy, obj_id, text_uv) - stt_map(p - small_step.xyy, obj_id, text_uv);
    float gradient_y = stt_map(p + small_step.yxy, obj_id, text_uv) - stt_map(p - small_step.yxy, obj_id, text_uv);
    float gradient_z = stt_map(p + small_step.yyx, obj_id, text_uv) - stt_map(p - small_step.yyx, obj_id, text_uv);

    float3 normal = float3(gradient_x, gradient_y, gradient_z);

    return normalize(normal);
}

float get_letter_mask(float2 text_uv, bool mirror)
{
  float epsilon = .005;
  if (text_uv.x > epsilon && text_uv.x < 1 - epsilon &&
      text_uv.y > epsilon && text_uv.y < 1 - epsilon) {
    text_uv.y = 1.0 - text_uv.y;
    // Make backside render left-to-right.
    text_uv.x = lerp(text_uv.x, 1.0 - text_uv.x, mirror);
    text_uv = AddMarginToUV(1.0 - text_uv, .01);
    return GetLetter(text_uv);
  }
  return 0;
}

float3 stt_march(float3 ro, float3 rd, out int obj_id, out float2 text_uv, int steps)
{
    float total_distance_traveled = 0.0;
    float3 current_position = 0;
    float distance_to_closest = 1;

    #define STT_RAY_MARCH_STEPS 48
    for (int i = 0; (i < steps) *
        (distance_to_closest > MINIMUM_HIT_DISTANCE/4) *
        (total_distance_traveled < MAXIMUM_TRACE_DISTANCE); i++)
    {
        current_position = ro + total_distance_traveled * rd;
        distance_to_closest = stt_map(current_position, obj_id, text_uv);
        total_distance_traveled += distance_to_closest;
    }
    obj_id = lerp(OBJ_ID_NONE, obj_id, distance_to_closest < MINIMUM_HIT_DISTANCE);

    return current_position;
}

float4 stt_ray_march(float3 ro, float3 rd, inout v2f v2f_i, inout float depth)
{

    // TODO(yum) remove
    float3 old_world_pos = v2f_i.worldPos;
    depth = getWorldSpaceDepth(old_world_pos);

    int obj_id;
    float2 text_uv;
    float3 current_position = stt_march(ro, rd, obj_id, text_uv, /*steps=*/48);

    float3 normal = stt_calculate_normal(current_position);
    v2f_i.normal = normalize(mul(MY_SPACE_TO_WORLD, normal));
    v2f_i.worldPos = mul(MY_SPACE_TO_WORLD, float4(current_position, 1.0)).xyz;

    float letter_mask = get_letter_mask(text_uv, ((normal.y + 1) / 2) > .01);

    float4 text = light(v2f_i, _Text_Color, _Text_Metallic, _Text_Smoothness);
    text += _Text_Color * _Text_Emissive;
    text = clamp(text, 0, 1);

    float4 bg = light(v2f_i, _BG_Color, _BG_Metallic, _BG_Smoothness);
    bg += _BG_Color * _BG_Emissive;
    bg = clamp(bg, 0, 1);

    float4 frame = light(v2f_i, _Frame_Color, _Frame_Metallic, _Frame_Smoothness);
    frame += _Frame_Color * _Frame_Emissive;
    frame = clamp(frame, 0, 1);

    frame += _Frame_Color * _Frame_Emissive;
    frame = clamp(frame, 0, 1);

    // TODO(yum) restore
    //depth = getWorldSpaceDepth(v2f_i.worldPos);

    [forcecase]
    switch (obj_id) {
      case OBJ_ID_NONE:
        depth = -1000;
        return 0;
      case OBJ_ID_FRAME:
        return frame;
      case OBJ_ID_BG:
        return lerp(bg, text, letter_mask);
    }
}

float4 stt_ray_march(inout v2f v2f_i, inout float depth)
{
  float4 ray_march_color;
  {
    float3 camera_position = mul(WORLD_SPACE_TO_MINE, float4(_WorldSpaceCameraPos, 1.0)).xyz;
    float3 ro = camera_position;
    float3 rd = normalize(mul(WORLD_SPACE_TO_MINE, float4(v2f_i.worldPos, 1.0)).xyz - ro);
    float3 old_normal = v2f_i.normal;
    ray_march_color = stt_ray_march(ro, rd, v2f_i, depth);
    //v2f_i.normal = old_normal;
  }

  return ray_march_color;
}

#endif  // __RAY_MARCH_INC__

