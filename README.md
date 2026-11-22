# kgbvsfbi.github.io

FirstCom Studio의 공개 웹 루트 — 앱 페이지·개인정보 처리방침과 AdMob이 읽는 `app-ads.txt`.
GitHub Pages(`main` 브랜치 `/`)로 `https://www.firstcomstudio.com/` 에 뜬다(`CNAME`). 옛 `https://kgbvsfbi.github.io/`는
새 주소로 301 전환된다 — 배포된 앱이 옛 주소를 쓰므로 커스텀 도메인 연결을 끊지 않는다. 정적 HTML이고 빌드 단계는
없다. 뽑아 쓰는 파일은 그 스크립트(`brand/build.py`, `tessera/build.py`)를 고쳐 다시 뽑고, 뽑은 결과를 함께 커밋한다.

```
app-ads.txt             # AdMob 판매자 인증 — 도메인 루트에 있어야 한다
index.html              # 스튜디오 메인 — 소개·Productions(앱 페이지로 가는 길)·문의 (kgbvsfbi/firstComMono#3113)
assets/site.css         # 처리방침 페이지 공통 스타일(Hailstorm — Tessera 처리방침은 tessera/style.css)
assets/favicon.svg      # 둥근 육각 파비콘
assets/tessera-icon.png # 메인 Productions의 Tessera 아이콘(256 px)
assets/tessera-share-card.jpg # 공유 링크 카드 그림(1200×630, 실제로 반쯤 푼 판 — 모든 언어 페이지가 같이 쓴다)
assets/tessera-touch-icon.png # 공유 링크 페이지의 apple-touch-icon(180 px)
hailstorm/index.html    # Hailstorm 앱 페이지 (support_url · marketing_url)
hailstorm/privacy.html  # Hailstorm 개인정보 처리방침 (privacy_url)
tessera/index.html      # Tessera 앱 페이지, 영어 (support_url · marketing_url) — tessera/build.py가 뽑는다 (kgbvsfbi/firstComMono#3287)
tessera/<lang>/         # 같은 페이지의 언어별 판 19개 — 목록은 앱 로케일. 문구·화면·색은 모노레포의 스토어 메타·앱 문구·palette.gd에서
tessera/build.py        # 위 20개 페이지와 style.css·img/를 뽑는다: python3 tessera/build.py <모노레포 경로>
tessera/lang.js         # 영어 페이지에 처음 들어오면 브라우저 언어 페이지로 옮긴다, 발에서 고른 언어는 기억한다
tessera/style.css       # 앱 페이지와 처리방침이 같이 쓰는 스타일 (build.py가 뽑는다)
tessera/img/            # 언어별 판 화면(스토어 스크린샷), 헤더 그림의 무늬 띠, 영상 썸네일 (build.py가 뽑는다)
tessera/privacy.html    # Tessera 개인정보 처리방침 (privacy_url)
tessera/get/index.html  # 공유 문장의 링크 — 영어 페이지, 기기별 스토어로 넘김 (kgbvsfbi/firstComMono#3148)
tessera/get/<lang>/     # 같은 페이지의 언어별 판 — 카드 문구(OG)의 언어를 주소로 가른다, 목록은 앱 로케일 (#3176)
tessera/get/get.js      # 위 페이지 전부의 스토어 이동(LIVE)과 브라우저 언어 페이지 이동, `?c=<채널>`을 스토어 추적 값으로 (#3150)
```

URL은 `https://www.firstcomstudio.com/<app>/privacy.html`. 새 앱은 디렉터리 하나를 더하고 메인 Productions에 줄 하나를 더한다.
스토어 리스팅이 드는 URL은 모노레포(`kgbvsfbi/firstComMono`)의 `apps/<app>/fastlane/metadata/`에 있다.
