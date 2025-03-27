[app]
title = MyKivyApp
package.name = mykivyapp
package.domain = org.example
version = 0.1
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
requirements = kivy, requests
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
build_dir = .buildozer

[android]
android.minapi = 21
android.api = 33
android.sdk = 31
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk = 21.4.7075529
android.permissions = INTERNET
copy_libs = 1
