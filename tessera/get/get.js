// tessera 공유 링크 페이지(tessera/get/와 그 아래 언어 페이지)가 모두 읽는 동작 — firstComMono#3148·#3176.
// 메신저 크롤러는 스크립트를 돌리지 않으므로 카드(OG 메타)는 각 페이지의 언어 그대로 남고, 사람이 열었을 때만 움직인다.
//
// 1. 기기를 보고 스토어로 넘긴다 — LIVE가 false인 동안(스토어 페이지가 열리기 전)과 그 밖의 기기는 페이지가 그대로 보인다.
//    출시 때 LIVE만 true로 바꾼다.
// 2. 아니면 브라우저 언어(navigator.languages)의 페이지로 옮긴다. 없는 언어는 영어(tessera/get/).
//    고르는 규칙은 앱의 Locale.resolve_locale(apps/tessera/godot/ui/locale.gd)과 같다.
(function () {
  var LIVE = false;
  var IOS = "https://apps.apple.com/app/id6821070961";
  var ANDROID = "https://play.google.com/store/apps/details?id=com.firstcom.tessera";
  // 언어 페이지 목록 — 앱 로케일과 같다(Platform.SHARE_PAGES). 영어는 tessera/get/ 그 자체다.
  var PAGES = ["ar", "de", "es", "fr", "he", "hi", "id", "it", "ja", "ko", "nl", "pl", "pt-BR", "ru", "th", "tr", "vi", "zh-Hans", "zh-Hant"];
  var ROOT = "/tessera/get/";

  if (LIVE) {
    var ua = navigator.userAgent || "";
    // iPadOS Safari는 맥 UA를 보내므로 터치 지점 수로 가른다
    var ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    if (ios) return location.replace(IOS);
    if (/Android/.test(ua)) return location.replace(ANDROID);
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
  location.replace(want === "en" ? ROOT : ROOT + want + "/");
})();
