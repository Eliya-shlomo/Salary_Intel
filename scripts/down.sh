#!/usr/bin/env bash
# Tears down the Salary Intel stack.
# Usage:  ./scripts/down.sh [--wipe] [--restore-redis]
#   (no flags)        stop containers, KEEP the postgres volume and all posts
#   --wipe            also delete the volume - destroys every ingested post
#   --restore-redis   start the local brew redis again
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WIPE=0
RESTORE_REDIS=0

for a in "$@"; do
  case "$a" in
    --wipe)          WIPE=1 ;;
    --restore-redis) RESTORE_REDIS=1 ;;
    -h|--help)       sed -n '2,7p' "$0"; exit 0 ;;
    *)               echo "unknown flag: $a"; exit 1 ;;
  esac
done

if docker compose version >/dev/null 2>&1; then DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"
else echo "x  Docker Compose not found"; exit 1; fi

# --------------------------------------------------------------- frontend
if [ -f .frontend.pid ]; then
  PID="$(cat .frontend.pid)"
  if kill "$PID" 2>/dev/null; then echo "ok  stopped frontend (pid $PID)"
  else echo "--  frontend pid $PID was not running"; fi
  rm -f .frontend.pid
fi

# -------------------------------------------------------------- containers
if [ "$WIPE" = "1" ]; then
  echo
  echo "!!  --wipe DELETES the postgres volume and every ingested post."
  echo "!!  app/generated_test_cases.json references those post ids -"
  echo "!!  the ablation study will stop working until you regenerate it."
  echo
  printf "Type DELETE to confirm: "
  read -r ans
  if [ "$ans" != "DELETE" ]; then echo "aborted - nothing removed"; exit 1; fi
  $DC down -v
  echo "ok  containers and postgres volume removed"
else
  $DC down
  echo "ok  containers stopped - postgres volume kept"
fi

# ------------------------------------------------------------- local redis
if [ "$RESTORE_REDIS" = "1" ]; then
  if brew services start redis >/dev/null 2>&1; then echo "ok  local redis restarted"
  else echo "--  could not restart local redis (brew services start redis)"; fi
fi
