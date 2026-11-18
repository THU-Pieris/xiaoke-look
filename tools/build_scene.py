# -*- coding: utf-8 -*-
"""Wrap traced paths into a backdrop SVG and write it as a TS module.

usage: build_scene.py <paths.json> <out_scene.ts> [--preview wide.svg]
                      [--fx afternoon|night|code|rain|snow] [--fade-left .42] [--fade-bottom .58]

Layout: the picture is pinned to the top right and fitted to the window height
(xMaxYMin meet); the rest of the window is bare paper. The picture fades into
that paper towards the left and the bottom through two gradient masks.

Effects: each scene gets a few kinds of slow particles and small decorations in
the blank part. Shapes are defined once in <defs> and placed with <use>. Every
moving part has a resting place and opacity in the plain markup, so the scene
reads finished when motion is reduced or stripped.
"""
import argparse, json, random

ap = argparse.ArgumentParser()
ap.add_argument("paths")
ap.add_argument("out")
ap.add_argument("--preview", default="")
ap.add_argument("--fx", default="afternoon")
ap.add_argument("--fade-left", type=float, default=0.42)
ap.add_argument("--fade-bottom", type=float, default=0.58)
ap.add_argument("--seed", type=int, default=7)
a = ap.parse_args()

d = json.load(open(a.paths))
W, H, paper = d["w"], d["h"], d["paper"]
body = "".join(f'<path fill="{f}" d="{p}"/>' for f, p in d["paths"])
rnd = random.Random(a.seed)

# ---- shape library (ids are short to save characters) ----
SHAPES = {
    "pe": '<g id="pe"><path fill="#ef7e42" d="M0 0c14-10 34-8 44 4c-12 12-32 12-44-4z"/><path fill="#ac4c27" d="M4 2c12 2 26 2 36 2c-12 4-26 2-36-2z"/></g>',
    "bl": '<g id="bl"><circle r="12" fill="#ef7e42"/>'
          + "".join(f'<ellipse rx="6" ry="16" cy="-20" fill="#f29e59" transform="rotate({k * 36})"/>' for k in range(10))
          + '<circle r="7" fill="#c8561f"/></g>',
    "lf": '<path id="lf" fill="#8f9a6c" d="M0 0c10-18 30-22 44-16c-8 16-26 24-44 16z"/>',
    "st": '<path id="st" d="M0-18L4-4L18 0L4 4L0 18L-4 4L-18 0L-4-4z"/>',
    "dot": '<circle id="dot" r="5"/>',
    "sh": '<g id="sh"><path stroke="url(#shg)" stroke-width="4" stroke-linecap="round" d="M0 0L220-110"/><circle r="4" fill="#fff6d8"/></g>',
    "lb": '<path id="lb" fill="none" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" d="M14-18L0 0L14 18"/>',
    "rb": '<path id="rb" fill="none" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" d="M0-18L14 0L0 18"/>',
    "cb": '<path id="cb" fill="none" stroke-width="5" stroke-linecap="round" d="M14-22c-8 0-8 4-8 10s-2 10-8 12c6 2 8 6 8 12s0 10 8 10"/>',
    "sl": '<path id="sl" fill="none" stroke-width="5" stroke-linecap="round" d="M8-18L-8 18"/>',
    "sq": '<rect id="sq" x="-5" y="-5" width="10" height="10"/>',
    "cu": '<rect id="cu" x="-6" y="-22" width="12" height="44" rx="2"/>',
    "rn": '<path id="rn" stroke-width="3" stroke-linecap="round" d="M0 0l-16 80"/>',
    "rp": '<ellipse id="rp" rx="40" ry="10" fill="none" stroke-width="3"/>',
    "fl": '<circle id="fl" r="8" fill="#fff" stroke-width="2"/>',
    "cr": '<g id="cr" fill="none" stroke-width="3" stroke-linecap="round">'
          + "".join(f'<path transform="rotate({k * 60})" d="M0 0V-22M0-12l-6-6M0-12l6-6"/>' for k in range(6)) + "</g>",
    "ht": '<path id="ht" d="M0 6c-14-10-20-16-20-24c0-8 10-12 20-2c10-10 20-6 20 2c0 8-6 14-20 24z"/>',
}

ANIM = {
    # name: keyframes body
    "drift": "0%{transform:translate(0,-160px) rotate(0deg);opacity:0}12%{opacity:.85}80%{opacity:.85}100%{transform:translate(-220px,520px) rotate(200deg);opacity:0}",
    "mote": "0%{transform:translate(0,40px);opacity:0}20%{opacity:.7}80%{opacity:.7}100%{transform:translate(70px,-180px);opacity:0}",
    "tw": "0%{opacity:.2}50%{opacity:.9}100%{opacity:.2}",
    "shoot": "0%{transform:translate(0,0);opacity:0}2%{opacity:.95}9%{transform:translate(-520px,260px);opacity:0}100%{transform:translate(-520px,260px);opacity:0}",
    "rise": "0%{transform:translate(0,60px);opacity:0}15%{opacity:.6}85%{opacity:.6}100%{transform:translate(20px,-260px);opacity:0}",
    "blink": "0%{opacity:.15}50%{opacity:.75}100%{opacity:.15}",
    # rain: travels along its own streak (dx/dy = -16/80 = -0.2), so the line and its motion agree
    "fall": "0%{transform:translate(100px,-500px);opacity:0}10%{opacity:.55}90%{opacity:.55}100%{transform:translate(-100px,500px);opacity:0}",
    "ripple": "0%{transform:scale(.2);opacity:.7}100%{transform:scale(1.6);opacity:0}",
    "snow": "0%{transform:translate(0,-260px);opacity:0}10%{opacity:.95}50%{transform:translate(46px,0)}90%{opacity:.95}100%{transform:translate(-24px,300px);opacity:0}",
    "spin": "0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}",
    "bob": "0%{transform:translate(0,0) rotate(-6deg)}50%{transform:translate(0,-18px) rotate(6deg)}100%{transform:translate(0,0) rotate(-6deg)}",
}

used_shapes, used_anims, items = set(), set(), []
# The picture is ~2300 units tall and drawn at window height (~1000 px), so one
# unit is under half a pixel: shapes are drawn in "screen-ish" sizes times this.
SCALE = 2.4


def place(shape, n, area, anim, dur, rest_op, fill=None, stroke=None, scale=(1, 1), rot=(0, 0), spin=None):
    """n copies of a shape at random spots of area (x0, y0, x1, y1), each with its own timing."""
    used_shapes.add(shape)
    used_anims.add(anim)
    if spin:
        used_anims.add("spin")
    for _ in range(n):
        x, y = rnd.randint(area[0], area[2]), rnd.randint(area[1], area[3])
        s = rnd.uniform(*scale) * SCALE
        r = rnd.randint(*rot)
        du = rnd.uniform(*dur)
        de = -rnd.uniform(0, du)
        paint = (f' fill="{fill}"' if fill else "") + (f' stroke="{stroke}"' if stroke else "")
        inner = f'<use href="#{shape}"{paint}/>'
        if spin:
            inner = f'<g class="sp" style="animation-duration:{rnd.uniform(*spin):.0f}s">{inner}</g>'
        items.append(
            f'<g transform="translate({x} {y}) rotate({r}) scale({s:.2f})">'
            f'<g class="{anim}" style="animation-duration:{du:.1f}s;animation-delay:{de:.1f}s;opacity:{rest_op}">{inner}</g></g>'
        )


L = (-1700, -60, 250, 1900)          # blank part left of the picture (picture x runs 0..W)
LB = (-1700, 1300, W - 200, 2250)     # lower band, where the picture has faded
fx = a.fx
if fx == "afternoon":
    place("pe", 16, L, "drift", (40, 70), .85, scale=(.8, 1.4), rot=(-60, 60))
    place("pe", 5, LB, "drift", (50, 70), .85, scale=(.7, 1.1), rot=(-60, 60))
    place("dot", 18, (-1500, 100, 700, 1600), "mote", (30, 55), .55, fill="#f6d78a", scale=(.5, 1.1))
    place("bl", 4, (-1500, 200, -200, 1700), "drift", (80, 110), .85, scale=(.6, .9), spin=(20, 40))
    place("lf", 6, (-1600, 300, -100, 1900), "drift", (70, 100), .75, scale=(.7, 1.1), rot=(-40, 40))
    place("bl", 2, (-1650, 1700, -900, 2100), "bob", (7, 10), .9, scale=(.9, 1.1))
elif fx == "night":
    place("st", 30, (-1750, 40, 300, 1300), "tw", (7, 16), .6, fill="#eadba6", scale=(.3, .8))
    place("st", 5, (-1600, 80, -300, 900), "tw", (9, 14), .8, fill="#f6e7b4", scale=(1.0, 1.3))
    place("dot", 16, (-1750, 60, 300, 1400), "tw", (5, 11), .5, fill="#c9c4e8", scale=(.3, .6))
    place("sh", 4, (-700, 60, 500, 600), "shoot", (22, 38), 0, scale=(.8, 1.1))
    place("dot", 16, (-500, 900, 900, 2000), "mote", (30, 50), .55, fill="#f2c66d", scale=(.4, .9))
elif fx == "code":
    place("dot", 18, (-1500, 100, 700, 1900), "mote", (30, 55), .5, fill="#8fb6d9", scale=(.4, .8))
    for sh in ("lb", "rb", "cb", "sl"):
        place(sh, 4, (-1650, 200, 0, 2100), "rise", (38, 60), .55, stroke="#6f9cc4", scale=(.7, 1.1), rot=(-15, 15))
    place("sq", 14, (-1750, 100, 200, 2100), "tw", (6, 14), .45, fill="#e8874a", scale=(.4, .8))
    place("cu", 2, (-1300, 500, -400, 1500), "blink", (2.6, 3.4), .6, fill="#8fb6d9", scale=(.8, 1.0))
    place("ht", 3, (-1400, 600, -200, 2000), "rise", (45, 65), .6, fill="#e8874a", scale=(.5, .8))
elif fx == "rain":
    place("rn", 56, (-1850, -200, 500, 2050), "fall", (0.9, 1.5), .4, stroke="#7f92a6", scale=(.5, .9))
    place("rp", 12, (-1750, 1700, 600, 2280), "ripple", (3.5, 6), .35, stroke="#8a9cb0", scale=(.6, 1.1))
    place("dot", 12, (-1500, 300, 300, 1700), "mote", (40, 60), .35, fill="#b9c6d4", scale=(.6, 1.2))
elif fx == "snow":
    place("fl", 56, (-1850, -60, 600, 2050), "snow", (22, 42), .9, stroke="#b7c4d3", scale=(.3, .9))
    place("cr", 10, (-1750, 0, 300, 1900), "snow", (36, 60), .8, stroke="#9fb1c5", scale=(.7, 1.2), spin=(18, 36))
    place("dot", 12, (-1650, 100, 600, 1900), "tw", (6, 12), .7, fill="#ffffff", scale=(.4, .9))
css = ["".join(f"@keyframes {k}{{{ANIM[k]}}}" for k in sorted(used_anims))]
css += [f".{k}{{animation:{k} 30s {'linear' if k in ('drift','mote','fall','snow','spin','rise','shoot') else 'ease-in-out'} infinite}}" for k in sorted(used_anims) if k != "spin"]
if "spin" in used_anims:
    css.append(".sp{animation:spin 30s linear infinite;transform-box:fill-box;transform-origin:center}")
if "ripple" in used_anims:
    css.append(".ripple{transform-box:fill-box;transform-origin:center}")
css.append("@media (prefers-reduced-motion: reduce){.drift,.mote,.tw,.shoot,.rise,.blink,.fall,.ripple,.snow,.sp,.bob{animation:none}}")

fl, fb = a.fade_left, a.fade_bottom
shapes = "".join(SHAPES[s] for s in sorted(used_shapes))
grad = ('<linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6d8" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#fff6d8"/></linearGradient>') if "sh" in used_shapes else ""
# The root has no viewBox, so its units are CSS pixels of the backdrop box. The
# picture lives in a nested viewport whose x is the right inset (0 here; the mod
# writes -N there to keep the picture clear of a side panel N px wide).
svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">'
    f"<style>{''.join(css)}</style>"
    f'<rect width="100%" height="100%" fill="{paper}"/>'
    f'<svg class="pic" x="0" y="0" width="100%" height="100%" viewBox="0 0 {W} {H}" preserveAspectRatio="xMaxYMin meet" overflow="visible">'
    "<defs>"
    '<linearGradient id="fx" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="#000"/><stop offset="{fl * 0.24:.2f}" stop-color="#000"/>'
    f'<stop offset="{fl * 0.62:.2f}" stop-color="#555"/><stop offset="{fl:.2f}" stop-color="#fff"/></linearGradient>'
    '<linearGradient id="fy" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="{fb:.2f}" stop-color="#fff"/><stop offset="{min(.95, fb + .2):.2f}" stop-color="#777"/>'
    f'<stop offset="{min(.99, fb + .38):.2f}" stop-color="#000"/></linearGradient>'
    f"{grad}"
    f'<mask id="mx" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fx)"/></mask>'
    f'<mask id="my" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fy)"/></mask>'
    f"{shapes}</defs>"
    f'<g mask="url(#mx)"><g mask="url(#my)">{body}</g></g>'
    f'<g>{"".join(items)}</g>'
    "</svg></svg>"
)
assert svg.count('<svg class="pic" x="0" ') == 1
assert "\\" not in svg and "&" not in svg and "<!" not in svg
print(f"{fx}: svg chars {len(svg)} (fx {len(svg) - len(body)})", "OK" if len(svg) <= 131072 else "TOO BIG")
open(a.out, "w", encoding="utf8").write(
    "// Generated by tools/build_scene.py from the traced illustration. Do not edit by hand.\n"
    f"export const PAPER = {json.dumps(paper)}\n"
    f"export const SCENE = {json.dumps(svg)}\n"
)
if a.preview:
    wide = svg.replace('width="100%" height="100%">', 'width="1600" height="1000">', 1)
    open(a.preview, "w", encoding="utf8").write(wide)
