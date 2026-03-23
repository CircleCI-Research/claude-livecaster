---
allowed-tools: Bash, AskUserQuestion, CronCreate
description: Run a zero-cost AI model race simulation with optional live voice commentary
---

The user wants to run a Claude LiveCaster simulation — generates realistic AI model race
log output without making any real API calls.
Arguments: $ARGUMENTS (optional: num_tasks, speed multiplier, `with-announcer`)

Parse $ARGUMENTS:
- First numeric arg (not immediately following `with-announcer`): number of tasks per model (default: 30)
- Second numeric arg (not immediately following `with-announcer`): speed multiplier (default: 1, real-time pacing)
- Any arg equal to `with-announcer`: enable voice announcer
- A numeric arg immediately following `with-announcer` in the arg list: announcer loop interval in minutes (default: 1 if not specified)

**Step 0 — Determine announcer mode**

If `with-announcer` is NOT present in $ARGUMENTS, use AskUserQuestion to ask:
"Want live voice commentary for this race?"
With options:
1. Yes — enable the voice announcer (requires kokoro-tts)
2. No — run silently (no TTS, no announcer loop)

Set `ANNOUNCER_ENABLED` to `true` or `false` based on the flag or the user's answer.

If `ANNOUNCER_ENABLED` is `true` AND no interval was specified in $ARGUMENTS, use AskUserQuestion to ask:
"How often should the announcer check in?"
With options:
1. Every 1 minute (default for simulations)
2. Every 2 minutes
3. Every 5 minutes

Set `ANNOUNCER_INTERVAL` to the chosen number of minutes (default: 1).

Use the Bash tool to do the following steps:

**1. Read configuration**
```bash
cat livecaster.yaml 2>/dev/null || echo "NO_CONFIG"
```
Note the voice and speed settings. Defaults: voice=am_michael, speed=0.9

**2. Initialize results directory and transcript**
```bash
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
RESULTS_DIR="results/simulation/$(date '+%Y-%m-%d')/$(date '+%H-%M-%S')"
LOG_FILE="$RESULTS_DIR/eval.log"
mkdir -p "$RESULTS_DIR"
echo "$RESULTS_DIR" > /tmp/.livecaster_results_dir
echo "$LOG_FILE" > /tmp/.livecaster_log_file
echo "${ANNOUNCER_INTERVAL:-1}" > /tmp/.livecaster_loop_interval_mins
cat > "$RESULTS_DIR/transcript.txt" << HEADER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CLAUDE LIVECASTER — LIVE COMMENTARY TRANSCRIPT
  Started: $TIMESTAMP
  Mode:    SIMULATION (no API calls)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HEADER
echo "Transcript initialized at $RESULTS_DIR/transcript.txt"
```

**3. Start the simulation in the background**
```bash
if [ -f /tmp/.livecaster_pid ]; then
  OLD_PID=$(cat /tmp/.livecaster_pid)
  kill "$OLD_PID" 2>/dev/null && echo "Killed previous simulation (PID: $OLD_PID)" || true
fi

NUM_TASKS="${1:-30}"
SPEED="${2:-1}"
LOG_FILE=$(cat /tmp/.livecaster_log_file)
nohup python3 scripts/simulate.py "$LOG_FILE" "$NUM_TASKS" "$SPEED" > /dev/null 2>&1 &
SIM_PID=$!
echo "$SIM_PID" > /tmp/.livecaster_pid
echo "Simulation started (PID: $SIM_PID)"
echo "Tasks per model: $NUM_TASKS"
echo "Speed: ${SPEED}x"
echo "Log: $LOG_FILE"
```

**4. Wait for simulation to begin, confirm it's writing**
```bash
sleep 3
head -15 "$(cat /tmp/.livecaster_log_file)" 2>/dev/null || echo "(log not yet available)"
```

**5. Open log and transcript in separate Terminal windows**
```bash
bash scripts/open-dashboard.sh
```

**6. (ANNOUNCER ONLY) Speak the race start announcement**

Skip this step entirely if `ANNOUNCER_ENABLED` is `false`.

```bash
echo "Ladies and gentlemen, welcome to a LiveCaster simulation! Six model configurations are about to go head to head. No real tokens, all the drama. Let the race begin!" > /tmp/commentary.txt && kokoro-tts /tmp/commentary.txt --stream --voice am_michael --speed 0.9 2>/dev/null || echo "(kokoro-tts not available — install with: pip install kokoro-tts)"
```

**7. (ANNOUNCER ONLY) Auto-start the announcer loop**

Skip this step entirely if `ANNOUNCER_ENABLED` is `false`.

Use the CronCreate tool to schedule the announcer automatically:
- `cron`: `*/${ANNOUNCER_INTERVAL:-1} * * * *` (every N minutes)
- `prompt`: `/livecaster-announce`
- `recurring`: `true`

Save the returned job ID to show the user.

**8. Tell the user the simulation is running**

Tell the user:
- The simulation is running (show PID, tasks per model, speed, log path)
- If announcer is enabled: the announcer loop is running every `ANNOUNCER_INTERVAL` minute(s) (show job ID)
- If announcer is disabled: mention they can re-run with `with-announcer` to enable voice commentary, or manually start with `/loop 1m /livecaster-announce`
- Watch live:
  - Transcript: `tail -f <results_dir>/transcript.txt`
  - Log: `tail -f <log_file>`
- Stop: `/livecaster-stop`
- Default is 30 tasks at 1x speed (~5-6 minutes)
- Quick sprint: `/livecaster-simulate 10 3`
