[app]
title = GroomerAsist
package.name = GroomerAsist
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,ttf
version = 0.1.0
requirements = python3,kivy==2.3.0,plyer
orientation = portrait
fullscreen = 0
# Optional: place icon at mobile_app/icon.png (512x512) and splash at mobile_app/splash.png (portrait)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/splash.png

[buildozer]
log_level = 2
warn_on_root = 1

[app.android]
android.minapi = 24
android.permissions = CAMERA,READ_MEDIA_IMAGES,VIBRATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# adaptive icons (optional)
# android.adaptive_icon.foreground = %(source.dir)s/icon.png
# android.adaptive_icon.background = #000000
