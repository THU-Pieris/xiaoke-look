# -*- coding: utf-8 -*-
"""Compact flat-ink tracer for the backdrop.

usage: trace.py <in.png> <out.json> [--scale S] [--colors N] [--eps E] [--minarea A]
                [--crop x0,y0,x1,y1] (crop in source pixels, applied first)

Idea: the darkest ink (outline) is laid down as one silhouette of everything that
is not paper; every other ink is drawn on top as its own region.  The lines are
whatever the colour patches leave uncovered, so they never need tracing.
Paths are polygons in half-pixel integer units with relative 'l' commands.
"""
import argparse, json, os
import numpy as np
import cv2


def quantize(img, n, seed=1):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
    cv2.setRNGSeed(seed)
    _, labels, centers = cv2.kmeans(lab, n, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    rgb = cv2.cvtColor(centers.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    return labels.reshape(img.shape[:2]), rgb, centers


def mode_filter(labels, n, k=3, iters=1):
    for _ in range(iters):
        votes = np.stack([cv2.boxFilter((labels == c).astype(np.float32), -1, (k, k), normalize=False) for c in range(n)])
        labels = votes.argmax(0)
    return labels


def contours_of(mask, eps, minarea, U, protect=None):
    """Polygons (outer + holes) of a binary mask, in units of 1/U pixel.

    The mask is grown by half a pixel to close seams with its neighbours, but
    never into `protect` (the line-art pixels), so outlines stay visible."""
    m2 = cv2.resize(mask.astype(np.uint8), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    m2 = cv2.dilate(m2, np.ones((3, 3), np.uint8))
    if protect is not None:
        p2 = cv2.resize(protect.astype(np.uint8), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        m2 = m2 & (1 - p2)
        m2 = m2 | cv2.resize(mask.astype(np.uint8), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    cs, hier = cv2.findContours(m2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in cs:
        if abs(cv2.contourArea(c)) < minarea * 4:
            continue
        a = cv2.approxPolyDP(c, eps * 2, True)
        if len(a) < 3:
            continue
        pts = np.round(a.reshape(-1, 2).astype(np.float64) / 2 * U).astype(int)
        polys.append(pts)
    return polys


def poly_d(polys):
    s = []
    for pts in polys:
        x0, y0 = pts[0]
        seg = [f"M{x0} {y0}l"]
        prev = pts[0]
        nums = []
        for p in pts[1:]:
            dx, dy = p - prev
            if dx == 0 and dy == 0:
                continue
            nums.append(f"{dx}" if dx < 0 or not nums else f" {dx}")
            nums.append(f"{dy}" if dy < 0 else f" {dy}")
            prev = p
        body = "".join(nums).lstrip()
        seg.append(body)
        seg.append("z")
        s.append("".join(seg))
    return "".join(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=0.6)
    ap.add_argument("--colors", type=int, default=14)
    ap.add_argument("--eps", type=float, default=0.9)
    ap.add_argument("--minarea", type=float, default=4)
    ap.add_argument("--crop", default="")
    ap.add_argument("--units", type=int, default=2, help="coordinate units per (scaled) pixel")
    ap.add_argument("--paper", default="")
    ap.add_argument("--paper-de", type=float, default=9, help="Lab distance under which an ink counts as paper")
    ap.add_argument("--dark-thr", type=float, default=70)
    ap.add_argument("--line-drop", type=float, default=28)
    ap.add_argument("--line-max", type=float, default=150)
    ap.add_argument("--eps-big", type=float, default=0, help="eps for the silhouette layer")
    a = ap.parse_args()

    img = cv2.cvtColor(cv2.imread(a.inp, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    if a.crop:
        x0, y0, x1, y1 = map(int, a.crop.split(","))
        img = img[y0:y1, x0:x1]
    img = cv2.bilateralFilter(img, 5, 30, 5)
    img = cv2.resize(img, None, fx=a.scale, fy=a.scale, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    labels, cols, lab = quantize(img, a.colors)
    n = a.colors
    L = lab[:, 0]
    dark0 = int(np.argmin(L))
    # line art: pixels clearly darker than their surroundings, or simply dark
    Lp = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)[:, :, 0].astype(np.float32)
    local = cv2.GaussianBlur(Lp, (0, 0), 3)
    lines = (Lp < a.dark_thr) | ((Lp < local - a.line_drop) & (Lp < a.line_max))
    lines = cv2.morphologyEx(lines.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 1), np.uint8)).astype(bool)
    labels = np.where(lines, dark0, labels)
    keep = labels.copy()
    labels = mode_filter(labels, a.colors, 3, 1)
    labels = np.where(lines, dark0, labels)

    if a.paper:
        p = np.array([int(a.paper[i:i + 2], 16) for i in (1, 3, 5)])
        paper = int(np.argmin(((cols.astype(int) - p) ** 2).sum(1)))
    else:
        margin = np.concatenate([labels[:, : max(2, w // 12)].ravel(), labels[: max(2, h // 20), : w // 3].ravel()])
        paper = int(np.bincount(margin, minlength=n).argmax())
    dark = int(np.argmin(L))
    U = a.units

    layers = []
    # paper = paper-coloured pixels connected to the picture's edge; the same ink
    # inside the figure (skin, highlights) is drawn as a layer of its own.
    near = [c for c in range(n) if np.linalg.norm(lab[c].astype(float) - lab[paper].astype(float)) < a.paper_de]
    pm = np.isin(labels, near).astype(np.uint8)
    nlab, comp = cv2.connectedComponents(pm, connectivity=4)
    edge_ids = set(np.unique(np.concatenate([comp[0], comp[-1], comp[:, 0], comp[:, -1]]))) - {0}
    bg = np.isin(comp, list(edge_ids))
    # small enclosed paper pockets between locks of hair etc. count as background too
    for i in range(1, nlab):
        if i in edge_ids:
            continue
    darkmask = labels == dark
    # 1. silhouette of everything that is not background, in the outline colour
    sil = ~bg
    layers.append((dark, contours_of(sil, a.eps_big or a.eps, a.minarea, U)))
    # 2. every other ink, largest area first so small details land on top
    area = np.bincount(labels.ravel(), minlength=n)
    order = [c for c in np.argsort(-area) if c != dark]
    for c in order:
        m = (labels == c) & ~bg
        if not m.any():
            continue
        layers.append((int(c), contours_of(m, a.eps, a.minarea, U, protect=darkmask)))

    paths = []
    for c, polys in layers:
        if not polys:
            continue
        paths.append(["#%02x%02x%02x" % tuple(cols[c]), poly_d(polys)])
    total = sum(len(d) + len(f) + 20 for f, d in paths)
    W, H = w * U, h * U
    json.dump({"w": W, "h": H, "paper": "#%02x%02x%02x" % tuple(cols[paper]), "paths": paths},
              open(a.out, "w"), separators=(",", ":"))
    prev = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#%02x%02x%02x"/>' % tuple(cols[paper])]
    prev += [f'<path fill="{f}" d="{d}"/>' for f, d in paths]
    prev.append("</svg>")
    base = os.path.splitext(a.out)[0]
    open(base + "_preview.svg", "w").write("".join(prev))
    q = cols[labels].astype(np.uint8)
    cv2.imwrite(base + "_quant.png", cv2.cvtColor(q, cv2.COLOR_RGB2BGR))
    print(f"{w}x{h} units {U} paper {paths and '#%02x%02x%02x' % tuple(cols[paper])} dark {'#%02x%02x%02x' % tuple(cols[dark])} "
          f"paths {len(paths)} polys {sum(len(p) for _, p in layers)} chars~{total}")


if __name__ == "__main__":
    main()
