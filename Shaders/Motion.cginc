#ifndef MOTION_
#define MOTION_

// xyz represent quaternion vector, w represents theta.
typedef float4 Quaternion;

// Math from here:
//   https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation
float3 qrot(in float3 v, in Quaternion q)
{
  float a = q.w;
  float b = q.x;
  float c = q.y;
  float d = q.z;

  float a2 = a*a;
  float b2 = b*b;
  float c2 = c*c;
  float d2 = d*d;

  float3x3 rot = float3x3(
    (a2 + b2 - c2) - d2, 2*b*c - 2*a*d, 2*b*d + 2*a*c,
    2*b*c + 2*a*d, (a2 - b2) + (c2 - d2), 2*c*d - 2*a*b,
    2*b*d - 2*a*c, 2*c*d + 2*a*b, ((a2 - b2) - c2) + d2
  );

  return mul(rot, v);
}

Quaternion qinv(in Quaternion q)
{
  return Quaternion(q.xyz, -q.w);
}

// Multiply two quaternions.
// Math from here: https://www.haroldserrano.com/blog/quaternions-in-computer-graphics
Quaternion qmul(in Quaternion a, in Quaternion b)
{
	return Quaternion(a.w * b.xyz + b.w * a.xyz + cross(a.xyz, b.xyz), a.w * b.w - dot(a.xyz, b.xyz));
}

float4 affine3(in float3 m)
{
  return float4(m, 1.0);
}

float4x4 affine3x3(in float3x3 m)
{
  return float4x4(
    m[0][0], m[0][1], m[0][2], 0,
    m[1][0], m[1][1], m[1][2], 0,
    m[2][0], m[2][1], m[2][2], 0,
    0,       0,       0,       1
  );
}

float4x4 eye()
{
  return float4x4(
    1, 0, 0, 0,
    0, 1, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1
  );
}

// Return affine translation matrix.
float4x4 translate(in float dx, in float dy, in float dz)
{
  return float4x4(
    1, 0, 0, dx,
    0, 1, 0, dy,
    0, 0, 1, dz,
    0, 0, 0, 1
  );
}

// Return affine scaling matrix.
float4x4 scale(in float sx, in float sy, in float sz)
{
  return float4x4(
    sx, 0,  0,  0,
    0,  sy, 0,  0,
    0,  0,  sz, 0,
    0,  0,  0,  1
  );
}

#endif // MOTION_

