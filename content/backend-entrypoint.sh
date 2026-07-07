#!/bin/bash
set -euo pipefail

ADMIN_EMAIL="${PENPOT_ADMIN_EMAIL:-admin@qq.com}"
ADMIN_PASSWORD="${PENPOT_ADMIN_PASSWORD:-admin123}"
ADMIN_FULLNAME="${PENPOT_ADMIN_FULLNAME:-Admin}"

echo "[backend-entrypoint] starting Penpot backend"
/bin/bash run.sh &
backend_pid=$!

python3 - "$ADMIN_EMAIL" "$ADMIN_PASSWORD" "$ADMIN_FULLNAME" <<'PYCODE' &
import json, socket, sys, time
email, password, fullname = sys.argv[1], sys.argv[2], sys.argv[3]
host, port = '127.0.0.1', 6063

def prepl(cmd, params):
    s = socket.create_connection((host, port), 10)
    try:
        f = s.makefile('rw')
        json.dump({'cmd': cmd, 'params': params}, f)
        f.write('\n')
        f.flush()
        line = f.readline()
        if not line:
            raise RuntimeError('empty PREPL response')
        return json.loads(line)
    finally:
        s.close()

for i in range(90):
    try:
        prepl('echo', {})
        print('[init-admin] PREPL ready')
        break
    except Exception as exc:
        if i in (0, 5, 15, 30, 60):
            print(f'[init-admin] waiting PREPL: {exc}', file=sys.stderr)
        time.sleep(2)
else:
    print('[init-admin] PREPL not ready, skip admin init', file=sys.stderr)
    sys.exit(0)

resp = prepl('create-profile', {
    'fullname': fullname,
    'email': email,
    'password': password,
})
print('[init-admin] create-profile response:', json.dumps(resp, ensure_ascii=False))
err = resp.get('err')
if err and err.get('code') != 'email-already-exists':
    print('[init-admin] unexpected error:', json.dumps(err, ensure_ascii=False), file=sys.stderr)
PYCODE

wait "$backend_pid"
