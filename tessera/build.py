"""Tessera 앱 페이지를 20개 언어로 뽑는다 (kgbvsfbi/firstComMono#3287).

    python3 tessera/build.py <모노레포 경로>      # 기본값 ~/Coms/firstCom

문구는 모노레포가 정본이다. 이 스크립트는 옮기기만 한다.
- 머리 문장, 규칙 문장, 모드 설명, "광고로 운영" 줄: 로케일별 App Store 설명(apps/tessera/fastlane/metadata/<로케일>/description.txt)
- 부제: 같은 자리의 subtitle.txt
- 가이드 그림의 문구와 특별판 이름·규칙: 앱 문구(apps/tessera/godot/locales/<로케일>.json)
- 첫 화면의 판 화면: 로케일별 스토어 스크린샷(apps/tessera/fastlane/screenshots/<로케일>/69_02.png)
- 바탕 무늬: App Store 헤더 그림(apps/tessera/fastlane/creative/header.png)의 양끝 무늬 띠
- 영상: Play 미리보기 영상 링크(apps/tessera/fastlane/metadata/android/en-US/video.txt)
스토어와 앱에 없는 짧은 이름표(LABELS)만 여기서 정한다.

결과는 tessera/index.html(영어), tessera/<lang>/index.html, tessera/style.css, tessera/img/다. 손으로 고치지 말고 이 스크립트를 고쳐
다시 뽑는다. 브라우저 언어로 옮기는 동작은 tessera/lang.js다.
"""

import html
import json
import math
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tessera")
MONO = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/Coms/firstCom")
APP = os.path.join(MONO, "apps/tessera")
FL = os.path.join(APP, "fastlane")
SITE = "https://www.firstcomstudio.com"

# 앱 로케일 → 페이지 경로·스토어 폴더·OG 로케일. 목록과 순서는 tessera/get/과 같다(앱 Platform.SHARE_PAGES).
LANGS = ["en", "ar", "de", "es", "fr", "he", "hi", "id", "it", "ja", "ko", "nl", "pl", "pt-BR", "ru", "th", "tr", "vi", "zh-Hans", "zh-Hant"]
STORE = {"en": "en-US", "de": "de-DE", "es": "es-ES", "fr": "fr-FR", "nl": "nl-NL", "ar": "ar-SA"}
OG = {"en": "en_US", "ar": "ar_AR", "de": "de_DE", "es": "es_ES", "fr": "fr_FR", "he": "he_IL", "hi": "hi_IN", "id": "id_ID", "it": "it_IT",
      "ja": "ja_JP", "ko": "ko_KR", "nl": "nl_NL", "pl": "pl_PL", "pt-BR": "pt_BR", "ru": "ru_RU", "th": "th_TH", "tr": "tr_TR", "vi": "vi_VN",
      "zh-Hans": "zh_CN", "zh-Hant": "zh_TW"}
NATIVE = {"en": "English", "ar": "العربية", "de": "Deutsch", "es": "Español", "fr": "Français", "he": "עברית", "hi": "हिन्दी",
          "id": "Bahasa Indonesia", "it": "Italiano", "ja": "日本語", "ko": "한국어", "nl": "Nederlands", "pl": "Polski",
          "pt-BR": "Português (Brasil)", "ru": "Русский", "th": "ไทย", "tr": "Türkçe", "vi": "Tiếng Việt", "zh-Hans": "简体中文", "zh-Hant": "繁體中文"}
RTL = {"ar", "he"}

# 스토어·앱 문구에 없는 이름표: 모드, 영상, 영상 단추, 앱의 다른 것, 문의, 처리방침
LABELS = {
    "en": ("Modes", "Watch", "Watch on YouTube", "Also in the app", "Contact", "Privacy Policy"),
    "ar": ("الأوضاع", "فيديو", "شاهد على YouTube", "وأيضًا في التطبيق", "تواصل معنا", "سياسة الخصوصية"),
    "de": ("Modi", "Video", "Auf YouTube ansehen", "Außerdem in der App", "Kontakt", "Datenschutzerklärung"),
    "es": ("Modos", "Vídeo", "Ver en YouTube", "También en la app", "Contacto", "Política de privacidad"),
    "fr": ("Modes", "Vidéo", "Regarder sur YouTube", "Aussi dans l’app", "Contact", "Politique de confidentialité"),
    "he": ("מצבים", "סרטון", "צפו ב-YouTube", "ועוד באפליקציה", "צור קשר", "מדיניות פרטיות"),
    "hi": ("मोड", "वीडियो", "YouTube पर देखें", "ऐप में और भी", "संपर्क", "गोपनीयता नीति"),
    "id": ("Mode", "Video", "Tonton di YouTube", "Juga di aplikasi", "Kontak", "Kebijakan Privasi"),
    "it": ("Modalità", "Video", "Guarda su YouTube", "Anche nell’app", "Contatti", "Informativa sulla privacy"),
    "ja": ("モード", "動画", "YouTubeで見る", "アプリにはほかにも", "お問い合わせ", "プライバシーポリシー"),
    "ko": ("모드", "영상", "YouTube에서 보기", "앱에는 이것도", "문의", "개인정보 처리방침"),
    "nl": ("Modi", "Video", "Bekijk op YouTube", "Ook in de app", "Contact", "Privacybeleid"),
    "pl": ("Tryby", "Wideo", "Obejrzyj na YouTube", "Także w aplikacji", "Kontakt", "Polityka prywatności"),
    "pt-BR": ("Modos", "Vídeo", "Assistir no YouTube", "Também no app", "Contato", "Política de privacidade"),
    "ru": ("Режимы", "Видео", "Смотреть на YouTube", "Ещё в приложении", "Контакты", "Политика конфиденциальности"),
    "th": ("โหมด", "วิดีโอ", "ดูบน YouTube", "ในแอปยังมี", "ติดต่อ", "นโยบายความเป็นส่วนตัว"),
    "tr": ("Modlar", "Video", "YouTube’da izle", "Uygulamada ayrıca", "İletişim", "Gizlilik Politikası"),
    "vi": ("Chế độ", "Video", "Xem trên YouTube", "Còn có trong ứng dụng", "Liên hệ", "Chính sách quyền riêng tư"),
    "zh-Hans": ("模式", "视频", "在 YouTube 上观看", "应用里还有", "联系", "隐私政策"),
    "zh-Hant": ("模式", "影片", "在 YouTube 上觀看", "App 裡還有", "聯絡", "隱私權政策"),
}

IOS = "https://apps.apple.com/app/id6821070961"
ANDROID = "https://play.google.com/store/apps/details?id=com.firstcom.tessera"
MAIL = "firstcomstudio@gmail.com"
VIDEO = open(os.path.join(FL, "metadata/android/en-US/video.txt")).read().strip()
VID = re.search(r"v=([\w-]+)", VIDEO).group(1)

esc = html.escape


def page_path(lang):
    return "/tessera/" if lang == "en" else f"/tessera/{lang}/"


# ── 이미지 ──────────────────────────────────────────────────────────

IMG = os.path.join(OUT, "img")
os.makedirs(IMG, exist_ok=True)


def images():
    # 첫 화면의 판 화면 — 로케일별. 폰 틀 안에 300 CSS px로 놓이므로 2배.
    for lang in LANGS:
        src = os.path.join(FL, "screenshots", STORE.get(lang, lang), "69_02.png")
        im = Image.open(src).convert("RGB")
        im.resize((600, round(im.height * 600 / im.width)), Image.LANCZOS).save(os.path.join(IMG, f"board-{lang}.webp"), quality=80)
    # 바탕 무늬 — 헤더 그림에서 아이콘·이름이 없는 양끝 띠. 안쪽 끝과 아래 끝이 바탕으로 사라지도록 알파를 굽는다.
    # (뒤집어 이으면 숫자가 거꾸로 읽혀서 양끝을 따로 둔다)
    h = Image.open(os.path.join(FL, "creative/header.png")).convert("RGB")
    for name, box, inner_right in [("pattern-l.webp", (0, 0, 1150, h.height), True), ("pattern-r.webp", (h.width - 1150, 0, h.width, h.height), False)]:
        c = h.crop(box)
        c = c.resize((c.width // 2, c.height // 2), Image.LANCZOS).convert("RGBA")
        w, hh = c.size
        a = Image.new("L", (w, hh))
        a.putdata([round(255 * min(1, (1 - (x if inner_right else w - 1 - x) / w) / 0.45) * min(1, (1 - y / hh) / 0.6))
                   for y in range(hh) for x in range(w)])
        c.putalpha(a)
        c.save(os.path.join(IMG, name), quality=80)
    # 영상 썸네일 — 남의 서버로 요청이 가지 않도록 우리 쪽에 둔다. 영상이 바뀌면 지우고 다시 뽑는다.
    thumb = os.path.join(IMG, "video.jpg")
    if not os.path.exists(thumb):
        raw = os.path.join(IMG, "video-raw.jpg")
        os.system(f'curl -sf -o "{raw}" https://i.ytimg.com/vi/{VID}/maxresdefault.jpg')
        Image.open(raw).convert("RGB").resize((960, 540), Image.LANCZOS).save(thumb, quality=78, optimize=True)
        os.remove(raw)


# ── 판 그림 ─────────────────────────────────────────────────────────
# 단서 하나와 여섯 이웃. 표지는 모노레포 gen/tessera_gen/hexlink.py Solution.clue와 같은 규칙으로 계산한다 — 판 밖은 빈칸,
# 이웃 지뢰가 2~4개일 때만 이어짐({n})·떨어짐(-n-)을 붙인다. 그래서 맨 숫자는 0·1·5·6뿐이다.

S3 = math.sqrt(3)
DIRS = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))  # hexlink.py DIRS — 둘레를 도는 순서


def rhex(cx, cy, rad, k=0.2):
    v = [(cx + math.cos(math.radians(60 * i - 90)) * rad, cy + math.sin(math.radians(60 * i - 90)) * rad) for i in range(6)]
    d = ""
    for i in range(6):
        c, p, n = v[i], v[i - 1], v[(i + 1) % 6]
        a = (c[0] + (p[0] - c[0]) * k, c[1] + (p[1] - c[1]) * k)
        b = (c[0] + (n[0] - c[0]) * k, c[1] + (n[1] - c[1]) * k)
        d += "%s%.2f %.2fQ%.2f %.2f %.2f %.2f" % ("L" if i else "M", a[0], a[1], c[0], c[1], b[0], b[1])
    return d + "Z"


def xy(q, r, s=10):
    return s * S3 * (q + r / 2), s * 1.5 * r


def clue_of(q, r, mines, board):
    ring = [1 if (q + dq, r + dr) in mines and (q + dq, r + dr) in board else 0 for dq, dr in DIRS]
    k = sum(ring)
    if not 2 <= k <= 4:
        return str(k), None
    return str(k), sum(1 for i in range(6) if ring[i] == 1 and ring[i - 1] == 0) == 1


def board_svg(board, mines, clues, label, off=(), zone=None, zone_n=None):
    pts = [xy(q, r) for q, r in list(board) + list(off)]
    x0, x1 = min(p[0] for p in pts) - 10, max(p[0] for p in pts) + 10
    y0, y1 = min(p[1] for p in pts) - 11, max(p[1] for p in pts) + 11
    o = [f'<svg class="board" viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}" role="img" aria-label="{esc(label)}">']
    for q, r in off:
        x, y = xy(q, r)
        o.append(f'<path d="{rhex(x, y, 9.2)}" class="off"/>')
    for q, r in board:
        x, y = xy(q, r)
        if (q, r) in mines:
            o.append(f'<path d="{rhex(x, y + 0.8, 9.6)}" class="sh"/><path d="{rhex(x, y, 9.6)}" class="mine"/>'
                     f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.1" class="pearl"/>')
        elif (q, r) in clues:
            o.append(f'<path d="{rhex(x, y, 9.6)}" class="clue"/>')
            n, link = clue_of(q, r, mines, board)
            if clues[(q, r)]:
                n = "?"
            if link is None:
                o.append(f'<text x="{x:.2f}" y="{y + 0.3:.2f}" font-size="7.4" class="cn">{n}</text>')
            else:
                a, b = ("{", "}") if link else ("-", "-")
                o.append(f'<text x="{x:.2f}" y="{y + 0.3:.2f}" font-size="6.2" class="cn"><tspan class="cb">{a}</tspan>{n}'
                         f'<tspan class="cb">{b}</tspan></text>')
        else:
            o.append(f'<path d="{rhex(x, y + 0.8, 9.6)}" class="sh"/><path d="{rhex(x, y, 9.6)}" class="safe"/>')
    if zone:
        # 구역 테두리 — 이웃이 구역 밖인 변만 긋는다(앱 ui/board.gd zone_loops의 요약). 수 원은 첫 칸(맨 위 줄 왼쪽)의 왼쪽 위.
        out = [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]  # 꼭짓점 i→i+1 변의 바깥 이웃(꼭짓점 0이 위)
        segs = []
        for q, r in zone:
            x, y = xy(q, r)
            v = [(x + math.cos(math.radians(60 * i - 90)) * 10, y + math.sin(math.radians(60 * i - 90)) * 10) for i in range(6)]
            for i, (dq, dr) in enumerate(out):
                if (q + dq, r + dr) not in zone:
                    segs.append(f"M{v[i][0]:.2f} {v[i][1]:.2f}L{v[(i + 1) % 6][0]:.2f} {v[(i + 1) % 6][1]:.2f}")
        o.append(f'<path d="{"".join(segs)}" class="zl"/>')
        fx, fy = xy(*sorted(zone, key=lambda c: (c[1], c[0]))[0])
        bx, by = fx - 6.2, fy - 6.8
        o.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="3.6" class="zb"/>'
                 f'<text x="{bx:.2f}" y="{by + 0.2:.2f}" font-size="4.6" class="zn">{zone_n}</text>')
    o.append("</svg>")
    return "".join(o)


FLOWER = [(0, 0)] + list(DIRS)


def flower(mines, label, hidden=False):
    return board_svg(FLOWER, set(mines), {(0, 0): hidden}, label)


RING2 = [(q, r) for q in range(-2, 3) for r in range(-2, 3) if abs(q + r) <= 2]
FIG = {
    "number": flower([(1, -1)], "1"),
    "together": flower([(1, -1), (0, -1)], "{2}"),
    "apart": flower([(1, -1), (-1, 1)], "-2-"),
    # 판 가장자리 — 아래 둘이 판 밖(점선)
    "edge": board_svg([(0, 0), (1, 0), (1, -1), (0, -1), (-1, 0)], {(1, -1), (0, -1)}, {(0, 0): False}, "{2}", off=[(-1, 1), (0, 1)]),
    "friday": flower([(-1, 0), (-1, 1), (0, 1)], "{?}", hidden=True),
    # 수요 특별판 — 가운데 7칸 꽃이 구역(모노레포 hexlink.py ZONES의 가운데 꽃). 구역 안 지뢰 둘
    "wednesday": board_svg(RING2, {(0, -1), (-1, 1), (2, -2), (-2, 1)}, {(2, 0): False, (-2, 2): False}, "2",
                           zone=FLOWER, zone_n=2),
}
LABEL = {"number": "1", "together": "{2}", "apart": "-2-", "edge": "{2}"}

# ── 문구 ─────────────────────────────────────────────────────────────


def store(lang):
    d = os.path.join(FL, "metadata", STORE.get(lang, lang))
    desc = open(os.path.join(d, "description.txt")).read().strip()
    paras = [p.strip() for p in desc.split("\n\n")]
    head, rules, bullets, free = paras[0], paras[1], paras[2], paras[-1]
    items = [b.lstrip("• ").strip() for b in bullets.splitlines() if b.startswith("•")]
    assert len(items) == 9, (lang, len(items))
    return {"head": head, "rules": rules, "items": items, "free": free,
            "subtitle": open(os.path.join(d, "subtitle.txt")).read().strip(),
            "promo": open(os.path.join(d, "promotional_text.txt")).read().strip()}


def ltr_ranges(s, lang):
    """RTL 페이지에서 숫자 범위(2–4)가 4–2로 뒤집히지 않도록 그 구간만 LRI…PDI로 묶는다."""
    if lang not in RTL:
        return s
    return re.sub(r"(\d[\d,.]*\s*[–-]\s*\d[\d,.]*)", "\u2066\\1\u2069", s)


def split_item(s):
    """'Daily — Tessera #N, …' → (이름, 설명). 줄표가 없는 줄은 이름 없이 설명만."""
    if " — " in s:
        a, b = s.split(" — ", 1)
        return a, b
    return "", s


def headline(s):
    """머리 문장의 둘째 마디를 강조한다 — 첫 마침표·쉼표 뒤. 끊을 자리가 없으면 통째로."""
    m = re.search(r"([.!。،，,、]\s?)", s)
    if not m or m.end() >= len(s):
        return esc(s)
    return f"{esc(s[:m.end()])}<em>{esc(s[m.end():].strip())}</em>"  # 원문의 띄어쓰기를 그대로 둔다(CJK는 붙여 쓴다)


def strings(lang):
    loc = json.load(open(os.path.join(APP, "godot/locales", f"{lang}.json")))
    st = store(lang)
    return loc, st


# ── 페이지 ───────────────────────────────────────────────────────────

APPLE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35'
         'C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13'
         '-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>')
PLAY = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.18 23.76a2 2 0 0 1-1.01-.27A2.1 2.1 0 0 1 1 21.6V2.4C1 1.52 1.46.78 2.17.51l11.4 11.4'
        '-10.39 11.85zM20.4 14.9l-2.6 1.5-3.13-3.13 3.13-3.13 2.63 1.52a2.1 2.1 0 0 1 0 3.24zM4.17.1l12.27 7.07-3.13 3.14z"/></svg>')


def render(lang):
    loc, st = strings(lang)
    modes_l, watch_l, watch_cta, also_l, contact_l, privacy_l = LABELS[lang]
    items = [split_item(s) for s in st["items"]]
    rtl = lang in RTL
    title = f"Tessera — {st['subtitle']}"

    alts = "\n".join(f'    <link rel="alternate" hreflang="{l}" href="{SITE}{page_path(l)}" />' for l in LANGS)
    alts += f'\n    <link rel="alternate" hreflang="x-default" href="{SITE}/tessera/" />'
    og_alts = "\n".join(f'    <meta property="og:locale:alternate" content="{OG[l]}" />' for l in LANGS if l != lang)

    guide = []
    for key, sub in [("number", None), ("together", "tutorial.sub.together"), ("apart", "tutorial.sub.apart"), ("edge", "tutorial.sub.edge")]:
        cap = f'<bdi class="lb" dir="ltr">{esc(LABEL[key])}</bdi> {esc(loc["tutorial.title." + key])}'
        if sub:
            cap += f'<small>{esc(loc[sub])}</small>'
        guide.append(f'<figure><div class="pic">{FIG[key]}</div><figcaption>{cap}</figcaption></figure>')

    # 모드 — 스토어 설명의 데일리·레벨·그림·대결 줄(0·1·2·4번째)과 특별판 둘(앱 문구의 이름·규칙)
    rows = [(items[i][0], items[i][1], "") for i in (0, 1, 2, 4)]
    rows += [(loc["friday.name"], loc["special.rule"], FIG["friday"]), (loc["wednesday.name"], loc["wednesday.rule"], FIG["wednesday"])]
    modes = "".join(f'<div class="row"><span class="no">{n:02d}</span><h3>{esc(h)}</h3><p>{esc(ltr_ranges(p, lang))}</p><span class="mini">{svg}</span></div>'
                    for n, (h, p, svg) in enumerate(rows, 1))
    # 앱의 다른 것 — 작품·통계·공유·힌트 줄(3·6·7·8번째). 순위(5번째)는 Game Center 이야기라 웹에서는 뺀다
    also = "".join(f'<li>{f"<b>{esc(h)}</b>" if h else ""}<span>{esc(p)}</span></li>' for h, p in (items[i] for i in (3, 6, 7, 8)))
    langs = "".join(f'<b lang="{l}">{esc(NATIVE[l])}</b>' if l == lang else f'<a href="{page_path(l)}" lang="{l}" hreflang="{l}" data-lang="{l}">{esc(NATIVE[l])}</a>'
                    for l in LANGS)

    return f"""<!doctype html>
<!-- tessera/build.py가 뽑는다 — 손으로 고치지 말 것 (kgbvsfbi/firstComMono#3287) -->
<html lang="{lang}" dir="{'rtl' if rtl else 'ltr'}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(st['promo'])}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="FirstCom Studio" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(st['promo'])}" />
    <meta property="og:url" content="{SITE}{page_path(lang)}" />
    <meta property="og:locale" content="{OG[lang]}" />
{og_alts}
    <meta property="og:image" content="{SITE}/assets/tessera-share-card.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="color-scheme" content="light dark" />
    <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="/assets/tessera-touch-icon.png" />
    <link rel="canonical" href="{SITE}{page_path(lang)}" />
{alts}
    <link rel="stylesheet" href="/tessera/style.css" />
    <!-- 브라우저 언어 페이지로 옮긴다(영어 페이지에서 처음 들어올 때만) -->
    <script src="/tessera/lang.js"></script>
  </head>
  <body>
    <div class="wrap">
      <nav class="nav">
        <a class="me" href="{page_path(lang)}"><img src="/assets/tessera-icon.png" alt="" width="34" height="34" />Tessera</a>
        <ul>
          <li class="hide-s"><a href="#play">{esc(loc['play.rules'])}</a></li>
          <li><a href="#modes">{esc(modes_l)}</a></li>
          <li><a class="studio" href="/" aria-label="FirstCom Studio"><img class="lk l" src="/brand/svg/lockup-light.svg" alt="" /><img class="lk d" src="/brand/svg/lockup-dark.svg" alt="" /><img class="mk l" src="/brand/svg/mark-light.svg" alt="" /><img class="mk d" src="/brand/svg/mark-dark.svg" alt="" /></a></li>
        </ul>
      </nav>
      <header class="hero">
        <div class="txt">
          <p class="lab">{esc(st['subtitle'])}</p>
          <h1>{headline(st['head'])}</h1>
          <p class="lead">{esc(st['rules'])}</p>
          <div class="stores">
            <a class="store" href="{IOS}">{APPLE}<b>App Store</b></a>
            <a class="store" href="{ANDROID}">{PLAY}<b>Google Play</b></a>
          </div>
          <p class="free">{esc(st['free'])}</p>
        </div>
        <div class="phone"><img src="/tessera/img/board-{lang}.webp" alt="{esc(st['subtitle'])}" width="300" height="650" /></div>
      </header>
      <section id="play">
        <p class="lab">{esc(loc['play.rules'])}</p>
        <h2>{esc(loc['tutorial.say.number'])}</h2>
        <div class="guide">{"".join(guide)}</div>
      </section>
      <section id="video">
        <p class="lab">{esc(watch_l)}</p>
        <a class="video" href="{VIDEO}"><img src="/tessera/img/video.jpg" alt="" width="960" height="540" /><span class="play"></span><span class="cap">{esc(watch_cta)}</span></a>
      </section>
      <section id="modes">
        <p class="lab">{esc(modes_l)}</p>
        {modes}
      </section>
      <section id="more">
        <p class="lab">{esc(also_l)}</p>
        <ul class="also">{also}</ul>
      </section>
    </div>
    <footer id="contact">
      <div class="wrap">
        <p class="lab">{esc(contact_l)}</p>
        <a class="m" href="mailto:{MAIL}">{MAIL}</a>
        <div class="links"><a href="/tessera/privacy.html">{esc(privacy_l)}</a><a href="{VIDEO}">YouTube</a></div>
        <div class="langs">{langs}</div>
        <a class="by" href="/" aria-label="FirstCom Studio"><img class="l" src="/brand/svg/lockup-light.svg" alt="" /><img class="d" src="/brand/svg/lockup-dark.svg" alt="" /></a>
        <small>© 2026 FirstCom Studio</small>
      </div>
    </footer>
  </body>
</html>
"""


# ── 스타일 ───────────────────────────────────────────────────────────
# 색은 앱의 팔레트(모노레포 apps/tessera/godot/ui/palette.gd LIGHT·DARK)에서 온다. 머리·발의 짜임은 스튜디오 메인(/index.html)과
# 같고, 스튜디오 BI(로크업)는 스튜디오로 가는 두 자리에만 쓴다.

PAL_KEYS = {"bg": "bg", "surface": "surface", "hi": "surface_hi", "line": "line", "ink": "ink", "ink2": "ink_2", "ink3": "ink_3",
            "brand": "brand", "onb": "on_brand", "clue": "clue", "mine": "mine", "pearl": "pearl"}


def palette():
    src = open(os.path.join(APP, "godot/ui/palette.gd")).read()
    out = {}
    for name in ("LIGHT", "DARK"):
        block = re.search(name + r" := \{(.*?)\n\}", src, re.S).group(1)
        vals = dict(re.findall(r"(\w+) = Color\(\"(#[0-9a-f]{6})\"\)", block))
        out[name] = {k: vals[v] for k, v in PAL_KEYS.items()}
    return out["LIGHT"], out["DARK"]


def css():
    light, dark = palette()
    lv = "; ".join(f"--{k}: {v}" for k, v in light.items()) + "; --shade: rgba(60, 48, 30, 0.16)"
    dv = "; ".join(f"--{k}: {v}" for k, v in dark.items()) + "; --shade: rgba(0, 0, 0, 0.5)"
    return f"""/* tessera/build.py가 뽑는다 — 손으로 고치지 말 것. 색은 앱 palette.gd에서 온다 */
:root {{ {lv}; --pat: 0.55; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {dv}; --pat: 0.12; }} }}
:root[data-theme="dark"] {{ {dv}; --pat: 0.12; }}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{ background: var(--bg); color: var(--ink); font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; min-height: 100vh; overflow-x: hidden; }}
a {{ color: inherit; text-decoration: none; }}
h1, h2, h3 {{ letter-spacing: -0.03em; }}
:lang(ko) {{ word-break: keep-all; }}
:lang(ko) .lab, :lang(ja) .lab, :lang(zh) .lab {{ letter-spacing: 0.04em; }}
:lang(ar) h1, :lang(ar) h2, :lang(ar) h3, :lang(hi) h1, :lang(hi) h2, :lang(hi) h3, :lang(th) h1, :lang(th) h2, :lang(th) h3 {{ letter-spacing: 0; }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 16px; }}
.nav {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 22px 0; }}
.me {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; }}
.me img {{ width: 34px; height: 34px; border-radius: 9px; display: block; }}
.nav ul {{ list-style: none; display: flex; align-items: center; gap: 22px; font-size: 0.92rem; color: var(--ink2); }}
.nav ul a:hover {{ color: var(--brand); }}
.studio img, .by img {{ height: 18px; width: auto; display: block; }}
.d {{ display: none !important; }}
:root[data-theme="dark"] .l {{ display: none !important; }}
:root[data-theme="dark"] .d {{ display: block !important; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .l {{ display: none !important; }} :root:not([data-theme="light"]) .d {{ display: block !important; }} }}
.lab {{ font-size: 0.8rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink3); margin-bottom: 18px; display: flex; align-items: center; gap: 10px; }}
.lab::before {{ content: ""; flex: none; width: 10px; height: 11px; background: var(--brand); clip-path: polygon(50% 0, 100% 25%, 100% 75%, 50% 100%, 0 75%, 0 25%); }}
/* 첫 화면 — 바탕은 헤더 그림의 양끝 무늬, 왼쪽에 문장과 스토어, 오른쪽에 그 언어의 판 화면 */
.hero {{ position: relative; padding: 48px 0 72px; display: grid; grid-template-columns: 1.15fr 1fr; gap: 40px; align-items: center; }}
.hero::before, .hero::after {{ content: ""; position: absolute; top: 0; bottom: 0; width: min(46vw, 560px); opacity: var(--pat); z-index: -1; pointer-events: none; }}
.hero::before {{ left: calc(50% - 50vw); background: url(img/pattern-l.webp) left top / auto 100% no-repeat; }}
.hero::after {{ right: calc(50% - 50vw); background: url(img/pattern-r.webp) right top / auto 100% no-repeat; }}
.hero .txt {{ background: color-mix(in srgb, var(--bg) 82%, transparent); padding: 28px; border-radius: 24px; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }}
h1 {{ font-size: clamp(2rem, 6vw, 3.4rem); line-height: 1.1; font-weight: 800; text-wrap: balance; overflow-wrap: break-word; }}
h1 em {{ font-style: normal; color: var(--brand); }}
.lead {{ margin-top: 18px; font-size: 1.05rem; color: var(--ink2); max-width: 34em; }}
.stores {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }}
.store {{ display: inline-flex; align-items: center; gap: 10px; background: var(--ink); color: var(--bg); padding: 12px 20px 12px 16px; border-radius: 14px; }}
.store:hover {{ background: var(--brand); color: var(--onb); }}
.store svg {{ width: 24px; height: 24px; fill: currentColor; flex: none; }}
.store b {{ font-size: 1.05rem; }}
.free {{ margin-top: 14px; font-size: 0.88rem; color: var(--ink3); }}
.phone {{ justify-self: center; width: min(300px, 100%); border-radius: 36px; border: 8px solid var(--ink); overflow: hidden; box-shadow: 0 24px 60px var(--shade); background: var(--surface); }}
.phone img {{ width: 100%; height: auto; display: block; }}
section {{ padding: 56px 0; border-top: 1px solid var(--line); }}
h2 {{ font-size: clamp(1.5rem, 4vw, 2.1rem); line-height: 1.2; margin-bottom: 24px; max-width: 24em; }}
/* 가이드 — 단서 하나와 여섯 이웃 */
.guide {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }}
.guide .pic {{ background: var(--surface); border: 1px solid var(--line); border-radius: 20px; aspect-ratio: 1; display: grid; place-items: center; padding: 14px; }}
.guide .pic svg {{ width: 88%; }}
figcaption {{ margin-top: 12px; color: var(--ink); font-weight: 600; font-size: 0.95rem; line-height: 1.45; }}
figcaption .lb {{ font-variant-numeric: tabular-nums; margin-inline-end: 4px; }}
figcaption small {{ display: block; margin-top: 4px; color: var(--ink2); font-weight: 400; font-size: 0.9rem; }}
.board {{ display: block; height: auto; overflow: visible; }}
.board .safe {{ fill: var(--hi); }}
.board .sh {{ fill: var(--shade); }}
.board .clue {{ fill: var(--clue); }}
.board .mine {{ fill: var(--mine); }}
.board .pearl {{ fill: var(--pearl); }}
.board .off {{ fill: none; stroke: var(--ink3); stroke-width: 0.6; stroke-dasharray: 1.4 1.4; }}
.board .cn {{ fill: var(--ink); font-weight: 800; text-anchor: middle; dominant-baseline: central; font-variant-numeric: tabular-nums; }}
.board .cb {{ font-weight: 400; fill-opacity: 0.5; }}
.board .zl {{ fill: none; stroke: var(--brand); stroke-width: 0.8; stroke-linecap: round; stroke-linejoin: round; }}
.board .zb {{ fill: var(--brand); }}
.board .zn {{ fill: var(--onb); font-weight: 800; text-anchor: middle; dominant-baseline: central; }}
/* 영상 — 썸네일과 재생 단추. 플레이어를 심지 않아 YouTube 쿠키가 페이지에 붙지 않는다 */
.video {{ position: relative; display: block; border-radius: 20px; overflow: hidden; border: 1px solid var(--line); aspect-ratio: 16 / 9; background: #000; }}
.video img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.video .play {{ position: absolute; inset: 0; margin: auto; width: 76px; height: 76px; border-radius: 50%; background: var(--brand); display: grid; place-items: center; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); }}
.video .play::after {{ content: ""; border-style: solid; border-width: 13px 0 13px 21px; border-color: transparent transparent transparent var(--onb); margin-left: 6px; }}
.video .cap {{ position: absolute; inset-inline-start: 16px; bottom: 14px; color: #fff; font-size: 0.9rem; font-weight: 600; text-shadow: 0 1px 6px rgba(0, 0, 0, 0.6); }}
.video:hover .play {{ transform: scale(1.06); }}
/* 모드 */
.row {{ display: grid; grid-template-columns: 40px 240px 1fr 96px; align-items: center; gap: 24px; padding: 18px 0; border-bottom: 1px solid var(--line); }}
.row:last-child {{ border-bottom: 0; }}
.row .no {{ color: var(--ink3); font-weight: 600; font-variant-numeric: tabular-nums; }}
.row h3 {{ font-size: clamp(1.3rem, 3.6vw, 1.8rem); line-height: 1.2; }}
.row p {{ color: var(--ink2); }}
.row .mini svg {{ width: 96px; }}
.also {{ list-style: none; display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px 28px; }}
.also li {{ color: var(--ink2); }}
.also b {{ display: block; color: var(--ink); font-size: 1.05rem; margin-bottom: 4px; }}
footer {{ border-top: 1px solid var(--line); padding: 56px 0 64px; }}
footer .m {{ font-weight: 700; font-size: clamp(1.3rem, 4vw, 2rem); line-height: 1.2; overflow-wrap: anywhere; letter-spacing: -0.03em; }}
footer .m:hover, footer a:hover {{ color: var(--brand); }}
footer .links {{ display: flex; flex-wrap: wrap; gap: 8px 24px; margin-top: 22px; color: var(--ink2); }}
footer .langs {{ display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 22px; font-size: 0.85rem; color: var(--ink3); }}
footer .langs b {{ color: var(--ink); }}
footer .by {{ display: inline-block; margin-top: 30px; }}
footer .by img {{ height: 20px; }}
footer small {{ display: block; margin-top: 14px; color: var(--ink3); }}
/* 처리방침(tessera/privacy.html) — 글만 있는 문서 */
.doc {{ max-width: 760px; padding: 8px 0 56px; line-height: 1.7; }}
.doc h1 {{ font-size: clamp(1.6rem, 5vw, 2.2rem); margin: 16px 0 8px; }}
.doc h2 {{ font-size: 1.15rem; margin: 36px 0 8px; max-width: none; }}
.doc p, .doc li {{ color: var(--ink2); font-size: 0.97rem; }}
.doc p + p, .doc ul {{ margin-top: 10px; }}
.doc ul {{ padding-inline-start: 1.3em; }}
.doc li + li {{ margin-top: 6px; }}
.doc strong {{ color: var(--ink); }}
.doc a {{ color: var(--brand); text-decoration: underline; text-underline-offset: 2px; }}
.doc code {{ font-size: 0.9em; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 0 4px; }}
.doc hr {{ border: 0; border-top: 1px solid var(--line); margin: 40px 0; }}
.doc section {{ padding: 0; border: 0; }}
.doc .lang {{ display: flex; gap: 14px; font-size: 0.9rem; color: var(--ink3); }}
.doc .lang a {{ color: var(--ink2); text-decoration: none; }}
.doc .lang a:hover {{ color: var(--brand); }}
.video {{ max-width: 760px; }}
@media (max-width: 760px) {{
  section {{ padding: 40px 0; }}
  .hero {{ grid-template-columns: 1fr; padding: 16px 0 44px; gap: 28px; }}
  .hero .txt {{ padding: 20px; }}
  .phone {{ width: 62%; }}
  .guide {{ grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  .row {{ grid-template-columns: 1fr 72px; gap: 4px 16px; padding: 16px 0; }}
  .row .no {{ display: none; }}
  .row h3, .row p {{ grid-column: 1; }}
  .row .mini {{ grid-column: 2; grid-row: 1 / span 2; }}
  .row .mini svg {{ width: 72px; }}
  .also {{ grid-template-columns: 1fr; }}
  .store {{ flex: 1 1 100%; justify-content: center; }}
  .nav ul {{ gap: 14px; font-size: 0.86rem; }}
}}
/* 좁은 폭에서는 메인처럼 스튜디오 로크업 대신 마크만 */
.studio .mk {{ height: 26px; }}
@media (min-width: 481px) {{ :root .nav .studio .mk {{ display: none !important; }} }}
@media (max-width: 480px) {{ .nav .hide-s {{ display: none; }} :root .nav .studio .lk {{ display: none !important; }} }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} .video:hover .play {{ transform: none; }} }}
"""


def main():
    images()
    open(os.path.join(OUT, "style.css"), "w").write(css())
    for lang in LANGS:
        d = OUT if lang == "en" else os.path.join(OUT, lang)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(render(lang))
    print("tessera: %d pages" % len(LANGS))


if __name__ == "__main__":
    main()
