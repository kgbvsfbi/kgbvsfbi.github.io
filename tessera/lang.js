// Tessera 앱 페이지의 언어 — kgbvsfbi/firstComMono#3287.
// 영어 페이지(/tessera/)에 처음 들어오면 브라우저 언어(navigator.languages)의 페이지로 옮긴다. 없는 언어는 영어 그대로다.
// 고르는 규칙은 tessera/get/get.js의 resolve와 같다(앱 Locale.resolve_locale). 발의 언어 목록에서 고르면 그 선택을 기억하고,
// 그 뒤로는 옮기지 않는다. 언어 페이지(/tessera/<lang>/)는 주소가 곧 선택이라 옮기지 않는다.
(function () {
  var KEY = "tessera.lang";
  var PAGES = [
    "ar",
    "de",
    "es",
    "fr",
    "he",
    "hi",
    "id",
    "it",
    "ja",
    "ko",
    "nl",
    "pl",
    "pt-BR",
    "ru",
    "th",
    "tr",
    "vi",
    "zh-Hans",
    "zh-Hant",
  ];
  var ROOT = "/tessera/";

  function load() {
    try {
      return localStorage.getItem(KEY);
    } catch (e) {
      return null; // 저장소를 막은 브라우저 — 매번 브라우저 언어를 따른다
    }
  }
  function save(v) {
    try {
      localStorage.setItem(KEY, v);
    } catch (e) {}
  }

  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a[data-lang]");
    if (a) save(a.getAttribute("data-lang"));
  });

  var here = document.documentElement.lang || "en";
  if (here !== "en" || location.pathname !== ROOT) return;

  function resolve(tags) {
    for (var i = 0; i < tags.length; i++) {
      var parts = String(tags[i]).replace(/_/g, "-").toLowerCase().split("-");
      var l = parts[0];
      var sub = parts.slice(1);
      if (!l) continue;
      var id = l;
      if (l === "zh") {
        var hant =
          sub.indexOf("hant") >= 0 ||
          sub.indexOf("tw") >= 0 ||
          sub.indexOf("hk") >= 0 ||
          sub.indexOf("mo") >= 0;
        id = hant ? "zh-Hant" : "zh-Hans";
      } else if (l === "pt") id = "pt-BR";
      else if (l === "in") id = "id";
      else if (l === "iw") id = "he";
      if (id === "en") return "en";
      if (PAGES.indexOf(id) >= 0) return id;
    }
    return "en";
  }

  var saved = load();
  var want =
    saved ||
    resolve(
      navigator.languages && navigator.languages.length
        ? navigator.languages
        : [navigator.language || "en"],
    );
  if (want !== "en" && PAGES.indexOf(want) >= 0)
    location.replace(ROOT + want + "/" + location.search + location.hash);
})();
