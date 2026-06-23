#!/usr/bin/env bash
# Council preview server. NOT a custom server - just a launcher around
# `python3 -m http.server` bound to an OS-chosen free port (loopback only).
#
# Lifecycle (per the panel's verdict):
#   - dynamic port: the OS picks a free one (no hardcoded 8777).
#   - self-cleaning: `start` kills the previously-recorded server first, so at
#     most ONE preview server ever runs (handles crashed/abandoned prior runs).
#   - NO auto-stop when a session finishes: status=done means the deliberation
#     ended, not that the human finished reading. The page keeps serving; the
#     next `start` reaps it, or run `stop` explicitly.
#
#   usage: bash preview.sh start [--live] | stop | url
#     --live: append ?live=1 to the printed URL so the page polls sidang.json
#             for a real deliberation. Omit it to show the bundled sample only
#             (no polling, clean console) - the right default for a showcase.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK="$DIR/.preview.lock"   # one line: "<pid> <port>"
LOG="$DIR/.preview.log"

# Kill the recorded server iff it is alive AND really our http.server
# (guards against a recycled PID pointing at an unrelated process).
reap() {
  if [ -f "$LOCK" ]; then
    local pid port; read -r pid port < "$LOCK" 2>/dev/null || true
    if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
      if ps -o command= -p "$pid" 2>/dev/null | grep -q "http.server"; then
        kill "$pid" 2>/dev/null || true
      fi
    fi
    rm -f "$LOCK"
  fi
  # backstop: kill any stray http.server serving THIS dir (e.g. orphan from a
  # start that crashed before recording its pid). cmdline match keeps it scoped.
  pkill -f "http\.server.*--directory $DIR" 2>/dev/null || true
}

case "${1:-}" in
  start)
    reap
    python3 -u -m http.server 0 --bind 127.0.0.1 --directory "$DIR" >"$LOG" 2>&1 &
    pid=$!
    port=""
    for _ in $(seq 1 50); do
      port="$(sed -n 's/.*port \([0-9][0-9]*\).*/\1/p' "$LOG" 2>/dev/null | head -1)"
      if [ -n "$port" ]; then break; fi
      if ! kill -0 "$pid" 2>/dev/null; then echo "preview failed to start; see $LOG" >&2; exit 1; fi
      sleep 0.1
    done
    if [ -z "$port" ]; then echo "could not determine preview port; see $LOG" >&2; exit 1; fi
    printf '%s %s\n' "$pid" "$port" > "$LOCK"
    suffix=""; [ "${2:-}" = "--live" ] && suffix="?live=1"
    echo "http://127.0.0.1:$port/$suffix"
    ;;
  stop)
    if [ -f "$LOCK" ]; then reap; echo "preview stopped"; else echo "no preview running"; fi
    ;;
  url)
    if [ -f "$LOCK" ]; then read -r _ port < "$LOCK" 2>/dev/null; echo "http://127.0.0.1:$port/"; else echo "no preview running"; fi
    ;;
  *)
    echo "usage: bash preview.sh start [--live] | stop | url" >&2; exit 1;;
esac
