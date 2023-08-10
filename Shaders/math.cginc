#ifndef __MATH_INC
#define __MATH_INC

#include "pema99.cginc"

#define PI 3.14159265

// Differentiable approximation of the standard `max` function.
float dmax(float a, float b, float k)
{
  return log2(exp2(k * a) + exp2(k * b)) / k;
}

// Differentiable approximation of the standard `min` function.
float dmin(float a, float b, float k)
{
  return -1.0 * dmax(-1.0 * a, -1.0 * b, k);
}

// Generate a random number on [0, 1].
float rand2(float3 p)
{
  return glsl_mod(sin(dot(p, float2(561.0, 885.0))) * 776.2, 1.0);
}

// Generate a random number on [0, 1].
float rand3(float3 p)
{
  return glsl_mod(sin(dot(p, float3(897.0, 367.0, 197.0))) * 1073.6, 1.0);
}

// 3 dimensional value noise. `p` is assumed to be a point inside a unit cube.
// Theory: https://en.wikipedia.org/wiki/Value_noise
float vnoise3d(float3 p)
{
  float3 pu = floor(p);
  float3 pv = glsl_mod(p, 1.0);

  // Assign random numbers to the corner of a cube.
  float n000 = rand3(pu + float3(0,0,0));
  float n001 = rand3(pu + float3(0,0,1));
  float n010 = rand3(pu + float3(0,1,0));
  float n011 = rand3(pu + float3(0,1,1));
  float n100 = rand3(pu + float3(1,0,0));
  float n101 = rand3(pu + float3(1,0,1));
  float n110 = rand3(pu + float3(1,1,0));
  float n111 = rand3(pu + float3(1,1,1));

  float n00 = lerp(n000, n001, pv.z);
  float n01 = lerp(n010, n011, pv.z);
  float n10 = lerp(n100, n101, pv.z);
  float n11 = lerp(n110, n111, pv.z);

  float n0 = lerp(n00, n01, pv.y);
  float n1 = lerp(n10, n11, pv.y);

  float n = lerp(n0, n1, pv.x);

  return n;
}

float fbm(float3 p, const int n_octaves, float w)
{
  float g = exp2(-w);
  float a = 1.0;
  float p_scale = 1.0;

  float res = 0.0;
  for (int i = 0; i < n_octaves; i++) {
    res += a * vnoise3d(p * p_scale);

    p_scale /= w;
    a *= g;
  }

  // On average, vnoise3d returns 0.5.
  // Sum of any geometric series is, for growth parameter r and constant a,
  // a / (1 - r).
  // We want to map onto [0, 1], so divide by this expected sum.
  // Use a = 1, to account for the worst-case possibility that every call to
  // vnoise3d() returns 1.
  res /= (1 / (1 - g));

  return res;
}

#endif  // __MATH_INC

