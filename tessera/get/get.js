// tessera 공유 링크 페이지(tessera/get/와 그 아래 언어 페이지)가 모두 읽는 동작 — firstComMono#3148·#3176.
// 메신저 크롤러는 스크립트를 돌리지 않으므로 카드(OG 메타)는 각 페이지의 언어 그대로 남고, 사람이 열었을 때만 움직인다.
//
// 1. 기기를 보고 스토어로 넘긴다 — LIVE가 false인 동안(스토어 페이지가 열리기 전)과 그 밖의 기기는 페이지가 그대로 보인다.
//    출시 때 LIVE만 true로 바꾼다.
// 2. 아니면 브라우저 언어(navigator.languages)의 페이지로 옮긴다. 없는 언어는 영어(tessera/get/).
//    고르는 규칙은 앱의 Locale.resolve_locale(apps/tessera/godot/ui/locale.gd)과 같다.
// 3. 채널(firstComMono#3150) — 게시글 링크는 `?c=<채널>`(영숫자 40자 이내)을 싣고, 스토어 주소에 같은 이름을 붙인다.
//    Android는 Play 설치 리퍼러의 utm_source(GA4 첫 사용자 소스가 된다), iOS는 App Store 캠페인 토큰 ct(App Store Connect
//    분석에만 남는다). 채널이 없으면 앱에서 나간 공유 링크라 `share`다. 언어 페이지로 옮겨도 쿼리를 그대로 들고 간다.
//    iOS 캠페인은 공급자 토큰 pt가 있어야 잡힌다 — PT가 비어 있는 동안은 iOS 링크에 캠페인을 붙이지 않는다.
(function () {
  var LIVE = false;
  var IOS = "https://apps.apple.com/app/id6821070961";
  var ANDROID = "https://play.google.com/store/apps/details?id=com.firstcom.tessera";
  // App Store Connect → 앱 분석 → 캠페인 링크 생성기의 pt 값(계정 하나에 하나).
  var PT = "";

  var m = /[?&]c=([^&#]*)/.exec(location.search);
  var raw = "";
  try {
    raw = m ? decodeURIComponent(m[1]).toLowerCase() : "";
  } catch (e) {
    // 깨진 퍼센트 인코딩 — 채널 없음으로 친다.
  }
  var channel = /^[a-z0-9]{1,40}$/.test(raw) ? raw : "share";
  var ios = PT ? IOS + "?pt=" + PT + "&ct=" + channel + "&mt=8" : IOS;
  var android = ANDROID + "&referrer=" + encodeURIComponent("utm_source=" + channel + "&utm_medium=link");

  // 페이지가 그대로 보일 때(LIVE 전 · 데스크톱) 누르는 스토어 단추도 같은 채널을 싣는다. 이 파일은 <head>에서 돌아
  // 단추가 아직 없으므로 문서를 다 읽은 뒤에 바꾼다.
  function tagStores() {
    var stores = document.querySelectorAll("a.store");
    for (var k = 0; k < stores.length; k++) {
      var href = stores[k].getAttribute("href") || "";
      if (href.indexOf(IOS) === 0) stores[k].setAttribute("href", ios);
      else if (href.indexOf(ANDROID) === 0) stores[k].setAttribute("href", android);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", tagStores);
  else tagStores();
  // 언어 페이지 목록 — 앱 로케일과 같다(Platform.SHARE_PAGES). 영어는 tessera/get/ 그 자체다.
  var PAGES = ["ar", "de", "es", "fr", "he", "hi", "id", "it", "ja", "ko", "nl", "pl", "pt-BR", "ru", "th", "tr", "vi", "zh-Hans", "zh-Hant"];
  var ROOT = "/tessera/get/";

  if (LIVE) {
    var ua = navigator.userAgent || "";
    // iPadOS Safari는 맥 UA를 보내므로 터치 지점 수로 가른다
    var onIos = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    if (onIos) return location.replace(ios);
    if (/Android/.test(ua)) return location.replace(android);
  }

  function resolve(tags) {
    for (var i = 0; i < tags.length; i++) {
      var parts = String(tags[i]).replace(/_/g, "-").toLowerCase().split("-");
      var l = parts[0];
      var sub = parts.slice(1);
      if (!l) continue;
      var id = l;
      if (l === "zh") {
        var hant = sub.indexOf("hant") >= 0 || sub.indexOf("tw") >= 0 || sub.indexOf("hk") >= 0 || sub.indexOf("mo") >= 0;
        id = hant ? "zh-Hant" : "zh-Hans";
      } else if (l === "pt") id = "pt-BR";
      else if (l === "in") id = "id";
      else if (l === "iw") id = "he";
      if (id === "en") return "en";
      if (PAGES.indexOf(id) >= 0) return id;
    }
    return "en";
  }

  var langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "en"];
  var want = resolve(langs);
  var here = document.documentElement.lang || "en";
  if (want === here) return;
  location.replace((want === "en" ? ROOT : ROOT + want + "/") + location.search);
})();
