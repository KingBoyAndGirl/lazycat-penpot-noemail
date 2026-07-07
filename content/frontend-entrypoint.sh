#!/bin/sh
set -eu

OVERRIDE_DIR=/etc/nginx/overrides/server.d
OVERRIDE_FILE="$OVERRIDE_DIR/mailcatch-locations.conf"
mkdir -p "$OVERRIDE_DIR"
cat > "$OVERRIDE_FILE" <<'EOF'
# Friendly Penpot invitation inbox under /mailcatch.
location = /mailcatch {
    return 302 /mailcatch/;
}

location = /mailcatch/ {
    root /lzcapp/pkg/content;
    try_files /mailcatch-ui.html =404;
    default_type text/html;
    add_header Cache-Control "no-store" always;
}

# Keep the original MailCatcher UI available for debugging.
location = /mailcatch/raw {
    return 302 /mailcatch/raw/;
}

location /mailcatch/raw/ {
    rewrite ^/mailcatch/raw/(.*)$ /mailcatch/$1 break;
    proxy_pass http://penpot-mailcatch:1080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}

# MailCatcher API and assets. MailCatcher is started with --http-path /mailcatch.
location /mailcatch/messages {
    proxy_pass http://penpot-mailcatch:1080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}

location /mailcatch/assets/ {
    proxy_pass http://penpot-mailcatch:1080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
}

location = /mailcatch/favicon.ico {
    proxy_pass http://penpot-mailcatch:1080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

EOF

exec /bin/bash /entrypoint.sh "$@"
