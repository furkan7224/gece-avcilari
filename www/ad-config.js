/* ============================================================
   GECE AVCILARI · REKLAM AYARLARI
   AdMob hesabını açıp reklam birimlerini oluşturduktan sonra
   aşağıdaki kimlikleri kendi kimliklerinle değiştir ve
   testing: false yap. Test kimlikleriyle mağazaya GÖNDERME.
   ============================================================ */
window.GA_AD_CONFIG = {
  testing: true,
  ios: {
    interstitial: "ca-app-pub-3940256099942544/4411468910",   // TEST · Vaka sonu geçiş reklamı
    rewarded:     "ca-app-pub-3940256099942544/1712485313"    // TEST · Ödüllü reklam
  },
  android: {
    interstitial: "ca-app-pub-3940256099942544/1033173712",   // TEST
    rewarded:     "ca-app-pub-3940256099942544/5224354917"    // TEST
  }
};
