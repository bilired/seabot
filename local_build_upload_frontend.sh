#!/usr/bin/env bash

set -euo pipefail

# Local frontend build + upload + atomic release switch.
# Usage example:
#   REMOTE_HOST="root@1.2.3.4" REMOTE_BASE_DIR="/www/wwwroot/seabot-frontend" bash local_build_upload_frontend.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${FRONTEND_DIR:-$PROJECT_ROOT/art-design-pro}"

REMOTE_HOST="${REMOTE_HOST:-}"
REMOTE_BASE_DIR="${REMOTE_BASE_DIR:-/www/wwwroot/seabot-frontend}"
RELEASES_TO_KEEP="${RELEASES_TO_KEEP:-5}"
RELOAD_NGINX="${RELOAD_NGINX:-false}"

# If RELOAD_NGINX=true, this command will run on remote host.
NGINX_RELOAD_CMD="${NGINX_RELOAD_CMD:-sudo systemctl reload nginx}"

log() {
  printf "[INFO] %s\n" "$1"
}

err() {
  printf "[ERROR] %s\n" "$1" >&2
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Missing command: $1"
    exit 1
  fi
}

validate() {
  if [[ -z "$REMOTE_HOST" ]]; then
    err "REMOTE_HOST is required. Example: REMOTE_HOST='root@1.2.3.4'"
    exit 1
  fi

  if [[ ! -d "$FRONTEND_DIR" ]] || [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    err "Frontend directory invalid: $FRONTEND_DIR"
    exit 1
  fi

  need_cmd ssh
  need_cmd scp
  need_cmd tar
  need_cmd date
}

install_and_build() {
  log "Installing dependencies and building frontend locally..."

  pushd "$FRONTEND_DIR" >/dev/null

  if command -v pnpm >/dev/null 2>&1 && [[ -f "pnpm-lock.yaml" ]]; then
    log "Using pnpm"
    pnpm install --frozen-lockfile
    pnpm build
  elif [[ -f "package-lock.json" ]]; then
    log "Using npm ci"
    npm ci
    npm run build
  else
    log "Using npm install"
    npm install
    npm run build
  fi

  if [[ ! -d "dist" ]]; then
    err "Build failed: dist directory not found"
    popd >/dev/null
    exit 1
  fi

  popd >/dev/null
}

package_dist() {
  TS="$(date +%Y%m%d-%H%M%S)"
  RELEASE_NAME="release-$TS"
  ARCHIVE_PATH="/tmp/$RELEASE_NAME.tar.gz"

  log "Packaging dist to $ARCHIVE_PATH"
  tar -C "$FRONTEND_DIR/dist" -czf "$ARCHIVE_PATH" .
}

upload_and_activate() {
  REMOTE_TMP_ARCHIVE="/tmp/$RELEASE_NAME.tar.gz"

  log "Uploading archive to $REMOTE_HOST:$REMOTE_TMP_ARCHIVE"
  scp "$ARCHIVE_PATH" "$REMOTE_HOST:$REMOTE_TMP_ARCHIVE"

  log "Activating new release on remote server"
  ssh "$REMOTE_HOST" "
    set -euo pipefail
    mkdir -p '$REMOTE_BASE_DIR/releases'
    mkdir -p '$REMOTE_BASE_DIR/shared'
    RELEASE_DIR='$REMOTE_BASE_DIR/releases/$RELEASE_NAME'
    mkdir -p \"\$RELEASE_DIR\"
    tar -xzf '$REMOTE_TMP_ARCHIVE' -C \"\$RELEASE_DIR\"
    ln -sfn \"\$RELEASE_DIR\" '$REMOTE_BASE_DIR/current'
    rm -f '$REMOTE_TMP_ARCHIVE'

    if [[ '$RELEASES_TO_KEEP' =~ ^[0-9]+$ ]] && [[ '$RELEASES_TO_KEEP' -gt 0 ]]; then
      ls -1dt '$REMOTE_BASE_DIR'/releases/* 2>/dev/null | tail -n +$((RELEASES_TO_KEEP + 1)) | xargs -r rm -rf
    fi
  "

  if [[ "$RELOAD_NGINX" == "true" ]]; then
    log "Reloading nginx on remote host"
    ssh "$REMOTE_HOST" "$NGINX_RELOAD_CMD"
  fi

  rm -f "$ARCHIVE_PATH"
}

print_done() {
  cat <<EOF

Done.
New release: $RELEASE_NAME
Remote current path: $REMOTE_BASE_DIR/current

Make sure your nginx root points to:
  $REMOTE_BASE_DIR/current

EOF
}

main() {
  validate
  install_and_build
  package_dist
  upload_and_activate
  print_done
}

main "$@"
