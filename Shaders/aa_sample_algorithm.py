#!/usr/bin/env python3

# This is the algorithm that the anti-aliasing logic inside
# TaSTT_lighting_template.cginc uses.

from math import fmod

x = .5
y = .1
aa = 10

# This lets us handle values smaller than 1. We're creating an m*n rectangle
# and walking a path left-to-right, top-to-bottom through it.
x_cap = max(x, 1.0 / x)
y_cap = max(y, 1.0 / y)

print(f"{x_cap} {y_cap}")

def lerp(lo, hi, fract):
    return lo + (hi - lo) * fract

for i in range(0, aa):
    # We want to subdivide an x*y area into `aa` evenly spaced pieces.
    region = x_cap * y_cap

    stride = region / aa

    region_i = i * stride + stride/2
    region_x = region_i / y_cap
    region_y = fmod(region_i, y_cap)

    print(f"{region_x} {region_y}")

    region_x = lerp(0, x, region_x / x_cap)
    region_y = lerp(0, y, region_y / y_cap)

    print(f"{region_x} {region_y}")

    assert(region_x >= 0)
    assert(region_x <= x)
    assert(region_y >= 0)
    assert(region_y <= y)

