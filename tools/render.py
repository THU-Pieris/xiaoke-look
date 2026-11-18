# -*- coding: utf-8 -*-
"""Rasterize an SVG file to PNG.  usage: render.py <in.svg> <out.png> [width]"""
import sys
import resvg_py

src = open(sys.argv[1], encoding="utf8").read()
w = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
data = resvg_py.svg_to_bytes(svg_string=src, width=w)
open(sys.argv[2], "wb").write(bytes(data))
print("ok", sys.argv[2])
