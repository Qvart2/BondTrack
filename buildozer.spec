[app]

# (str) Title of your application
title = MyKivyApp

# (str) Package name (это имя пакета, без пробелов и спецсимволов)
package.name = mykivyapp

# (str) Package domain (обычно используется обратный домен, например, org.example)
package.domain = org.example

# (str) Source code where the main.py file is located.
source.dir = .

# (list) Source files to include (оставьте пустым, чтобы включить все файлы)
source.include_exts = py,png,jpg,kv,atlas

# (str) The main .py file to use as the main entry point of your application.
# Если ваш главный файл называется иначе, укажите его здесь.
# Например, если ваш файл называется app.py, измените значение ниже.
# main.py не нужно указывать, если он называется именно так.
# main.entrypoint = main.py

# (list) Application requirements
# Указываем все зависимости: здесь указываем kivy и requests (остальные модули Python, такие как xml или datetime, входят в стандартную библиотеку)
requirements = kivy, requests

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) If True, then the application will run in fullscreen mode.
fullscreen = 0

# (str) Icon of the application (если есть иконка, укажите путь к ней)
# icon.filename = %(source.dir)s/icon.png

[buildozer]

# (str) Log level (0, 1, 2 or 3)
log_level = 2

# (str) Path to build output directory
build_dir = .buildozer

[android]

# (str) Android SDK version to use
sdk = 28

# (str) Android NDK version to use (21b или другую, совместимую с вашим SDK)
ndk = 21b

# (list) Permissions required by your application
android.permissions = INTERNET

# (bool) Whether to copy the whole source directory instead of symlinking
copy_libs = 1
