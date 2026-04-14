[app]
# (str) Title of your application
title = Talos-ai

# (str) Package name (no spaces, only letters and dots)
package.name = Talos.ai

# (str) Package domain (usually your website in reverse, e.g., com.example)
package.domain = com.test.talos

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (include your python, images, etc.)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Add any extra libraries here (e.g., requirements = python3,kivy,requests)
requirements = python3,kivy,internet

# (list) Supported orientations
orientation = portrait

# -----------------------------------------------------------------------------
# Android specific configurations (Critical for Google Play)
# -----------------------------------------------------------------------------

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API. Google Play requires API 34+ for 2024/2025.
android.api = 35

# (int) Minimum API your app will support (21 is usually safe for older phones)
android.minapi = 21

# (str) Android NDK version to use (25b is a stable choice for modern builds)
android.ndk = 25b

# (str) The format used to package the app. 
# "aab" is required for Google Play; "apk" is for direct install.
android.release_artifact = aab

# (list) Permissions
android.permissions = INTERNET

# (str) python-for-android branch to use (develop is often more stable for AAB)
p4a.branch = develop

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off)
warn_on_root = 1
