---
allowed-tools: Bash
description: Stop the running process and finalize the commentary transcript
---

Stop the current Claude LiveCaster session.

First, read voice settings:
```bash
cat livecaster.yaml 2>/dev/null
```
Use the voice and speed from config (defaults: am_michael, 0.9).

Use the Bash tool to run:

**1. Kill the process and finalize transcript**
```bash
RESULTS_DIR=$(cat /tmp/.livecaster_results_dir 2>/dev/null || echo ".")
LOG_FILE=$(cat /tmp/.livecaster_log_file 2>/dev/null || echo "logs/eval.log")
TRANSCRIPT="$RESULTS_DIR/transcript.txt"
if [ -f /tmp/.livecaster_pid ]; then
  PID=$(cat /tmp/.livecaster_pid)
  if kill "$PID" 2>/dev/null; then
    echo "Process stopped (PID $PID)."
  else
    echo "Process $PID not found (may have already finished)."
  fi
  rm -f /tmp/.livecaster_pid
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  echo "" >> "$TRANSCRIPT"
  echo "━━━ Race Stopped: $TIMESTAMP ━━━" >> "$TRANSCRIPT"
  echo "Transcript finalized at $TRANSCRIPT"
else
  echo "No PID file found at /tmp/.livecaster_pid — nothing to stop."
fi
```

**2. Speak the stop announcement**
```bash
echo "The race has been stopped. Check the transcript for the full play by play." | kokoro-tts - --stream --voice am_michael 2>/dev/null || echo "(kokoro-tts not available)"
```

**3. Show final leaderboard from the log (if available)**
Read the leaderboard_command from livecaster.yaml (default below), substitute {log_file}:
```bash
LOG_FILE=$(cat /tmp/.livecaster_log_file 2>/dev/null || echo "logs/eval.log")
if [ -f "$LOG_FILE" ]; then
  echo ""
  echo "=== Final Leaderboard (tasks completed per contestant) ==="
  grep "task has finished" "$LOG_FILE" | sed 's/.*\] //' | cut -d: -f1-2 | sort | uniq -c | sort -rn
  echo ""
fi
```

Tell the user:
- The process has been stopped and the transcript finalized
- If they had a /loop running for /livecaster-announce, they should cancel it (type `/loop` and select cancel, or close the session)
- The leaderboard above shows how far each contestant got before the stop
- They can review the full commentary in the transcript file
