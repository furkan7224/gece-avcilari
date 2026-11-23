#!/usr/bin/env bash
# GitHub Actions (macOS) üzerinde çağrılır: imzalı iOS yapısı üretip TestFlight'a yükler.
# Gerekli ortam değişkenleri: APP_STORE_KEY_ID, APP_STORE_ISSUER_ID, APPLE_TEAM_ID, APP_STORE_KEY_PATH, BUILD_NUMBER
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Yapı numarası: ${BUILD_NUMBER}"
if ! command -v fastlane >/dev/null 2>&1; then
  echo "fastlane kuruluyor…"
  sudo gem install fastlane -N --quiet || brew install fastlane
fi
fastlane --version | tail -1
export FASTLANE_SKIP_UPDATE_CHECK=1 FASTLANE_HIDE_CHANGELOG=1 FASTLANE_DISABLE_COLORS=1
fastlane ios beta
