[app]
title = NEO
package.name = neoia
package.domain = org.neo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 8.0
requirements = python3,kivy,pyjnius,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
