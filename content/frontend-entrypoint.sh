#!/bin/sh
set -eu

OVERRIDE_DIR=/etc/nginx/overrides/server.d
OVERRIDE_FILE="$OVERRIDE_DIR/mailcatch-locations.conf"
mkdir -p "$OVERRIDE_DIR"
cat > "$OVERRIDE_FILE" <<'EOF'
# MailCatcher UI under /mailcatch.
# MailCatcher is started with --http-path /mailcatch, so it emits /mailcatch/assets URLs.
# Preserve the browser-visible /mailcatch prefix when proxying to MailCatcher.
location = /mailcatch {
    return 302 /mailcatch/;
}

location /mailcatch/ {
    proxy_pass http://penpot-mailcatch:1080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}
EOF

exec /bin/bash /entrypoint.sh "$@"
