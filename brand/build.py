"""FirstCom Studio BI 생성기 — 이 파일이 BI의 정본이다.

마크 도형, 팔레트, 워드마크 글꼴·굵기·자간이 전부 여기 있고, brand/ 아래의
SVG·CSS는 이 스크립트가 뽑은 결과다. 결과 파일을 손으로 고치지 말고 여기를
고친 뒤 다시 뽑는다.

    python3 -m venv .venv && .venv/bin/pip install fonttools numpy pillow
    .venv/bin/python brand/build.py

마크: 소문자 i를 줄기와 점으로 떼어 낸 모양. 줄기는 단정하게 서 있고, 점만
강조색 둥근 사각으로 떠올라 14° 기울어 있다(#3210 1안 "뛰는 점").
워드마크: 공식 표기 "FirstCom Studio"를 Sora Bold로 쓰고, First의 i 점만
마크와 같은 강조색 기운 사각으로 바꾼다.
"""

import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")

# 팔레트 — 라이트·다크. 사이트와 Play 자료가 이 값만 쓴다.
PALETTE = {
    "light": {
        "bg": "#f6f5f1",
        "surface": "#ffffff",
        "line": "#e2e0da",
        "ink": "#16171a",
        "ink-2": "#5c5d63",
        "ink-3": "#94959b",
        "accent": "#3355ff",
        "on-accent": "#ffffff",
    },
    "dark": {
        "bg": "#121316",
        "surface": "#1b1c20",
        "line": "#2a2b30",
        "ink": "#f1f0ec",
        "ink-2": "#a9aab0",
        "ink-3": "#6f7077",
        "accent": "#7d93ff",
        "on-accent": "#0d0f1a",
    },
}

# 마크 — 100×100 상자 안의 좌표.
STEM = dict(x=38, y=44, w=22, h=46, r=11)
DOT = dict(x=48, y=8, s=28, r=8, rot=14)

# 워드마크
FONT_FILE = os.path.join(HERE, "fonts", "Sora[wght].ttf")
WEIGHT = 700
TRACKING = -0.035  # em
TEXT = "FirstCom Studio"


def mark_shapes(ink, accent):
    s, d = STEM, DOT
    cx, cy = d["x"] + d["s"] / 2, d["y"] + d["s"] / 2
    return (
        f'<rect x="{s["x"]}" y="{s["y"]}" width="{s["w"]}" height="{s["h"]}" rx="{s["r"]}" fill="{ink}"/>'
        f'<rect x="{d["x"]}" y="{d["y"]}" width="{d["s"]}" height="{d["s"]}" rx="{d["r"]}" fill="{accent}" '
        f'transform="rotate({d["rot"]} {cx:g} {cy:g})"/>'
    )


def svg(view_box, body, width=None, height=None):
    size = f' width="{width:g}" height="{height:g}"' if width else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}"{size}>{body}</svg>\n'


def load_font():
    font = TTFont(FONT_FILE)
    return instantiateVariableFont(font, {"wght": WEIGHT})


def wordmark_dot(gs, name, x):
    """워드마크 i 점의 (가운데 x, 가운데 y, 크기, 모서리) — 글꼴 단위, y는 아래로.

    줄기 폭을 재서 마크와 같은 비율로 얹되, 글자 안에서는 점을 줄이고 줄기에
    붙인다. 오른쪽 치우침도 마크보다 줄여 옆 글자(r)와 겹치지 않게 한다.
    """
    from fontTools.pens.boundsPen import BoundsPen

    bp = BoundsPen(gs)
    gs[name].draw(bp)
    x0, _, x1, top = bp.bounds
    stem_w = x1 - x0
    k = stem_w / STEM["w"]  # 마크 단위 → 글꼴 단위
    size = stem_w * 1.08
    gap = stem_w * 0.22
    stem_cx = x + (x0 + x1) / 2
    cx = stem_cx + (DOT["x"] + DOT["s"] / 2 - (STEM["x"] + STEM["w"] / 2)) * k * 0.3
    cy = -(top + gap + size / 2)
    return cx, cy, size, DOT["r"] * k


def wordmark_width(font):
    """워드마크 폭 — 글꼴 단위."""
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    first_i = TEXT.index("i")
    names = ["dotlessi" if i == first_i else cmap[ord(c)] for i, c in enumerate(TEXT)]
    return sum(hmtx[n][0] for n in names) + TRACKING * font["head"].unitsPerEm * (len(TEXT) - 1)


def wordmark_paths(font, ink, accent):
    """TEXT를 윤곽 경로로 바꾼다. 반환: (svg 본문, 폭, 위쪽 y, 아래쪽 y) — 글꼴 단위, y는 아래로."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    track = TRACKING * upm
    x = 0.0
    parts = []
    first_i = TEXT.index("i")
    dot = None
    for idx, ch in enumerate(TEXT):
        name = "dotlessi" if idx == first_i else cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        d = pen.getCommands()
        if d:
            parts.append(f'<path d="{d}" fill="{ink}"/>')
        if idx == first_i:
            dot = wordmark_dot(gs, name, x)
        x += hmtx[name][0] + (track if idx < len(TEXT) - 1 else 0)
    cx, cy, size, r = dot
    parts.append(
        f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size:.1f}" height="{size:.1f}" '
        f'rx="{r:.1f}" fill="{accent}" transform="rotate({DOT["rot"]} {cx:.1f} {cy:.1f})"/>'
    )
    cap = font["OS/2"].sCapHeight
    top = min(-cap, cy - size * 0.75)
    return "".join(parts), x, top, 0.0


def main():
    os.makedirs(OUT, exist_ok=True)
    font = load_font()
    written = []

    def write(name, text):
        with open(os.path.join(OUT, name), "w") as f:
            f.write(text)
        written.append(name)

    for theme, p in PALETTE.items():
        # 마크 단독(투명 바탕)
        write(f"mark-{theme}.svg", svg("0 0 100 100", mark_shapes(p["ink"], p["accent"])))
        # 워드마크 단독
        body, w, top, bottom = wordmark_paths(font, p["ink"], p["accent"])
        pad = 20
        write(
            f"wordmark-{theme}.svg",
            svg(f"{-pad} {top - pad:.0f} {w + 2 * pad:.0f} {bottom - top + 2 * pad:.0f}", body),
        )
        # 가로 조합: 줄기 바닥을 글자 기준선에 맞추고, 마크 전체(점 위~줄기 바닥)를
        # 대문자 높이의 1.3배로 둔다. 사이는 0.3em.
        cap = font["OS/2"].sCapHeight
        span = STEM["y"] + STEM["h"] - DOT["y"]
        scale = cap * 1.3 / span
        base = (STEM["y"] + STEM["h"]) * scale
        # 마크가 실제로 차지하는 가로 범위: 줄기 왼쪽 ~ 기운 점의 오른쪽 끝
        half = DOT["s"] / 2 * (abs(math.cos(math.radians(DOT["rot"]))) + abs(math.sin(math.radians(DOT["rot"]))))
        right = DOT["x"] + DOT["s"] / 2 + half
        mark_w = (right - STEM["x"]) * scale
        word_x = mark_w + 0.3 * font["head"].unitsPerEm
        mark_g = f'<g transform="translate({-STEM["x"] * scale:.1f} {-base:.1f}) scale({scale:.4f})">{mark_shapes(p["ink"], p["accent"])}</g>'
        word_g = f'<g transform="translate({word_x:.1f} 0)">{body}</g>'
        t = min(top, -base + DOT["y"] * scale - 4)
        b = bottom
        write(
            f"lockup-{theme}.svg",
            svg(f"{-pad} {t - pad:.0f} {word_x + w + 2 * pad:.0f} {b - t + 2 * pad:.0f}", mark_g + word_g),
        )

    # 테마를 따르는 판 — 색 대신 CSS 변수를 쓴다. 사이트가 인라인으로 싣는다.
    themed = {}
    for name in ("mark", "lockup"):
        with open(os.path.join(OUT, f"{name}-light.svg")) as f:
            s = f.read()
        L0 = PALETTE["light"]
        s = s.replace(L0["ink"], "var(--ink)").replace(L0["accent"], "var(--accent)")
        write(f"{name}-themed.svg", s)
        themed[name] = s.strip()

    # 사이트 index.html의 <!-- brand:NAME --> … <!-- /brand:NAME --> 구간을 다시 채운다.
    index = os.path.join(HERE, "..", "index.html")
    if os.path.exists(index):
        import re

        with open(index) as f:
            page = f.read()
        for name, s in themed.items():
            pat = re.compile(rf"(<!-- brand:{name} (\S+) -->).*?(<!-- /brand:{name} -->)", re.S)

            def fill(m, s=s):
                cls = m.group(2)
                return m.group(1) + s.replace("<svg ", f'<svg class="{cls}" aria-hidden="true" ', 1) + m.group(3)

            page = pat.sub(fill, page)
        with open(index, "w") as f:
            f.write(page)
        written.append("../index.html (brand 구간)")

    # 파비콘 — OS 테마를 따른다.
    L, D = PALETTE["light"], PALETTE["dark"]
    fav = (
        f"<style>.s{{fill:{L['ink']}}}.d{{fill:{L['accent']}}}"
        f"@media (prefers-color-scheme:dark){{.s{{fill:{D['ink']}}}.d{{fill:{D['accent']}}}}}</style>"
        + mark_shapes("x", "y").replace('fill="x"', 'class="s"').replace('fill="y"', 'class="d"')
    )
    write("favicon.svg", svg("0 0 100 100", fav))

    # 팔레트 토큰 CSS
    def block(p):
        return " ".join(f"--{k}: {v};" for k, v in p.items())

    css = (
        "/* brand/build.py가 뽑는다 — 손으로 고치지 말 것 */\n"
        f":root {{ {block(L)} }}\n"
        f'@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {block(D)} }} }}\n'
        f':root[data-theme="dark"] {{ {block(D)} }}\n'
    )
    with open(os.path.join(HERE, "tokens.css"), "w") as f:
        f.write(css)
    written.append("../tokens.css")

    # Play 개발자 페이지 자료(PNG) — 배치는 play.py
    import play

    written += play.main(font)
    print("\n".join(written))


if __name__ == "__main__":
    main()
