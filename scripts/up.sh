#!/usr/bin/env bash
# Brings up the whole Salary Intel stack: db, redis, api, (optionally) frontend.
# Usage:  ./scripts/up.sh [--frontend] [--real]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

API_CONTAINER="salary_intel_api"
WITH_FRONTEND=0
SEED_REAL=""

for a in "$@"; do
  case "$a" in
    --frontend) WITH_FRONTEND=1 ;;
    --real)     SEED_REAL="--real" ;;
    -h|--help)  echo "usage: $0 [--frontend] [--real]"; exit 0 ;;
    *)          echo "unknown flag: $a"; exit 1 ;;
  esac
done

if docker compose version >/dev/null 2>&1; then DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"
else echo "x  Docker Compose not found - install Docker Desktop"; exit 1; fi

say() { printf "\n\033[1m== %s\033[0m\n" "$*"; }

# ---------------------------------------------------------------- 1. preflight
say "1/6  Preflight"
docker info >/dev/null 2>&1 || { echo "x  Docker daemon is not running - start Docker Desktop"; exit 1; }
echo "ok  docker daemon"

[ -f .env ] || { echo "x  .env missing at repo root"; exit 1; }
for k in OPENAI_API_KEY API_KEY; do
  grep -q "^${k}=." .env || { echo "x  .env is missing ${k}"; exit 1; }
done
echo "ok  .env has OPENAI_API_KEY and API_KEY"

API_KEY="$(grep -m1 '^API_KEY=' .env | cut -d= -f2- | sed 's/^["'"'"']//; s/["'"'"']$//' | tr -d '\r')"

# --------------------------------------------------------------- 2. port 6379
say "2/6  Port 6379"
if docker ps --format '{{.Names}}' | grep -qx salary_intel_redis; then
  echo "ok  6379 held by our own redis container"
elif lsof -nP -iTCP:6379 -sTCP:LISTEN >/dev/null 2>&1; then
  if [ "${SKIP_REDIS_STOP:-0}" = "1" ]; then
    echo "!   6379 busy and SKIP_REDIS_STOP=1 - compose will probably fail"
  else
    echo "!   6379 taken by a local redis - stopping it"
    brew services stop redis >/dev/null 2>&1 || true
    sleep 1
    if lsof -nP -iTCP:6379 -sTCP:LISTEN >/dev/null 2>&1; then
      echo "x   still busy - free port 6379 manually and re-run"; exit 1
    fi
    echo "ok  6379 free   (restore later: brew services start redis)"
  fi
else
  echo "ok  6379 free"
fi

# ------------------------------------------------------------- 3. containers
say "3/6  Containers"
$DC up -d --build

# ------------------------------------------------------------- 4. wait for api
say "4/6  Waiting for the API"
for i in $(seq 1 90); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    echo "ok  API healthy after ${i}s"; break
  fi
  if [ "$i" = "90" ]; then
    echo "x   API never came up. Last 40 log lines:"; $DC logs --tail=40 api; exit 1
  fi
  sleep 1
done

# ---------------------------------------------------------------- 5. database
say "5/6  Database"
docker exec "$API_CONTAINER" python -m app.db.init_db

read_count() {
  curl -fsS -H "X-API-Key: ${API_KEY}" http://localhost:8000/api/v1/stats 2>/dev/null \
    | sed -n 's/.*"total_posts":[[:space:]]*\([0-9]*\).*/\1/p'
}

COUNT="$(read_count)"; COUNT="${COUNT:-0}"
if [ "$COUNT" -gt 0 ]; then
  echo "ok  ${COUNT} posts already in the database - skipping seed"
else
  echo "!   database is empty - seeding"
  docker exec "$API_CONTAINER" python -m app.seed ${SEED_REAL}
  COUNT="$(read_count)"; COUNT="${COUNT:-0}"
  echo "ok  ${COUNT} posts after seeding"
fi

# ---------------------------------------------------------------- 6. frontend
say "6/6  Frontend"
if [ "$WITH_FRONTEND" = "1" ]; then
  ( cd frontend && npm install --silent )
  ( cd frontend && nohup npm run dev >/tmp/salary-intel-frontend.log 2>&1 & echo $! > "$ROOT/.frontend.pid" )
  sleep 3
  echo "ok  frontend starting -> http://localhost:3000"
  echo "    log: /tmp/salary-intel-frontend.log   pid: $(cat "$ROOT/.frontend.pid")"
else
  echo "--  skipped (pass --frontend to start it, or run: cd frontend && npm run dev)"
fi

printf "\n\033[1m== Ready\033[0m\n"
echo "  health   http://localhost:8000/health"
echo "  docs     http://localhost:8000/docs"
echo "  posts    ${COUNT}"
echo
echo "  test a query:"
echo "    curl -s -X POST http://localhost:8000/api/v1/query -H 'Content-Type: application/json' -H \"X-API-Key: ${API_KEY}\" -d '{\"query\":\"כמה מרוויח מהנדס תשתיות ענן\"}'"
echo
echo "  run the ablation study (fills the missing rows in your table):"
echo "    docker exec ${API_CONTAINER} python -m app.ablation_study"
