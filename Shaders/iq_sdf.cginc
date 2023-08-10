#ifndef __IQ_SDF_INC__
#define __IQ_SDF_INC__

#include "pema99.cginc"

// The MIT License
// Copyright © 2020 Inigo Quilez
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

float distance_from_octahedron(in float3 p)
{
  float s = 1.0;
  float3 pp = abs(p);
  float m = pp.x+pp.y+pp.z-s;
  float3 q;
  if( 3.0*pp.x < m ) q = pp.xyz;
  else if( 3.0*pp.y < m ) q = pp.yzx;
  else if( 3.0*pp.z < m ) q = pp.zxy;
  else return m*0.57735027;

  float k = clamp(0.5*(q.z-q.y+s),0.0,s);
  return length(float3(q.x,q.y-s+k,q.z-k));
}

float distance_from_sphere(float3 p)
{
    return length(p);
}

float distance_from_sphere(float3 p, float3 c, float r)
{
    return length(p - c) - r;
}

float distance_from_cut_sphere( in float3 p, in float r, in float h )
{
  float w = sqrt(r*r-h*h); // constant for a given shape

  float2 q = float2( length(p.xz), p.y );

  float s = max( (h-r)*q.x*q.x+w*w*(h+r-2.0*q.y), h*q.x-w*q.y );

  return (s<0.0) ? length(q)-r :
    (q.x<w) ? h - q.y     :
    length(q-float2(w,h));
}

float distance_from_cut_hollow_sphere( float3 p, float r, float h, float t )
{
  float2 q = float2( length(p.xz), p.y );

  float w = sqrt(r*r-h*h);

  return ((h*q.x<w*q.y) ? length(q-float2(w,h)) : 
      abs(length(q)-r) ) - t;
}

float distance_from_box(float3 p, float3 b)
{
  float3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}

float distance_from_box_frame(float3 p, float3 b, float e)
{
  p = abs(p)-b;
  float3 q = abs(p+e)-e;

  return min(min(
        length(max(float3(p.x,q.y,q.z),0.0))+min(max(p.x,max(q.y,q.z)),0.0),
        length(max(float3(q.x,p.y,q.z),0.0))+min(max(q.x,max(p.y,q.z)),0.0)),
      length(max(float3(q.x,q.y,p.z),0.0))+min(max(q.x,max(q.y,p.z)),0.0));
}

float distance_from_pyramid(float3 p, float h, bool invert)
{
  float m2 = h*h + 0.25;

  // symmetry
  p.xz = abs(p.xz); // do p=abs(p) instead for double pyramid
  p.xz = (p.z>p.x) ? p.zx : p.xz;
  p.xz -= 0.5;

  // project into face plane (2D)
  float3 q = float3( p.z, h*p.y-0.5*p.x, h*p.x+0.5*p.y);

  float s = max(-q.x,0.0);
  float t = clamp( (q.y-0.5*q.x)/(m2+0.25), 0.0, 1.0 );

  float a = m2*(q.x+s)*(q.x+s) + q.y*q.y;
  float b = m2*(q.x+0.5*t)*(q.x+0.5*t) + (q.y-m2*t)*(q.y-m2*t);

  float d2 = max(-q.y,q.x*m2+q.y*0.5) < 0.0 ? 0.0 : min(a,b);

  // recover 3D and scale, and add sign
  return sqrt( (d2+q.z*q.z)/m2 ) * sign(max(q.z,-p.y));;
}

float distance_from_plane(float3 p, float3 n, float h)
{
  // n must be normalized
  return dot(p,n) + h;
}

float distance_from_torus( float3 p, float2 t )
{
  float2 q = float2(length(p.xz)-t.x,p.y);
  return length(q)-t.y;
}

float distance_from_capped_torus( float3 p, float2 sc, float ra, float rb)
{
  p.x = abs(p.x);
  float k = (sc.y*p.x>sc.x*p.y) ? dot(p.xy,sc) : length(p.xy);
  return sqrt( dot(p,p) + ra*ra - 2.0*ra*k ) - rb;
}

float3 op_rep(in float3 p, in float3 c)
{
  return glsl_mod(p+0.5*c,c)-0.5*c;
}

float smoothstep_cubic(float x)
{
  return x * x * (3.0 - 2.0 * x);
}

float smoothstep_quintic(float x)
{
  return x*x*x*(x*(x*6.0-15.0)+10.0);
}

// End licensed section

#endif  // __IQ_SDF_INC__

