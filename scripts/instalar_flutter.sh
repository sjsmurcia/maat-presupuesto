#!/usr/bin/env bash
# Vercel no trae Flutter: se baja la misma versión que usa el grupo (frontend/.fvmrc).
set -euo pipefail
dnf install -y unzip xz > /dev/null
version=$(python3 -c "import json; print(json.load(open('frontend/.fvmrc'))['flutter'])")
git clone --quiet --depth 1 --branch "$version" https://github.com/flutter/flutter.git "$HOME/flutter"
