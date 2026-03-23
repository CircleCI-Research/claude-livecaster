---
allowed-tools: Bash, AskUserQuestion, CronCreate
description: Start watching a log file with optional live voice commentary
---

The user wants to start Claude LiveCaster to watch a running process.
Arguments: $ARGUMENTS (optional: log file path, `with-announcer`, interval)

Parse $ARGUMENTS:
- Any arg that looks like a file path (contains / or . or ends in .log/.txt): log file path
- `with-announcer`: enable voice announcer
- A numeric arg immediately following `with-announcer`: interval in minutes (default: 5)

**Step 0 — Read configuration**
```bash
cat livecaster.yaml 2>/dev/null || echo "NO_CONFIG"
```
Note settings from config. Defaults: voice=am_michael, speed=0.9

**Step 1 — Determine what to watch**

If no log file path was provided in args, use AskUserQuestion to ask:
"What log file should LiveCaster watch?"
With options:
1. logs/activity.log (default)
2. Let me specify a path

If they choose option 2, ask a follow-up question for the path.

Verify the log file exists:
```bash
ls -la "<log_file_path>" 2>/dev/null || echo "FILE_NOT_FOUND"
```
If the file doesn't exist yet, that's okay — the announcer will wait for it to appear.

**Step 2 — Determine announcer mode**

If `with-announcer` is NOT present in $ARGUMENTS, use AskUserQuestion to ask:
"Want live voice commentary?"
With options:
1. Yes — enable the voice announcer (requires kokoro-tts)
2. No — just set up the dashboard

Set `ANNOUNCER_ENABLED` accordingly.

If `ANNOUNCER_ENABLED` is `true` AND no interval was specified, use AskUserQuestion to ask:
"How often should the announcer check in?"
With options:
1. Every 1 minute
2. Every 2 minutes
3. Every 5 minutes (default)
4. Every 10 minutes

Set `ANNOUNCER_INTERVAL` to the chosen number (default: 5).

**Step 3 — Set up state files**
```bash
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
RESULTS_DIR="results/watch/$(date '+%Y-%m-%d')/$(date '+%H-%M-%S')"
LOG_FILE="<the log file path from Step 1>"
mkdir -p "$RESULTS_DIR"
echo "$RESULTS_DIR" > /tmp/.livecaster_results_dir
echo "$LOG_FILE" > /tmp/.livecaster_log_file
echo "${ANNOUNCER_INTERVAL:-5}" > /tmp/.livecaster_loop_interval_mins
cat > "$RESULTS_DIR/transcript.txt" << HEADER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CLAUDE LIVECASTER — LIVE COMMENTARY TRANSCRIPT
  Started: $TIMESTAMP
  Watching: $LOG_FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HEADER
echo "LiveCaster initialized. Watching: $LOG_FILE"
```

**4. Open dashboard**
```bash
bash scripts/open-dashboard.sh
```

**5. (ANNOUNCER ONLY) Speak the start announcement**

Skip if `ANNOUNCER_ENABLED` is `false`.

```bash
echo "LiveCaster is online and watching. Let us see what happens!" > /tmp/commentary.txt && kokoro-tts /tmp/commentary.txt --stream --voice am_michael --speed 0.9 2>/dev/null || echo "(kokoro-tts not available — install with: pip install kokoro-tts)"
```

**6. (ANNOUNCER ONLY) Auto-start the announcer loop**

Skip if `ANNOUNCER_ENABLED` is `false`.

Use CronCreate:
- `cron`: `*/${ANNOUNCER_INTERVAL:-5} * * * *`
- `prompt`: `/livecaster-announce`
- `recurring`: `true`

Save the returned job ID.

**7. Tell the user**
- LiveCaster is watching the log file (show path)
- If announcer is enabled: the announcer loop is running (show interval, job ID)
- If announcer is disabled: can start anytime with `/loop 5m /livecaster-announce`
- Dashboard windows are open for the log and transcript
- Stop with `/livecaster-stop`
- Customize commentary style and log parsing in `livecaster.yaml`
