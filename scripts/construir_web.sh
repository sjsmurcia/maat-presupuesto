#!/usr/bin/env bash
# El sitio que sirve Vercel: el Flutter web compilado en frontend/build/web.
set -euo pipefail
flutter="$HOME/flutter/bin/flutter"
cd frontend
"$flutter" config --no-analytics > /dev/null
"$flutter" pub get
"$flutter" build web --release
