#!/usr/bin/env bash
# Opens two Terminal.app windows to tail the live log and transcript.
# Reads state from /tmp/.livecaster_* files set by the slash commands.

set -euo pipefail

LOG_FILE="${1:-$(cat /tmp/.livecaster_log_file 2>/dev/null)}"
RESULTS_DIR="${2:-$(cat /tmp/.livecaster_results_dir 2>/dev/null)}"
TRANSCRIPT="$RESULTS_DIR/transcript.txt"

if [[ -z "$LOG_FILE" || -z "$RESULTS_DIR" ]]; then
  echo "No active LiveCaster session found. Start one with /livecaster-simulate first." >&2
  exit 1
fi

ABS_LOG="$(cd "$(dirname "$LOG_FILE")" && pwd)/$(basename "$LOG_FILE")"
ABS_TRANSCRIPT="$(cd "$(dirname "$TRANSCRIPT")" && pwd)/$(basename "$TRANSCRIPT")"

echo "Opening tail windows for:"
echo "  Log:        $ABS_LOG"
echo "  Transcript: $ABS_TRANSCRIPT"

open_terminal_window() {
  local file="$1"
  osascript -e "tell application \"Terminal\" to do script \"tail -f '$file'\"" \
            -e "tell application \"Terminal\" to activate"
}

open_terminal_window "$ABS_LOG"
open_terminal_window "$ABS_TRANSCRIPT"

echo "Done."
