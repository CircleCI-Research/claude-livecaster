---
allowed-tools: Bash, AskUserQuestion, CronCreate
description: Run a zero-cost SDLC simulation with optional live voice commentary
---

The user wants to run a Claude LiveCaster simulation — generates realistic log output
without making any real API calls. Seven scenarios are available.
Arguments: $ARGUMENTS (optional: scenario name, num_tasks, speed multiplier, `with-announcer`)

Parse $ARGUMENTS:
- Any arg matching a scenario filename (without .yaml): scenario name (e.g. `pipeline-wars`, `deploy-day`)
- First numeric arg (not immediately following `with-announcer`): number of tasks per contestant (default: 30)
- Second numeric arg (not immediately following `with-announcer`): speed multiplier (default: 1, real-time pacing)
- Any arg equal to `with-announcer`: enable voice announcer
- A numeric arg immediately following `with-announcer` in the arg list: announcer loop interval in minutes (default: 1 if not specified)

**Step 0 — Choose a scenario**

If no scenario name was provided in $ARGUMENTS, use AskUserQuestion to ask:
"Pick a simulation scenario:"
With options:
1. AI Model Race — Six AI models compete on coding and reasoning tasks (the classic)
2. Full-Stack Sprint — Six tech stacks race to ship the same web app
3. Pipeline Wars — Six microservice CI pipelines compete (dual-voice broadcast!)
4. Code Review Roundup — Five PRs race through the review gauntlet
5. App Build Journey — Solo narration: one agent builds a Next.js SaaS app from scratch
6. Deploy Day — Solo narration: a production deployment from staging to full rollout
7. Incident Response — Solo narration: a P1 production incident from alert to resolution

Map the selection to a scenario file:
1 → `simulations/ai-model-race.yaml`
2 → `simulations/full-stack-sprint.yaml`
3 → `simulations/pipeline-wars.yaml`
4 → `simulations/code-review-roundup.yaml`
5 → `simulations/app-build-journey.yaml`
6 → `simulations/deploy-day.yaml`
7 → `simulations/incident-response.yaml`

If a scenario name was provided as an arg, map it to `simulations/<name>.yaml`.

Set `SCENARIO_FILE` to the selected path.

**Step 1 — Determine announcer mode**

If `with-announcer` is NOT present in $ARGUMENTS, use AskUserQuestion to ask:
"Want live voice commentary?"
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

**2. Copy scenario config to livecaster.yaml**
```bash
SCENARIO_FILE="<selected scenario file>"
if [ -f "$SCENARIO_FILE" ]; then
  cp "$SCENARIO_FILE" livecaster.yaml
  SCENARIO_NAME=$(grep '^name:' "$SCENARIO_FILE" | head -1 | sed 's/name: *//' | tr -d '"')
  echo "Loaded scenario: $SCENARIO_NAME"
  echo "Config: $SCENARIO_FILE -> livecaster.yaml"
else
  echo "ERROR: Scenario file not found: $SCENARIO_FILE"
  exit 1
fi
```

**3. Initialize results directory and transcript**
```bash
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SCENARIO_SLUG=$(basename "$SCENARIO_FILE" .yaml)
RESULTS_DIR="results/simulation/$SCENARIO_SLUG/$(date '+%Y-%m-%d')/$(date '+%H-%M-%S')"
LOG_FILE="$RESULTS_DIR/activity.log"
mkdir -p "$RESULTS_DIR"
echo "$RESULTS_DIR" > /tmp/.livecaster_results_dir
echo "$LOG_FILE" > /tmp/.livecaster_log_file
echo "${ANNOUNCER_INTERVAL:-1}" > /tmp/.livecaster_loop_interval_mins
cat > "$RESULTS_DIR/transcript.txt" << HEADER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CLAUDE LIVECASTER — LIVE COMMENTARY TRANSCRIPT
  Started: $TIMESTAMP
  Scenario: $SCENARIO_NAME
  Mode:    SIMULATION (no API calls)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HEADER
echo "Transcript initialized at $RESULTS_DIR/transcript.txt"
```

**4. Start the simulation in the background**
```bash
if [ -f /tmp/.livecaster_pid ]; then
  OLD_PID=$(cat /tmp/.livecaster_pid)
  kill "$OLD_PID" 2>/dev/null && echo "Killed previous simulation (PID: $OLD_PID)" || true
fi

NUM_TASKS="${1:-30}"
SPEED="${2:-1}"
LOG_FILE=$(cat /tmp/.livecaster_log_file)
SCENARIO_FILE="<selected scenario file>"
nohup python3 scripts/simulate.py "$LOG_FILE" "$NUM_TASKS" "$SPEED" --scenario "$SCENARIO_FILE" > /dev/null 2>&1 &
SIM_PID=$!
echo "$SIM_PID" > /tmp/.livecaster_pid
echo "Simulation started (PID: $SIM_PID)"
echo "Scenario: $SCENARIO_NAME"
echo "Tasks per contestant: $NUM_TASKS"
echo "Speed: ${SPEED}x"
echo "Log: $LOG_FILE"
```

**5. Wait for simulation to begin, confirm it's writing**
```bash
sleep 3
head -15 "$(cat /tmp/.livecaster_log_file)" 2>/dev/null || echo "(log not yet available)"
```

**6. Open log and transcript in separate Terminal windows**
```bash
bash scripts/open-dashboard.sh
```

**7. (ANNOUNCER ONLY) Speak the start announcement**

Skip this step entirely if `ANNOUNCER_ENABLED` is `false`.

Read the voice settings from livecaster.yaml. If the config has a `voices` list, use the first voice for this announcement. Otherwise use the single `voice` value.

Generate a brief, scenario-appropriate opening line. Examples:
- AI Model Race: "Ladies and gentlemen, welcome to a LiveCaster simulation! Six model configurations are about to go head to head. Let the race begin!"
- Pipeline Wars: "This is your CI broadcast team coming to you, LIVE. Six pipelines are firing up. Lets see who ships first!"
- Deploy Day: "Deploy sequence initiated. Version 2 point 4 point 0 is heading to production. All systems standing by."
- Incident Response: "We have a P1 alert. The war room is open. Lets walk through this together."

Speak the line:
```bash
echo "<OPENING_LINE>" > /tmp/commentary.txt && kokoro-tts /tmp/commentary.txt --stream --voice <voice> --speed <speed> 2>/dev/null || echo "(kokoro-tts not available — install with: pip install kokoro-tts)"
```

**8. (ANNOUNCER ONLY) Auto-start the announcer loop**

Skip this step entirely if `ANNOUNCER_ENABLED` is `false`.

Use the CronCreate tool to schedule the announcer automatically:
- `cron`: `*/${ANNOUNCER_INTERVAL:-1} * * * *` (every N minutes)
- `prompt`: `/livecaster-announce`
- `recurring`: `true`

Save the returned job ID to show the user.

**9. Tell the user the simulation is running**

Tell the user:
- The simulation is running (show scenario name, PID, tasks per contestant, speed, log path)
- If announcer is enabled: the announcer loop is running every `ANNOUNCER_INTERVAL` minute(s) (show job ID)
- If announcer is disabled: mention they can re-run with `with-announcer` to enable voice commentary, or manually start with `/loop 1m /livecaster-announce`
- Watch live:
  - Transcript: `tail -f <results_dir>/transcript.txt`
  - Log: `tail -f <log_file>`
- Stop: `/livecaster-stop`
- Default is 30 tasks at 1x speed (~5-6 minutes for races, ~2-3 minutes for solo narrations)
- Quick sprint: `/livecaster-simulate <scenario> 10 3`
- All available scenarios: ai-model-race, full-stack-sprint, pipeline-wars, code-review-roundup, app-build-journey, deploy-day, incident-response
