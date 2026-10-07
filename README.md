# VPN Client

Android-клиент для своего сервера **AmneziaWG**. Ключ берётся из админ-панели: ссылка `vpn://` или файл `.conf`. Приложение само VPN-сервер не поднимает и другие протоколы не подключает.

Репозиторий приватный. Ключи клиентов и параметры сервера в git не входят — они остаются только на телефоне после импорта.

## Что умеет

- Подключение и отключение AmneziaWG, в том числе AmneziaWG 3.
- Обычный WireGuard, если в ключе нет обфускации.
- Импорт: QR из панели, вставка текста, файл, ссылка `vpn://` и «Поделиться».
- Ссылка на чат поддержки: [t.me/Maer_VPN_bot](https://t.me/Maer_VPN_bot).
- Несколько серверов, переключение активного.
- Статус, время сессии и счётчики трафика. Если туннель уже поднят, экран показывает «Подключено» и после повторного входа в приложение.
- Тёмная тема в цветах админ-панели.

OpenVPN, XRay, IPsec и установка контейнера на сервер сюда не входят.

## Сборка

Нужны JDK 17 и Android SDK (`ANDROID_HOME`).

```bat
gradlew.bat :app:assembleDebug
gradlew.bat :app:testDebugUnitTest
```

Подписанный выпуск собирается, если рядом с проектом лежит `keystore.properties` (в git он не попадает):

```properties
storeFile=release/vpn-client-release.jks
storePassword=...
keyAlias=vpn-client
keyPassword=...
```

```bat
gradlew.bat :app:assembleRelease
```

APK: `app/build/outputs/apk/release/app-release.apk`.

Минимальная версия Android — 8.0 (API 26).

## Туннель

Каталог `tunnel` — исходники и `libwg-go.so` из [amneziawg-android](https://github.com/amnezia-vpn/amneziawg-android) `v3.1.20260814`. Лицензия Apache 2.0, текст в `tunnel/COPYING`.
