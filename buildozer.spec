[app]
# Название приложения
title = MyKivyApp
# Имя пакета (без пробелов и спецсимволов)
package.name = mykivyapp
# Домен пакета
package.domain = org.example
# Версия приложения
version = 0.1
# Директория с исходным кодом
source.dir = .
# Включаем расширения, которые понадобятся (например, py, kv, png, jpg)
source.include_exts = py,kv,png,jpg,atlas
# Точка входа (если main.py – основной файл, можно не указывать)
# main.entrypoint = main.py
# Зависимости: указываем только внешние пакеты, встроенные модули Python не требуются
requirements = kivy, requests
# Ориентация экрана
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
build_dir = .buildozer

[android]
# Минимальная версия API
android.minapi = 21
# API для сборки (например, 33)
android.api = 33
# Версия Android SDK
android.sdk = 31
# Версия NDK
android.ndk = 23b
# Разрешения, необходимые вашему приложению
android.permissions = INTERNET
copy_libs = 1
