#!/usr/bin/env bash

# Machina Intelligence deployment script (server-side)
# Usage: ./deploy.sh

set -euo pipefail

PROJECT_PATH="/opt/machina"
WEB_ROOT="/var/www/machina-intelligence"

echo "Starting Machina deployment..."

cd "$PROJECT_PATH"

echo "Stashing local server changes (if any)..."
git stash --include-untracked || true

echo "Pulling latest code from GitHub..."
git pull origin main

echo "Installing dependencies..."
npm ci

echo "Building production assets..."
npm run build

echo "Syncing dist to web root..."
mkdir -p "$WEB_ROOT"
rsync -av --delete dist/ "$WEB_ROOT/"

echo "Setting safe web permissions..."
chown -R www-data:www-data "$WEB_ROOT"
find "$WEB_ROOT" -type d -exec chmod 755 {} \;
find "$WEB_ROOT" -type f -exec chmod 644 {} \;

if command -v systemctl >/dev/null 2>&1; then
  echo "Reloading nginx (if active)..."
  systemctl reload nginx || true
fi

echo "Deployment complete."
