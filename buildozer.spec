[app]
title = Battery Guardian Pro
package.name = batteryguardian
package.domain = org.guardian
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3
version = 1.0
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = BATTERY_STATS
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
