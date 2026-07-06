#!/bin/sh
set -e

echo "[auto-login] Waiting for penpot-backend..."
for i in $(seq 1 60); do
    curl -sf http://penpot-backend:6060/readyz >/dev/null 2>&1 && break
    sleep 2
done

echo "[auto-login] Fetching admin auth token..."
RESP=$(curl -s -D - -X POST http://penpot-backend:6060/api/rpc/command/login-with-password \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@qq.com","password":"admin123"}' 2>&1)

TOKEN=$(echo "$RESP" | grep -i "set-cookie: auth-token=" | sed 's/.*auth-token=\([^;]*\).*/\1/')

if [ -z "$TOKEN" ]; then
    echo "[auto-login] ERROR: Failed to get auth token"
    echo "$RESP"
    exit 1
fi

echo "[auto-login] Got token: ${TOKEN:0:20}..."
sed -i "s/__PENPOT_AUTH_TOKEN__/$TOKEN/g" /etc/nginx/conf.d/default.conf

echo "[auto-login] Starting nginx..."
exec nginx -g "daemon off;"
