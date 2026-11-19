# -*- coding: utf-8 -*-
"""Wrap traced paths into a backdrop SVG and write it as a TS module.

usage: build_scene.py <paths.json> <out_scene.ts> [--preview wide.svg]
                      [--fx <look id>] [--side right|left] [--face x,y] [--fade-left .42] [--fade-bottom .58]

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
ap.add_argument("--side", choices=("right", "left"), default="right",
                help="edge the picture is pinned to; the fade runs toward the other side")
ap.add_argument("--face", default="0.5,0.2", help="face centre as fractions of the picture: x,y")
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
    # cherry petal with its notch, and a five-petal blossom
    "sk": '<path id="sk" d="M0 0c-10-8-12-22-4-30l4 6l4-6c8 8 6 22-4 30z"/>',
    "sb": '<g id="sb">' + "".join(f'<path fill="#f4c3cf" transform="rotate({k * 72})" d="M0 0c-9-6-11-18-4-24l4 5l4-5c7 6 5 18-4 24z"/>' for k in range(5))
          + '<circle r="4" fill="#d9788f"/></g>',
    # firework burst: a ring of short strokes
    "fw": '<g id="fw" fill="none" stroke-width="4" stroke-linecap="round">'
          + "".join(f'<path transform="rotate({k * 22.5})" d="M0-26V-46"/>' for k in range(16)) + "</g>",
    "ln": '<g id="ln"><path stroke="#3a3346" stroke-width="2" d="M0-30V-18"/><rect x="-12" y="-18" width="24" height="32" rx="10" fill="#e8743c"/>'
          '<rect x="-12" y="-6" width="24" height="4" fill="#c4512a"/><rect x="-6" y="14" width="12" height="4" fill="#3a3346"/></g>',
    # maple leaf
    "mp": '<path id="mp" d="M0 22V8L-18 14L-12 2L-26-6L-14-8L-18-22L-6-14L0-28L6-14L18-22L14-8L26-6L12 2L18 14L0 8z"/>',
    # round tree ornament
    "or": '<g id="or"><path stroke="#c9a45a" stroke-width="2" fill="none" d="M0-34V-16"/><rect x="-4" y="-18" width="8" height="5" fill="#c9a45a"/>'
          '<circle r="13" cy="0"/><path fill="#fff" opacity=".55" d="M-6-6a7 7 0 0 1 6-4v3a4 4 0 0 0-3 2z"/></g>',
    # a gull in flight, and steam curls, coffee bean, question mark
    "bd": '<path id="bd" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" d="M-18 2c4-8 12-10 18 0c6-10 14-8 18 0"/>',
    "sm": '<path id="sm" fill="none" stroke-width="4" stroke-linecap="round" d="M0 40c-10-10 10-20 0-30s10-20 0-30"/>',
    "bn": '<g id="bn"><ellipse rx="10" ry="14" fill="#6b4630"/><path fill="none" stroke="#3f281b" stroke-width="2.5" d="M0-12c-5 6 5 18 0 24"/></g>',
    "qm": '<path id="qm" fill="none" stroke-width="5" stroke-linecap="round" d="M-9-12c0-10 18-10 18 0c0 8-9 8-9 16M0 15v1"/>',
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
    # a firework opens, hangs, fades; then stays dark for the rest of its period
    "burst": "0%{transform:scale(.15);opacity:0}4%{opacity:.95}18%{transform:scale(1);opacity:.85}34%{transform:scale(1.08);opacity:0}100%{transform:scale(1.08);opacity:0}",
    "fly": "0%{transform:translate(0,0);opacity:0}8%{opacity:.8}85%{opacity:.8}100%{transform:translate(-1100px,-160px);opacity:0}",
    "steam": "0%{transform:translate(0,40px) scale(.7);opacity:0}25%{opacity:.5}75%{opacity:.4}100%{transform:translate(14px,-200px) scale(1.2);opacity:0}",
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
        if a.side == "left":
            x = W - x  # the blank part is on the right
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
elif fx == "spring":
    for c in ("#f4c3cf", "#eaa2b4", "#f8dbe2"):
        place("sk", 12, L, "drift", (34, 60), .85, fill=c, scale=(.6, 1.1), rot=(-90, 90), spin=(16, 30))
    place("sk", 8, LB, "drift", (40, 66), .8, fill="#f4c3cf", scale=(.6, 1.0), rot=(-90, 90))
    place("sb", 4, (-1500, 300, -200, 1800), "drift", (80, 110), .85, scale=(.7, 1.0), spin=(24, 40))
    place("dot", 14, (-1500, 100, 700, 1700), "mote", (30, 55), .5, fill="#f7e3a8", scale=(.4, .9))
elif fx == "festival":
    for c in ("#f2c65c", "#f08a54", "#f4efe4"):
        place("fw", 2, (-1600, 60, -100, 800), "burst", (9, 15), 0, stroke=c, scale=(1.6, 2.6), rot=(0, 20))
    place("dot", 22, (-1700, 500, 500, 2100), "tw", (3, 7), .6, fill="#d8f08a", scale=(.4, .8))
    place("dot", 14, (-1500, 900, 300, 2100), "mote", (24, 40), .6, fill="#c8e86f", scale=(.4, .7))
    place("st", 18, (-1750, 40, 200, 900), "tw", (7, 16), .5, fill="#e7dcb0", scale=(.25, .6))
    place("ln", 4, (-1600, 1650, -500, 1950), "bob", (6, 9), .9, scale=(.9, 1.1))
elif fx == "autumn":
    for c in ("#c8452d", "#e07a2e", "#d9a13a", "#a8452a"):
        place("mp", 7, L, "drift", (38, 64), .85, fill=c, scale=(.6, 1.1), rot=(-90, 90), spin=(14, 26))
    place("mp", 6, LB, "drift", (44, 70), .8, fill="#c8452d", scale=(.6, 1.0), rot=(-90, 90))
    place("dot", 12, (-1500, 100, 700, 1700), "mote", (30, 55), .45, fill="#f1cf8a", scale=(.4, .9))
elif fx == "holiday":
    place("fl", 40, (-1850, -60, 600, 2050), "snow", (22, 42), .85, stroke="#8a7d8c", scale=(.3, .8))
    place("st", 16, (-1750, 60, 200, 1700), "tw", (5, 11), .75, fill="#f2c65c", scale=(.3, .8))
    place("dot", 18, (-1750, 60, 500, 2000), "tw", (3, 8), .6, fill="#f6d27a", scale=(.4, .8))
    for c in ("#d23a3a", "#e8874a", "#c9a45a", "#3f7a55"):
        place("or", 1, (-1550, 1650, -400, 1950), "bob", (6, 10), .95, fill=c, scale=(1.0, 1.3))
elif fx == "morning":
    place("dot", 26, (-1500, 100, 700, 1800), "mote", (30, 55), .55, fill="#f3d58a", scale=(.4, 1.0))
    place("bd", 5, (-600, 150, 400, 900), "fly", (40, 70), .7, stroke="#8a9bb0", scale=(.7, 1.1), rot=(-8, 8))
    place("lf", 5, (-1600, 300, -100, 1900), "drift", (70, 100), .7, scale=(.6, 1.0), rot=(-40, 40))
    place("sm", 3, (-1300, 1400, -500, 1900), "steam", (8, 12), .3, stroke="#c7b8a6", scale=(.8, 1.2))
elif fx == "dusk":
    place("bd", 7, (-500, 100, 500, 1000), "fly", (40, 70), .7, stroke="#5a3b52", scale=(.6, 1.1), rot=(-8, 8))
    place("dot", 18, (-1500, 100, 700, 1800), "mote", (30, 55), .5, fill="#f3b27a", scale=(.4, .9))
    place("st", 4, (-1600, 60, -400, 600), "tw", (8, 14), .7, fill="#fbe7c2", scale=(.4, .7))
    place("pe", 8, L, "drift", (40, 70), .8, scale=(.6, 1.0), rot=(-60, 60))
elif fx == "cafe":
    place("sm", 8, (-1500, 900, 0, 2000), "steam", (8, 14), .3, stroke="#b9a088", scale=(.8, 1.4))
    place("bn", 10, (-1650, 0, 100, 1900), "drift", (60, 95), .85, scale=(.6, 1.0), rot=(-90, 90), spin=(20, 40))
    place("ht", 4, (-1400, 700, -200, 2000), "rise", (45, 65), .5, fill="#d9a07a", scale=(.4, .7))
    place("dot", 14, (-1500, 100, 700, 1700), "mote", (30, 55), .45, fill="#e8cfa0", scale=(.4, .9))
elif fx == "detective":
    place("qm", 7, (-1650, 200, 0, 2100), "rise", (40, 62), .55, stroke="#c9b27a", scale=(.8, 1.3), rot=(-15, 15))
    for sh in ("lb", "rb", "cb"):
        place(sh, 3, (-1650, 200, 0, 2100), "rise", (38, 60), .45, stroke="#6f9a7e", scale=(.7, 1.0), rot=(-15, 15))
    place("dot", 20, (-1500, 100, 700, 1900), "mote", (30, 55), .5, fill="#e9d28f", scale=(.4, .8))
    place("sq", 10, (-1750, 100, 200, 2100), "tw", (6, 14), .4, fill="#c8452d", scale=(.4, .7))
    place("cu", 1, (-1100, 900, -600, 1300), "blink", (2.6, 3.4), .6, fill="#6f9a7e", scale=(.8, 1.0))
css =["".join(f"@keyframes {k}{{{ANIM[k]}}}" for k in sorted(used_anims))]
css += [f".{k}{{animation:{k} 30s {'linear' if k in ('drift','mote','fall','snow','spin','rise','shoot','fly') else 'ease-out' if k in ('burst','steam') else 'ease-in-out'} infinite}}" for k in sorted(used_anims) if k != "spin"]
if "spin" in used_anims:
    css.append(".sp{animation:spin 30s linear infinite;transform-box:fill-box;transform-origin:center}")
for k in ("ripple", "burst"):
    if k in used_anims:
        css.append(f".{k}{{transform-box:fill-box;transform-origin:center}}")
css.append("@media (prefers-reduced-motion: reduce){.drift,.mote,.tw,.shoot,.rise,.blink,.fall,.ripple,.snow,.sp,.bob,.burst,.fly,.steam{animation:none}}")

fl, fb = a.fade_left, a.fade_bottom
if a.side == "right":
    fade_x = ('<linearGradient id="fx" x1="0" y1="0" x2="1" y2="0">'
              f'<stop offset="0" stop-color="#000"/><stop offset="{fl * 0.24:.2f}" stop-color="#000"/>'
              f'<stop offset="{fl * 0.62:.2f}" stop-color="#555"/><stop offset="{fl:.2f}" stop-color="#fff"/></linearGradient>')
else:
    # pinned left: fades out toward the right, and a little at its own left edge
    fade_x = ('<linearGradient id="fx" x1="0" y1="0" x2="1" y2="0">'
              '<stop offset="0" stop-color="#000"/><stop offset="0.06" stop-color="#fff"/>'
              f'<stop offset="{1 - fl:.2f}" stop-color="#fff"/><stop offset="{1 - fl * 0.62:.2f}" stop-color="#555"/>'
              f'<stop offset="{1 - fl * 0.24:.2f}" stop-color="#000"/><stop offset="1" stop-color="#000"/></linearGradient>')
face_x, face_y = (float(v) for v in a.face.split(","))
shapes = "".join(SHAPES[s] for s in sorted(used_shapes))
grad = ('<linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6d8" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#fff6d8"/></linearGradient>') if "sh" in used_shapes else ""
# The root has no viewBox, so its units are CSS pixels of the backdrop box. The
# picture lives in a nested viewport pinned to one edge, inside <g class="mv">:
# the mod gives that group a translateX worked out from the window size (vw, vh)
# and the side panels, so the face lands in the gap beside the conversation.
svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">'
    f"<style>{''.join(css)}</style>"
    f'<rect width="100%" height="100%" fill="{paper}"/>'
    '<g class="mv">'
    f'<svg class="pic" x="0" y="0" width="100%" height="100%" viewBox="0 0 {W} {H}" preserveAspectRatio="{'xMinYMin' if a.side == 'left' else 'xMaxYMin'} meet" overflow="visible">'
    "<defs>"
    f"{fade_x}"
    '<linearGradient id="fy" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="{fb:.2f}" stop-color="#fff"/><stop offset="{min(.95, fb + .2):.2f}" stop-color="#777"/>'
    f'<stop offset="{min(.99, fb + .38):.2f}" stop-color="#000"/></linearGradient>'
    f"{grad}"
    f'<mask id="mx" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fx)"/></mask>'
    f'<mask id="my" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fy)"/></mask>'
    f"{shapes}</defs>"
    f'<g mask="url(#mx)"><g mask="url(#my)">{body}</g></g>'
    f'<g>{"".join(items)}</g>'
    "</svg></g></svg>"
)
assert svg.count('<svg class="pic" x="0" ') == 1
assert "\\" not in svg and "&" not in svg and "<!" not in svg
print(f"{fx}: svg chars {len(svg)} (fx {len(svg) - len(body)})", "OK" if len(svg) <= 131072 else "TOO BIG")
open(a.out, "w", encoding="utf8").write(
    "// Generated by tools/build_scene.py from the traced illustration. Do not edit by hand.\n"
    f"export const PAPER = {json.dumps(paper)}\n"
    f"export const SCENE = {json.dumps(svg)}\n"
    f"export const SIDE = {json.dumps(a.side)}\n"
    "// Face centre as fractions of the picture, and the picture's height over its width.\n"
    f"export const FACE = {{ x: {face_x}, y: {face_y} }}\n"
    f"export const ASPECT = {H / W:.4f}\n"
)
if a.preview:
    wide = svg.replace('width="100%" height="100%">', 'width="1600" height="1000">', 1)
    open(a.preview, "w", encoding="utf8").write(wide)
