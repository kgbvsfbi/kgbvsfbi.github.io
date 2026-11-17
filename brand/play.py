"""Play 개발자 페이지 자료 — 개발자 아이콘 512×512, 헤더 4096×2304.

build.py가 부른다. 도형·색·글꼴은 전부 build.py의 값을 쓰고, 여기에는 배치만 있다.
SVG 렌더러 없이 Pillow로 직접 그린다: 도형을 다각형으로 펴서 크게 그린 뒤 줄여
가장자리를 부드럽게 하고, 채우기는 nonzero 규칙(글꼴과 같은 규칙)을 따른다.

규격(Play Console): PNG 24비트(알파 없음), 1 MB 이하.
"""

import math
import os

import numpy as np
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw

import build

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "play")

ICON = 512
HEADER = (4096, 2304)
# 고른 배치 — HEADER_LAYOUTS / ICON_THEMES의 키
HEADER_LAYOUT = "center"
HEADER_THEME = "light"
ICON_THEME = "light"


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """a에서 b 쪽으로 t만큼 섞은 색 — 반투명 대신 바탕과 섞은 단색을 쓴다(알파 없음)."""
    A, B = hex_rgb(a), hex_rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


# ---- 도형 → 다각형 -------------------------------------------------------


def rrect(x, y, w, h, r, rot=0.0, steps=12):
    """둥근 사각형 윤곽 하나. rot(도)는 사각형 가운데를 축으로 돈다."""
    pts = []
    corners = [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)]
    for cx, cy, a0 in corners:
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    if rot:
        ox, oy = x + w / 2, y + h / 2
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = [(ox + (px - ox) * c - (py - oy) * s, oy + (px - ox) * s + (py - oy) * c) for px, py in pts]
    return pts


def mark_shapes(ox, oy, scale, ink, accent, dot=None):
    """마크를 (윤곽들, 색) 목록으로. (ox, oy)는 100×100 상자의 왼쪽 위."""
    s, d = build.STEM, build.DOT
    if dot is None:
        dot = (d["x"], d["y"], d["rot"])
    dx, dy, rot = dot

    def T(v):
        return v * scale

    stem = rrect(ox + T(s["x"]), oy + T(s["y"]), T(s["w"]), T(s["h"]), T(s["r"]))
    dotp = rrect(ox + T(dx), oy + T(dy), T(d["s"]), T(d["s"]), T(d["r"]), rot)
    return [([stem], ink), ([dotp], accent)]


class FlattenPen(BasePen):
    """글리프 윤곽을 꺾은선으로 편다."""

    def __init__(self, glyphset, tf, steps=10):
        super().__init__(glyphset)
        self.tf, self.steps, self.contours, self.cur = tf, steps, [], None

    def _moveTo(self, p):
        self.cur = [self.tf(p)]
        self.contours.append(self.cur)

    def _lineTo(self, p):
        self.cur.append(self.tf(p))

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, self.steps + 1):
            t = i / self.steps
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
            self.cur.append(self.tf((x, y)))

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for i in range(1, self.steps + 1):
            t = i / self.steps
            m = 1 - t
            x = m**3 * p0[0] + 3 * m * m * t * p1[0] + 3 * m * t * t * p2[0] + t**3 * p3[0]
            y = m**3 * p0[1] + 3 * m * m * t * p1[1] + 3 * m * t * t * p2[1] + t**3 * p3[1]
            self.cur.append(self.tf((x, y)))

    def _closePath(self):
        pass


def wordmark_shapes(font, x0, baseline, px_per_unit, ink, accent):
    """워드마크를 (윤곽들, 색) 목록으로. build.wordmark_paths와 같은 배치 규칙을 쓴다."""
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    upm = font["head"].unitsPerEm
    track = build.TRACKING * upm
    first_i = build.TEXT.index("i")
    x = 0.0
    letters = []
    dot = None
    for idx, ch in enumerate(build.TEXT):
        name = "dotlessi" if idx == first_i else cmap[ord(ch)]

        def tf(p, x=x):
            return (x0 + (x + p[0]) * px_per_unit, baseline - p[1] * px_per_unit)

        pen = FlattenPen(gs, tf)
        gs[name].draw(pen)
        letters += [c for c in pen.contours if len(c) > 2]
        if idx == first_i:
            dot = build.wordmark_dot(gs, name, x)
        x += hmtx[name][0] + (track if idx < len(build.TEXT) - 1 else 0)
    cx, cy, size, r = dot
    P = px_per_unit
    dotp = rrect(x0 + (cx - size / 2) * P, baseline + (cy - size / 2) * P, size * P, size * P, r * P, build.DOT["rot"])
    return [(letters, ink), ([dotp], accent)], x * px_per_unit


# ---- 래스터 --------------------------------------------------------------


def render(size, bg, shapes, ss=3):
    """shapes = [(윤곽 목록, 색)] → RGB 이미지. 크게(ss배) 그려 줄인다."""
    W, H = size
    canvas = Image.new("RGB", size, bg)
    for contours, color in shapes:
        wind = np.zeros((H * ss, W * ss), dtype=np.int16)
        for c in contours:
            area = sum(c[i][0] * c[i - 1][1] - c[i - 1][0] * c[i][1] for i in range(len(c)))
            m = Image.new("L", (W * ss, H * ss), 0)
            ImageDraw.Draw(m).polygon([(px * ss, py * ss) for px, py in c], fill=1)
            wind += np.asarray(m, dtype=np.int16) * (1 if area > 0 else -1)
        full = Image.fromarray(((wind != 0) * 255).astype(np.uint8), "L")
        alpha = full.resize(size, Image.BOX)
        canvas.paste(Image.new("RGB", size, color), (0, 0), alpha)
    return canvas


# ---- 배치 ----------------------------------------------------------------

# 마크가 실제로 차지하는 범위(100 단위) — 가운데 맞춤에 쓴다.
def mark_box():
    s, d = build.STEM, build.DOT
    half = d["s"] / 2 * (abs(math.cos(math.radians(d["rot"]))) + abs(math.sin(math.radians(d["rot"]))))
    cx, cy = d["x"] + d["s"] / 2, d["y"] + d["s"] / 2
    return s["x"], cy - half, cx + half, s["y"] + s["h"]  # 왼, 위, 오른, 아래


def centered_mark(cx, cy, height, p, dot=None):
    l, t, r, b = mark_box()
    scale = height / (b - t)
    ox = cx - (l + r) / 2 * scale
    oy = cy - (t + b) / 2 * scale
    return mark_shapes(ox, oy, scale, p["ink"], p["accent"], dot), (ox, oy, scale)


def icon(theme):
    p = build.PALETTE[theme]
    # 원형 마스크에도 안전하게 — 마크 높이를 지름의 58%로
    shapes, _ = centered_mark(ICON / 2, ICON / 2, ICON * 0.58, p)
    return render((ICON, ICON), p["bg"], shapes, ss=4)


def header_center(p, font):
    W, H = HEADER
    shapes, _ = centered_mark(W / 2, H / 2, 1000, p)
    return shapes


def header_hop(p, font):
    """점이 왼쪽 아래에서 통통 뛰어와 제자리에 앉는 궤적 — 작은 점선 하나."""
    W, H = HEADER
    shapes, (ox, oy, scale) = centered_mark(W / 2, H / 2 + 80, 1000, p)
    d, s = build.DOT, build.STEM
    # 왼쪽 아래(줄기 바닥 높이)에서 솟았다가 점의 가운데로 내려오는 포물선
    start = (s["x"] - 70, s["y"] + s["h"])
    end = (d["x"] + d["s"] / 2, d["y"] + d["s"] / 2)
    peak = (start[0] + 50, end[1] - 95)
    trail = []
    n = 9
    for i in range(n):
        t = 0.04 + 0.7 * i / (n - 1)
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * peak[0] + t * t * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * peak[1] + t * t * end[1]
        r = 2.6
        color = mix(p["bg"], p["accent"], 0.25 + 0.5 * i / (n - 1))
        c = rrect(ox + (x - r) * scale, oy + (y - r) * scale, 2 * r * scale, 2 * r * scale, r * scale)
        trail.append(([c], color))
    return trail + shapes


def header_lockup(p, font):
    """마크 위, 워드마크 아래로 쌓은 조합 — 가운데 1300px 폭 안에 든다."""
    W, H = HEADER
    upm = font["head"].unitsPerEm
    word_w_units = build.wordmark_width(font)
    P = 1240 / word_w_units
    mark_h = 760
    gap = 150
    cap = font["OS/2"].sCapHeight * P
    total = mark_h + gap + cap
    top = H / 2 - total / 2
    shapes, _ = centered_mark(W / 2, top + mark_h / 2, mark_h, p)
    words, w = wordmark_shapes(font, W / 2 - 1240 / 2, top + mark_h + gap + cap, P, p["ink"], p["accent"])
    return shapes + words


HEADER_LAYOUTS = {"center": header_center, "hop": header_hop, "lockup": header_lockup}


def header(layout, theme, font):
    p = build.PALETTE[theme]
    return render(HEADER, p["bg"], HEADER_LAYOUTS[layout](p, font), ss=2)


def save(img, path):
    img.convert("RGB").save(path, optimize=True)
    kb = os.path.getsize(path) / 1024
    assert img.mode == "RGB" and kb <= 1024, f"{path}: {img.mode} {kb:.0f} KB"
    return f"{os.path.relpath(path, HERE)} ({img.size[0]}×{img.size[1]}, {kb:.0f} KB)"


def main(font):
    os.makedirs(OUT, exist_ok=True)
    return [
        save(icon(ICON_THEME), os.path.join(OUT, "developer-icon.png")),
        save(header(HEADER_LAYOUT, HEADER_THEME, font), os.path.join(OUT, "header.png")),
    ]
