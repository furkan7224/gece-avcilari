#!/usr/bin/env python3
"""Gece Avcıları · App Store Connect API
Kullanım: asc_gece.py setup|status|submit|ship|withdraw
Ortam: APP_STORE_KEY_ID, APP_STORE_ISSUER_ID, APP_STORE_KEY_PATH, APP_ID, VERSION, RELEASE_TYPE
"""
import os, sys, time, hashlib, glob
import jwt, requests

APP_ID = os.environ['APP_ID'].strip()
VERSION = os.environ.get('VERSION', '1.0.0').strip()
RELEASE_TYPE = os.environ.get('RELEASE_TYPE', 'AFTER_APPROVAL').strip() or 'AFTER_APPROVAL'
PREV_APP_ID = os.environ.get('PREV_APP_ID', '6830630846')  # Büyük Yemin: inceleme iletişim bilgisi buradan kopyalanır
BASE = 'https://api.appstoreconnect.apple.com'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'status'
SITE = 'https://furkan7224.github.io/gece-avcilari/'
PRIVACY = SITE + 'gizlilik.html'

INFO = {  # appInfoLocalizations
    'tr': {'name': 'Gece Avcıları', 'subtitle': 'Doğaüstü avcılık ve gizem', 'privacyPolicyUrl': PRIVACY},
    'en-US': {'name': 'Night Hunters: Gece Avcıları', 'subtitle': 'Supernatural mystery hunts', 'privacyPolicyUrl': PRIVACY + '#en'},
}

DESC_TR = """Gece çöktüğünde kasabalar susar. Sen susmazsın.

Gece Avcıları, doğaüstü yaratıkların izini sürdüğün stratejik bir korku ve gizem oyunu. Siyah klasik araban, sahte rozetlerin ve bagajındaki silahlarla dünyanın dört bir yanından gelen vakaları çöz.

VAKAYI ÇÖZ
Morg, olay yeri, tanıklar, arşiv ve yerel bar. Her yerden farklı ipuçları toplanır, kanıt panosuna iğnelenir. Bazı ipuçları seni yanıltır.

YARATIĞI TEŞHİS ET
Vampir mi, kurt adam mı, intikamcı bir ruh mu? 32 yaratık, her birinin kendi zayıf noktası. Yanlış teşhis, bagajda yanlış silah demek.

TAKTİK AVLAR
Her hamle önemli. Yaratığın niyetini oku, ortamı kullan, ritüeli tamamla. Tek başına değilsin: ortağının kendi kişiliği ve ruh hali var, kararlarına itiraz da edebilir.

ORTAĞINLA KONUŞ
Telsizden ortağınla sohbet et: vakayı tartış, şaka yap, dertleş.

AYRICA
• Üç farklı ortak: Cole, Mara ve Kerem
• Yaralar, bulaşmalar ve kurtarma görevleri
• Melek Sariel ile iş birliği
• Silah geliştirme, iksirler ve araç garajı
• Türkçe ve İngilizce, internetsiz oynanabilir

Rozetini tak. Bagajı doldur. Karanlık seni bekliyor."""

DESC_EN = """When night falls, towns go quiet. You don't.

Night Hunters is a strategic horror mystery game about tracking supernatural creatures. With a black classic car, fake badges and a trunk full of weapons, you take on cases from all over the world.

SOLVE THE CASE
The morgue, the crime scene, witnesses, the archives and the local bar. Every place gives different clues, pinned to your evidence board. Some of them will mislead you.

DIAGNOSE THE CREATURE
Vampire, werewolf or vengeful spirit? 32 creatures, each with its own weak spot. A wrong diagnosis means the wrong weapon in the trunk.

TACTICAL HUNTS
Every move matters. Read the creature's intent, use the terrain, complete the ritual. You're not alone: your partner has their own personality and moods, and may push back on your calls.

TALK TO YOUR PARTNER
Chat with your partner on the radio: discuss the case, joke around, share your worries.

ALSO
• Three partners: Cole, Mara and Kerem
• Wounds, infections and rescue missions
• Team up with the angel Sariel
• Weapon upgrades, potions and a garage of cars
• English and Turkish, playable offline

Pin on your badge. Load the trunk. The dark is waiting."""

VERLOC = {
    'tr': {'description': DESC_TR,
           'keywords': 'hayalet,vampir,kurt adam,iblis,korku,gizem,dedektif,strateji,rpg,doğaüstü,melek,cadı,macera,av',
           'promotionalText': 'Siyah klasik bir araba, sahte rozetler ve dünyanın dört bir yanından gelen mühürlü mektuplar. İpuçlarını topla, yaratığı teşhis et ve ortağınla avla.',
           'supportUrl': SITE, 'marketingUrl': SITE},
    'en-US': {'description': DESC_EN,
              'keywords': 'ghost,vampire,werewolf,demon,horror,mystery,detective,strategy,rpg,supernatural,angel,witch,monster',
              'promotionalText': 'A black classic car, fake badges and sealed letters from all over the world. Gather clues, diagnose the creature and hunt it with your partner.',
              'supportUrl': SITE + '#en', 'marketingUrl': SITE + '#en'},
}
SHOTS = {'tr': 'magaza/ios/tr/*.jpg', 'en-US': 'magaza/ios/en/*.jpg'}
SHOT_TYPE = os.environ.get('SHOT_TYPE', 'APP_IPHONE_67')

REVIEW_NOTES = ("Gece Avcıları / Night Hunters is a single-player strategy game. No account or login is required; all progress is stored on the device.\n"
                "The game supports Turkish and English (switch at the top right).\n"
                "Ads: Google AdMob. An interstitial ad may appear after a case ends (never during the first two cases). Rewarded ads are optional: "
                "\"Watch an ad\" to heal heavy wounds, or to get a last chance when both hunters fall during a hunt.\n"
                "App Tracking Transparency is requested on the first tap, before any ad is loaded.\n"
                "There are no in-app purchases in this version.")

AGE = {  # yalnızca API'nin döndürdüğü alanlar gönderilir
    'violenceCartoonOrFantasy': 'FREQUENT_OR_INTENSE',
    'horrorOrFearThemes': 'FREQUENT_OR_INTENSE',
    'alcoholTobaccoOrDrugUseOrReferences': 'INFREQUENT_OR_MILD',
    'gamblingSimulated': 'INFREQUENT_OR_MILD',
    'gunsOrOtherWeapons': 'FREQUENT_OR_INTENSE',
    'matureOrSuggestiveThemes': 'NONE', 'medicalOrTreatmentInformation': 'NONE', 'profanityOrCrudeHumor': 'NONE',
    'sexualContentGraphicAndNudity': 'NONE', 'sexualContentOrNudity': 'NONE', 'violenceRealistic': 'NONE',
    'violenceRealisticProlongedGraphicOrSadistic': 'NONE', 'contests': 'NONE',
    'gambling': False, 'unrestrictedWebAccess': False, 'lootBox': False, 'messagingAndChat': False,
    'userGeneratedContent': False, 'advertising': True, 'parentalControls': False, 'ageAssurance': False,
    'healthOrWellnessTopics': False,
}


def token():
    key = open(os.environ['APP_STORE_KEY_PATH']).read()
    now = int(time.time())
    return jwt.encode({'iss': os.environ['APP_STORE_ISSUER_ID'], 'iat': now, 'exp': now + 1100, 'aud': 'appstoreconnect-v1'},
                      key, algorithm='ES256', headers={'kid': os.environ['APP_STORE_KEY_ID'], 'typ': 'JWT'})


S = requests.Session()


def call(method, path, body=None, ok=(200, 201, 204), soft=False):
    url = path if path.startswith('http') else BASE + path
    r = S.request(method, url, json=body, headers={'Authorization': 'Bearer ' + token(), 'Content-Type': 'application/json'})
    if r.status_code not in ok:
        print('HATA', method, path, r.status_code, r.text[:1500], flush=True)
        if soft:
            return None
        raise SystemExit(1)
    return r.json() if r.text else {}


def log(*a):
    print('•', *a, flush=True)


def app_info():
    infos = call('GET', f'/v1/apps/{APP_ID}/appInfos')['data']
    for i in infos:  # düzenlenebilir olan
        if i['attributes'].get('appStoreState') in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED', 'REJECTED', 'METADATA_REJECTED', None) or \
           i['attributes'].get('state') in ('PREPARE_FOR_SUBMISSION', 'REJECTED', None):
            return i
    return infos[0]


def find_or_create_version():
    r = call('GET', f'/v1/apps/{APP_ID}/appStoreVersions?filter[platform]=IOS&limit=10')
    for v in r['data']:
        if v['attributes']['versionString'] == VERSION:
            return v
    for v in r['data']:
        if v['attributes']['appStoreState'] in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED', 'REJECTED', 'METADATA_REJECTED'):
            return call('PATCH', f"/v1/appStoreVersions/{v['id']}", {'data': {'type': 'appStoreVersions', 'id': v['id'], 'attributes': {'versionString': VERSION}}})['data']
    v = call('POST', '/v1/appStoreVersions', {'data': {'type': 'appStoreVersions', 'attributes': {'platform': 'IOS', 'versionString': VERSION, 'releaseType': RELEASE_TYPE},
                                                        'relationships': {'app': {'data': {'type': 'apps', 'id': APP_ID}}}}})['data']
    log('Sürüm oluşturuldu', VERSION)
    return v


def setup_app_info():
    info = app_info()
    iid = info['id']
    call('PATCH', f'/v1/appInfos/{iid}', {'data': {'type': 'appInfos', 'id': iid, 'relationships': {
        'primaryCategory': {'data': {'type': 'appCategories', 'id': 'GAMES'}},
        'primarySubcategoryOne': {'data': {'type': 'appCategories', 'id': 'GAMES_ROLE_PLAYING'}},
        'primarySubcategoryTwo': {'data': {'type': 'appCategories', 'id': 'GAMES_ADVENTURE'}}}}}, soft=True)
    log('Kategori: Oyunlar › Rol Yapma, Macera')
    locs = {l['attributes']['locale']: l for l in call('GET', f'/v1/appInfos/{iid}/appInfoLocalizations')['data']}
    for loc, attrs in INFO.items():
        if loc in locs:
            call('PATCH', f"/v1/appInfoLocalizations/{locs[loc]['id']}", {'data': {'type': 'appInfoLocalizations', 'id': locs[loc]['id'], 'attributes': attrs}}, soft=True)
        else:
            call('POST', '/v1/appInfoLocalizations', {'data': {'type': 'appInfoLocalizations', 'attributes': dict(attrs, locale=loc),
                  'relationships': {'appInfo': {'data': {'type': 'appInfos', 'id': iid}}}}}, soft=True)
        log('Uygulama bilgisi:', loc, attrs['name'])
    # yaş derecelendirmesi
    ar = call('GET', f'/v1/appInfos/{iid}/ageRatingDeclaration', soft=True)
    if ar and ar.get('data'):
        cur = ar['data']['attributes']
        attrs = {k: v for k, v in AGE.items() if k in cur and (isinstance(cur[k], bool) == isinstance(v, bool) or cur[k] is None)}
        r = call('PATCH', f"/v1/ageRatingDeclarations/{ar['data']['id']}", {'data': {'type': 'ageRatingDeclarations', 'id': ar['data']['id'], 'attributes': attrs}}, soft=True)
        log('Yaş derecelendirmesi', 'kaydedildi' if r else 'KAYDEDİLEMEDİ (App Store Connect’ten elle doldur)', '| alanlar:', sorted(cur.keys()))
    # içerik hakları
    call('PATCH', f'/v1/apps/{APP_ID}', {'data': {'type': 'apps', 'id': APP_ID, 'attributes': {'contentRightsDeclaration': 'DOES_NOT_USE_THIRD_PARTY_CONTENT'}}}, soft=True)
    log('İçerik hakları: üçüncü taraf içerik yok')


def setup_price():
    have = call('GET', f'/v1/apps/{APP_ID}/appPriceSchedule', ok=(200, 404), soft=True)
    if have and have.get('data'):
        log('Fiyat planı zaten var')
        return
    pts = call('GET', f'/v1/apps/{APP_ID}/appPricePoints?filter[territory]=USA&limit=200', soft=True)
    free = [p for p in (pts or {}).get('data', []) if float(p['attributes'].get('customerPrice') or 0) == 0]
    if not free:
        log('Ücretsiz fiyat noktası bulunamadı; fiyatı elle ayarla')
        return
    body = {'data': {'type': 'appPriceSchedules', 'relationships': {
        'app': {'data': {'type': 'apps', 'id': APP_ID}},
        'baseTerritory': {'data': {'type': 'territories', 'id': 'USA'}},
        'manualPrices': {'data': [{'type': 'appPrices', 'id': '${price1}'}]}}},
        'included': [{'type': 'appPrices', 'id': '${price1}', 'attributes': {'startDate': None},
                      'relationships': {'appPricePoint': {'data': {'type': 'appPricePoints', 'id': free[0]['id']}}}}]}
    r = call('POST', '/v1/appPriceSchedules', body, soft=True)
    log('Fiyat: Ücretsiz', 'ayarlandı' if r else 'AYARLANAMADI (elle ayarla)')


def setup_version(v):
    vid = v['id']
    call('PATCH', f'/v1/appStoreVersions/{vid}', {'data': {'type': 'appStoreVersions', 'id': vid, 'attributes': {
        'releaseType': RELEASE_TYPE, 'copyright': '2026 Guler Game Studios'}}}, soft=True)
    locs = {l['attributes']['locale']: l for l in call('GET', f'/v1/appStoreVersions/{vid}/appStoreVersionLocalizations')['data']}
    for loc, attrs in VERLOC.items():
        if loc in locs:
            lid = locs[loc]['id']
            call('PATCH', f'/v1/appStoreVersionLocalizations/{lid}', {'data': {'type': 'appStoreVersionLocalizations', 'id': lid, 'attributes': attrs}})
        else:
            lid = call('POST', '/v1/appStoreVersionLocalizations', {'data': {'type': 'appStoreVersionLocalizations', 'attributes': dict(attrs, locale=loc),
                        'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': vid}}}}})['data']['id']
        log('Mağaza metni:', loc)
        upload_shots(lid, loc)
    review_detail(vid)


def upload_shots(lid, loc):
    files = sorted(glob.glob(SHOTS[loc]))
    sets = call('GET', f'/v1/appStoreVersionLocalizations/{lid}/appScreenshotSets')['data']
    st = next((s for s in sets if s['attributes']['screenshotDisplayType'] == SHOT_TYPE), None)
    if st is None:
        st = call('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': SHOT_TYPE},
                  'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': lid}}}}})['data']
    have = call('GET', f"/v1/appScreenshotSets/{st['id']}/appScreenshots?limit=20")['data']
    if len([h for h in have if (h['attributes'].get('assetDeliveryState') or {}).get('state') in ('COMPLETE', 'UPLOAD_COMPLETE')]) >= len(files):
        log('Ekran görüntüleri zaten yüklü:', loc)
        return
    for h in have:
        call('DELETE', f"/v1/appScreenshots/{h['id']}", soft=True)
    for f in files:
        data = open(f, 'rb').read()
        sc = call('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(f), 'fileSize': len(data)},
                  'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': st['id']}}}}})['data']
        for op in sc['attributes']['uploadOperations']:
            hdr = {h['name']: h['value'] for h in op.get('requestHeaders', [])}
            chunk = data[op['offset']:op['offset'] + op['length']]
            r = requests.request(op['method'], op['url'], data=chunk, headers=hdr)
            if r.status_code >= 300:
                print('HATA yükleme', f, r.status_code, r.text[:300]); raise SystemExit(1)
        call('PATCH', f"/v1/appScreenshots/{sc['id']}", {'data': {'type': 'appScreenshots', 'id': sc['id'], 'attributes': {
            'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
        log('Ekran görüntüsü yüklendi:', loc, os.path.basename(f))


def review_detail(vid):
    contact = {}
    try:
        pv = call('GET', f'/v1/apps/{PREV_APP_ID}/appStoreVersions?filter[platform]=IOS&limit=1')['data']
        if pv:
            rd = call('GET', f"/v1/appStoreVersions/{pv[0]['id']}/appStoreReviewDetail", ok=(200, 404), soft=True)
            if rd and rd.get('data'):
                a = rd['data']['attributes']
                contact = {k: a.get(k) for k in ('contactFirstName', 'contactLastName', 'contactPhone', 'contactEmail') if a.get(k)}
    except SystemExit:
        pass
    attrs = dict(contact, demoAccountRequired=False, notes=REVIEW_NOTES)
    cur = call('GET', f'/v1/appStoreVersions/{vid}/appStoreReviewDetail', ok=(200, 404), soft=True)
    if cur and cur.get('data'):
        call('PATCH', f"/v1/appStoreReviewDetails/{cur['data']['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': cur['data']['id'], 'attributes': attrs}}, soft=True)
    else:
        call('POST', '/v1/appStoreReviewDetails', {'data': {'type': 'appStoreReviewDetails', 'attributes': attrs,
              'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': vid}}}}}, soft=True)
    log('İnceleme bilgileri:', 'iletişim Büyük Yemin’den kopyalandı' if contact else 'İLETİŞİM BİLGİSİ EKSİK (elle doldur)')


def find_build(wait=False):
    for _ in range(170 if wait else 1):
        r = call('GET', f'/v1/builds?filter[app]={APP_ID}&filter[preReleaseVersion.version]={VERSION}&sort=-uploadedDate&limit=5')
        bs = [b for b in r['data'] if b['attributes']['processingState'] == 'VALID']
        if bs:
            b = bs[0]
            if b['attributes'].get('usesNonExemptEncryption') is None:
                call('PATCH', f"/v1/builds/{b['id']}", {'data': {'type': 'builds', 'id': b['id'], 'attributes': {'usesNonExemptEncryption': False}}}, soft=True)
            log('Yapı', VERSION, '(', b['attributes']['version'], ')')
            return b
        log('Geçerli yapı yok:', [(b['attributes']['version'], b['attributes']['processingState']) for b in r['data']])
        if wait:
            time.sleep(30)
    raise SystemExit(1)


def setup():
    setup_app_info()
    setup_price()
    setup_version(find_or_create_version())
    log('KURULUM TAMAM. App Store Connect’te kalan: Uygulama Gizliliği formu ve ülke erişilebilirliği (bir kez).')


def status():
    a = call('GET', f'/v1/apps/{APP_ID}')['data']['attributes']
    log('Uygulama', a.get('name'), a.get('bundleId'))
    for v in call('GET', f'/v1/apps/{APP_ID}/appStoreVersions?filter[platform]=IOS&limit=5')['data']:
        log('Sürüm', v['attributes']['versionString'], v['attributes']['appStoreState'], v['attributes'].get('releaseType'))
    for b in call('GET', f'/v1/builds?filter[app]={APP_ID}&sort=-uploadedDate&limit=5')['data']:
        log('Yapı', b['attributes']['version'], b['attributes']['processingState'])
    for s in call('GET', f'/v1/reviewSubmissions?filter[app]={APP_ID}&limit=5')['data']:
        log('İnceleme kaydı', s['id'], s['attributes'].get('state'), s['attributes'].get('submittedDate'))


def submit(wait=False):
    b = find_build(wait)
    v = find_or_create_version()
    setup_version(v)
    call('PATCH', f"/v1/appStoreVersions/{v['id']}/relationships/build", {'data': {'type': 'builds', 'id': b['id']}})
    log('Yapı sürüme bağlandı')
    subs = call('GET', f'/v1/reviewSubmissions?filter[app]={APP_ID}&filter[platform]=IOS&filter[state]=READY_FOR_REVIEW&limit=5')['data']
    if subs:
        sid = subs[0]['id']
    else:
        sid = call('POST', '/v1/reviewSubmissions', {'data': {'type': 'reviewSubmissions', 'attributes': {'platform': 'IOS'},
                    'relationships': {'app': {'data': {'type': 'apps', 'id': APP_ID}}}}})['data']['id']
    items = call('GET', f'/v1/reviewSubmissions/{sid}/items')['data']
    if not any(i.get('relationships', {}).get('appStoreVersion', {}).get('data') for i in items):
        call('POST', '/v1/reviewSubmissionItems', {'data': {'type': 'reviewSubmissionItems', 'relationships': {
            'reviewSubmission': {'data': {'type': 'reviewSubmissions', 'id': sid}},
            'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': v['id']}}}}})
    call('PATCH', f'/v1/reviewSubmissions/{sid}', {'data': {'type': 'reviewSubmissions', 'id': sid, 'attributes': {'submitted': True}}})
    log('GÖNDERİLDİ: sürüm', VERSION, 'Apple incelemesine gitti')
    status()


def withdraw():
    for x in call('GET', f'/v1/reviewSubmissions?filter[app]={APP_ID}&filter[platform]=IOS&limit=10')['data']:
        if x['attributes'].get('state') in ('WAITING_FOR_REVIEW', 'IN_REVIEW', 'UNRESOLVED_ISSUES'):
            call('PATCH', f"/v1/reviewSubmissions/{x['id']}", {'data': {'type': 'reviewSubmissions', 'id': x['id'], 'attributes': {'canceled': True}}})
            log('İnceleme geri çekildi', x['id'])
    status()


{'setup': setup, 'status': status, 'submit': submit, 'ship': lambda: submit(True), 'withdraw': withdraw}[MODE]()
