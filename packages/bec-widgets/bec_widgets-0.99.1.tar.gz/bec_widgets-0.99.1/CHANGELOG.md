# CHANGELOG

## v0.99.1 (2024-08-27)

### Fix

* fix(crosshair): emit all crosshair events, not just line coordinates ([`2265458`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2265458dcc57970db18c62619f5877d542d72e81))

## v0.99.0 (2024-08-25)

### Documentation

* docs(darkmodebutton): added dark mode button docs ([`406c263`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/406c263746f0e809c1a4d98356c48f40428c23d7))

### Feature

* feat(darkmodebutton): added button to toggle between dark and light mode ([`cc8c166`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/cc8c166b5c1d37e0f64c83801b2347a54a6550b6))

### Fix

* fix(toggle): emit state change ([`c4f3308`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/c4f3308dc0c3e4b2064760ccd7372d71b3e49f96))

### Refactor

* refactor(darkmodebutton): renamed set_dark_mode_enabled to toggle_dark_mode ([`c70724a`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/c70724a456900bcb06b040407a2c5d497e49ce77))

### Test

* test(dark_mode_button): added tests for dark mode button ([`df35aab`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/df35aabff30c5d00b1c441132bd370446653741e))

## v0.98.0 (2024-08-25)

### Feature

* feat(themes): added set_theme method ([`2b4449a`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2b4449afebdda0a97f95712a1353cf40ec55c283))

### Fix

* fix(toolbar): removed hardcoded color values ([`afdf4e8`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/afdf4e8782a22566932180224fa1c924d24c810f))

* fix: transitioning to material icons ([`2a82032`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2a82032644a84e38df04e2035a6aa63f4a046360))

* fix(dock_area): transitioned to MaterialIconAction ([`88a2f66`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/88a2f667588e9aeb34ae556fa327898824052bc3))

* fix: fix color palette if qtheme was not called ([`3f3b207`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/3f3b207295ebd406ebaeecee465c774965161b8b))

* fix(figure): removed theme from figure init ([`e42b84c`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/e42b84c63650297d67feffccc02a2c2ba111ca79))

* fix: use globally set theme instead of the internal bec widgets theme ([`77c5aa7`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/77c5aa741cf1f5b969a42aa878aa2965176dbf41))

* fix(waveform): fixed icon appearance ([`36ad464`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/36ad4641594b67c9b789515c28f7db78a12757ee))

### Refactor

* refactor(waveform): use set theme for demo ([`44cfda1`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/44cfda1c07306669c9a4e09706d95e6b91dee370))

## v0.97.0 (2024-08-23)

### Feature

* feat(designer): added designer icon factory ([`82a55dd`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/82a55ddf3eafb589cb63408db1c0e7e5c9d629da))

### Fix

* fix(toolbar icon): fixed material icon toolbar for theme changes ([`3ecbd60`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/3ecbd60627994417c9175364e5909710dbcdceb2))

## v0.96.3 (2024-08-23)

### Documentation

* docs(dispatcher): docs added ([`dd7c71b`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/dd7c71bb1e0b7ef5398b1e1a05fc1147c772420a))

### Fix

* fix: minor fixes for type annotations ([`8c2e7c8`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/8c2e7c82592ace50e4e1f47e392a0ddc988f57ae))

## v0.96.2 (2024-08-22)

### Fix

* fix(waveform): validation of custom curves removed ([`af28574`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/af28574bd58457a05f1269f121db01ad627b5769))

* fix(waveform): skip validation for curves that are not BECCurve instances ([`617db36`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/617db36ed4932c8a0633724079b695bc67d5c77b))

## v0.96.1 (2024-08-22)

### Ci

* ci: fail pytest after 2 failed tests ([`f0203d9`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/f0203d9bf60c4975ba5ab93a057d9091762454d5))

### Fix

* fix(crosshair): update markers if necessary ([`4473805`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/44738057a36f5de2bbb55affdd309f92286d4a0f))

* fix(waveform_widget): fixed icon appearance ([`f98a9f9`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/f98a9f9771b93226d47830aa52f45739624f51b4))

* fix: bubble-up signals ([`2fe72c9`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2fe72c9ccb71bcb196a1b78197b73acf9aa3f506))

* fix(crosshair): fixed crosshair for image and waveforms ([`37835cb`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/37835cbf76ca3ba1081f514ee7793244ac500e7f))

## v0.96.0 (2024-08-22)

### Documentation

* docs(scan_control): added designer options ([`9d7718c`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/9d7718c3d9badf14150174410b9958a3134a1e23))

### Feature

* feat(scan_control): added the ability to configure the scan control widget from designer ([`9d8fb0b`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/9d8fb0b761efa92972399bcd9aea28e956074380))

## v0.95.1 (2024-08-22)

### Documentation

* docs: links section added ([`2bf5c70`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2bf5c7096e7d822713e1b50bde89f072e6356e17))

### Fix

* fix(docs): changed link to scan gui config in main docs ([`640464a`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/640464a6543b2111bdb58d0174f2ce86c5836cbe))

### Refactor

* refactor: removed designer pngs ([`84abe46`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/84abe460502d838aac41bb8ff63d93c9fcec9214))

* refactor: moved to dynamically loaded material design icons ([`1d2afaa`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/1d2afaa09e64b7f714d72796e87e2cb49b2a75a7))

## v0.95.0 (2024-08-21)

### Documentation

* docs(device_browser): added user docs ([`2c31cc9`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/2c31cc90ae751f14a653cbbdd6c353d6359aaafe))

* docs(user): widget gallery with documentation added ([`7357f3d`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/7357f3d2a189f9f04954a027f39ce07c394d57ec))

* docs: added sphinx-inline-tabs as sphinx dependency ([`e9ecd26`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/e9ecd268c602ea9572df0e8d508e49ee62d0c170))

* docs(cards): changed index cards to custom css class instead of overwriting the default sd-card theme ([`91ba30e`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/91ba30e8d054a9c7f6c6d98b21113a5d0b1bbbbb))

### Feature

* feat(cli): added device_browser to cli ([`196504b`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/196504b533367a899c19b88af4ccd5b39dc46aac))

* feat(widgets): added device_browser widget ([`73f5a2f`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/73f5a2f085b289ac18fa8a918b6ad7cfed595fb4))

### Fix

* fix(device_browser): fixed plugin assignment for designer ([`6500393`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/650039303aae9bbec62c676285938416fff146ce))

### Refactor

* refactor(docs): review response ([`4790afd`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/4790afde3d61fc9beb073c2775c339d4f80779e3))

### Test

* test: added test for device browser ([`e870e5b`](https://gitlab.psi.ch/bec/bec_widgets/-/commit/e870e5ba083c61df581c9c0305adabe72967f997))
