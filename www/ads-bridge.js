/* Gece Avcıları · AdMob köprüsü (Capacitor). Oyun window.GAAds üzerinden reklam ister. */
(function () {
  var C = window.Capacitor;
  if (!C || !C.isNativePlatform || !C.isNativePlatform()) return;
  var A = C.Plugins && C.Plugins.AdMob;
  if (!A) return;
  var cfg = window.GA_AD_CONFIG || {};
  var ids = cfg[C.getPlatform()] || {};
  var started = null, iReady = false, rReady = false;

  function start() {
    if (started) return started;
    started = (async function () {
      try {
        var ci = await A.requestConsentInfo();
        if (ci && ci.isConsentFormAvailable && ci.status === "REQUIRED") ci = await A.showConsentForm();
      } catch (e) {}
      try {
        if (C.getPlatform() === "ios") {
          var st = await A.trackingAuthorizationStatus();
          if (st && st.status === "notDetermined") await A.requestTrackingAuthorization();
        }
      } catch (e) {}
      try { await A.initialize({ maxAdContentRating: "Teen" }); } catch (e) {}
      prepI(); prepR();
    })();
    return started;
  }
  function prepI() { if (!ids.interstitial) return; A.prepareInterstitial({ adId: ids.interstitial, isTesting: !!cfg.testing }).then(function () { iReady = true; }).catch(function () { iReady = false; }); }
  function prepR() { if (!ids.rewarded) return; A.prepareRewardVideoAd({ adId: ids.rewarded, isTesting: !!cfg.testing }).then(function () { rReady = true; }).catch(function () { rReady = false; }); }
  function waitEvent(names, ms) {
    return new Promise(function (res) {
      var hs = [], done = false;
      function fin(v) { if (done) return; done = true; hs.forEach(function (h) { Promise.resolve(h).then(function (x) { x && x.remove && x.remove(); }); }); res(v); }
      names.forEach(function (n) { hs.push(A.addListener(n[0], function () { fin(n[1]); })); });
      setTimeout(function () { fin("timeout"); }, ms);
    });
  }
  window.GAAds = {
    showInterstitial: async function () {
      await start();
      if (!iReady) { prepI(); return; }
      iReady = false;
      var closed = waitEvent([["interstitialAdDismissed", "ok"], ["interstitialAdFailedToShow", "fail"]], 90000);
      try { await A.showInterstitial(); await closed; } catch (e) {}
      prepI();
    },
    showRewarded: async function () {
      await start();
      if (!rReady) {
        try { await A.prepareRewardVideoAd({ adId: ids.rewarded, isTesting: !!cfg.testing }); rReady = true; } catch (e) { prepR(); return false; }
      }
      rReady = false;
      var earned = false;
      var rh = A.addListener("onRewardedVideoAdReward", function () { earned = true; });
      var closed = waitEvent([["onRewardedVideoAdDismissed", "ok"], ["onRewardedVideoAdFailedToShow", "fail"]], 120000);
      try { A.showRewardVideoAd().then(function () { earned = true; }).catch(function () {}); await closed; } catch (e) {}
      Promise.resolve(rh).then(function (x) { x && x.remove && x.remove(); });
      prepR();
      return earned;
    }
  };
  /* İzin pencereleri oyuncu ilk dokunduğunda açılır (Apple ve Google bunu önerir). */
  var once = function () { document.removeEventListener("pointerdown", once, true); setTimeout(start, 600); };
  document.addEventListener("pointerdown", once, true);
})();
