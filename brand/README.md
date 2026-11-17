# FirstCom Studio BI

스튜디오 이름으로 나가는 모든 표면은 이 BI를 쓴다. 사이트, Play·App Store 개발자 페이지, YouTube 채널, 스토어의 스튜디오 표기, 스튜디오 메일이 여기에 든다. 게임(Tessera, Hailstorm)의 아이콘과 화면은 각 게임의 얼굴이라 이 BI를 따르지 않는다.

- **마크**: 소문자 i를 줄기와 점으로 나눈 모양이다. 줄기는 단정하게 서 있고, 점만 강조색 둥근 사각으로 떠올라 기울어 있다. 단정한 틀에 장난스러운 한 수를 더한다는 기준에서 나왔다.
- **워드마크**: 공식 표기 `FirstCom Studio`를 Sora Bold로 쓰고, First의 i 점만 마크의 점으로 바꾼다. 표기를 바꾸지 않는다(소문자, 줄임 금지).
- **팔레트**: 라이트·다크 두 벌, 강조색은 하나.

## 정본

[`build.py`](build.py)가 정본이다. 마크 좌표, 팔레트, 글꼴·굵기·자간이 전부 그 안에 있다. `svg/`, `tokens.css`, `play/*.png`, `index.html`의 `<!-- brand:… -->` 구간은 이 스크립트가 뽑은 결과이므로 손으로 고치지 않는다. 고칠 때는 `build.py`를 고치고 다시 뽑는다.

```bash
python3 -m venv .venv && .venv/bin/pip install fonttools skia-pathops numpy pillow
.venv/bin/python brand/build.py
```

| 결과                            | 쓰는 곳                                                     |
| ------------------------------- | ----------------------------------------------------------- |
| `svg/lockup-{light,dark}.svg`   | 마크와 워드마크를 함께 놓은 가로 조합. 기본으로 이것을 쓴다 |
| `svg/mark-{light,dark}.svg`     | 마크만. 아이콘이나 좁은 자리                                |
| `svg/wordmark-{light,dark}.svg` | 워드마크만                                                  |
| `svg/favicon.svg`               | 사이트 파비콘. OS 테마를 따른다                             |
| `tokens.css`                    | 사이트 색 토큰                                              |
| `svg/{mark,lockup}-themed.svg`  | 색 대신 CSS 변수를 쓴 판. `index.html`에 인라인으로 들어간다 |
| `play/developer-icon.png`       | Play 개발자 아이콘 512×512                                  |
| `play/header.png`               | Play 개발자 페이지 헤더 4096×2304. 배치는 [`play.py`](play.py) |
| `youtube/banner.png`            | YouTube 채널 배너 2560×1440. Play 헤더와 같은 배치를 모든 기기에 보이는 가운데 1235×338 안에 줄였다 |

Play 개발자 페이지의 광고 문구는 `play/promotional-text/<로케일>.txt`에 있다. 로케일 목록은 tessera가 지원하는 Android 로케일과 같고, 모두 140자 이하다. Play Console에는 API가 없어서 손으로 넣는다.

글꼴은 [Sora](https://github.com/sora-xor/sora-font)이고, 라이선스는 SIL OFL 1.1이다([`fonts/OFL.txt`](fonts/OFL.txt)).

시안과 고른 경위는 모노레포 `docs/research/company-site-2026-11/notes/`(#3210)에 있다.
