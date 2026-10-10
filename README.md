# kgbvsfbi.github.io

FirstCom Studio의 공개 웹 루트 — 앱 페이지·개인정보 처리방침과 AdMob이 읽는 `app-ads.txt`.
GitHub Pages(`main` 브랜치 `/`)로 `https://kgbvsfbi.github.io/` 에 뜬다. 손으로 쓴 정적 HTML이고
빌드 도구는 없다.

```
app-ads.txt             # AdMob 판매자 인증 — 도메인 루트에 있어야 한다
index.html              # 앱 목록
assets/site.css         # 앱 공통 스타일 한 벌
hailstorm/index.html    # Hailstorm 앱 페이지 (support_url · marketing_url)
hailstorm/privacy.html  # Hailstorm 개인정보 처리방침 (privacy_url)
tessera/index.html      # Tessera 앱 페이지 (support_url · marketing_url)
tessera/privacy.html    # Tessera 개인정보 처리방침 (privacy_url)
```

URL은 `https://kgbvsfbi.github.io/<app>/privacy.html`. 새 앱은 디렉터리 하나를 더한다.
스토어 리스팅이 드는 URL은 모노레포(`kgbvsfbi/firstComMono`)의 `apps/<app>/fastlane/metadata/`에 있다.
