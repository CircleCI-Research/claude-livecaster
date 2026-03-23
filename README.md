<div align="center">
  <a href="https://youtu.be/5q6fjDWF3Cs">
  <img width="640" height="357" alt="Claude-LiveCaster__Gemini_Generated_Image_3774343774343774__medium" src="https://github.com/user-attachments/assets/fa9ff7c3-cab6-4e0f-b054-6c624c854df4" />
  </a>
</div>

# Claude LiveCaster

Real-time AI voice announcer for races, benchmarks, and long-running agent processes in Claude Code. Watches your logs, generates sports-style play-by-play commentary, and speaks it aloud using fast local text-to-speech (TTS). Powered by Claude. No cloud TTS APIs required.

## [See it in action!](https://youtu.be/5q6fjDWF3Cs) 🎥

<div align="center">
  
https://github.com/user-attachments/assets/be8cf774-b16b-409e-9bbf-ee1789cc7227
<!-- https://github.com/user-attachments/assets/8454d030-2a9c-4753-933e-21313318c3f0 -->

</div>

GitHub limits uploaded video file sizes. For clearer video, [watch this on YouTube](https://youtu.be/5q6fjDWF3Cs).

---

## How It Works

Claude LiveCaster is a set of [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) that turn any log-producing process into a narrated sporting event.

1. **You start a process** (or run the built-in simulation)
2. **Claude wakes up on a timer** via `/loop`, reads your log file, and generates 2–4 sentences of dramatic sports commentary
3. **[Kokoro TTS](https://github.com/nazdridoy/kokoro-tts) speaks it aloud** through your speakers — locally, no cloud APIs
4. **When the process finishes**, Claude delivers a final wrap-up, writes a results summary, and auto-cancels the loop

The commentary style, voice, log parsing, and contestant names are all configurable via `livecaster.yaml`.

## Quick Start

**Try it in under 5 minutes — simulations run locally, no additional API keys needed beyond Claude Code itself.**

### 1. Clone the repo

```bash
git clone https://github.com/CircleCI-Research/claude-livecaster.git
cd claude-livecaster
```

### 2. Install Kokoro TTS

```bash
pip install kokoro-tts
```

Verify it works:

```bash
echo "We are LIVE! The race has begun!" | kokoro-tts - --stream --voice am_michael
```

You should hear audio through your speakers. If not, see [Kokoro TTS troubleshooting](https://github.com/nazdridoy/kokoro-tts).

### 3. Run a simulation in Claude Code

Open the project in [Claude Code](https://docs.anthropic.com/en/docs/claude-code):

```bash
claude
```

Then type:

```
/livecaster-simulate with-announcer
```

You'll be asked to pick a scenario — try **AI Model Race** to start. Six AI models will "race" through 30 tasks while Claude narrates the action live through your speakers. The whole thing takes ~5 minutes at 1x speed.

**Quick sprint** (shorter, faster):

```
/livecaster-simulate ai-model-race 10 3 with-announcer
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (the CLI for Claude — generates the commentary)
- Python 3.9+ (for the simulation script and Kokoro TTS)
- [Kokoro TTS](https://github.com/nazdridoy/kokoro-tts) — local text-to-speech

> **Note:** Simulations generate synthetic log data locally (no external API calls), and TTS runs entirely on-device. The only API usage is Claude Code itself, which generates the commentary text.

### Installing Kokoro TTS

```bash
pip install kokoro-tts
```

Test it:

```bash
echo "Testing one two three" | kokoro-tts - --stream --voice am_michael
```

> **Recommended voices:** `am_michael` (confident American male, default), `af_heart` (warm American female), `bf_emma` (British female — maximum BBC Sports energy). See [all Kokoro TTS voices](https://github.com/nazdridoy/kokoro-tts#supported-voices).

## Slash Commands

All commands are [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) — no external infrastructure, no daemons, no Docker.

| Command | Description |
|---|---|
| `/livecaster-simulate` | Run a simulation (7 SDLC scenarios — synthetic data, no external APIs) |
| `/livecaster-start` | Start watching an existing log file with live commentary |
| `/livecaster-announce` | One tick of live commentary — meant to be called by `/loop` |
| `/livecaster-stop` | Stop the process and finalize the commentary transcript |

### Simulation (built-in demos)

```
/livecaster-simulate                                    # pick a scenario, then configure
/livecaster-simulate with-announcer                     # pick scenario with voice enabled
/livecaster-simulate pipeline-wars with-announcer       # jump straight to Pipeline Wars
/livecaster-simulate deploy-day 15 2 with-announcer     # Deploy Day, 15 tasks, 2x speed
```

## Simulations

Seven built-in scenarios cover the software development lifecycle — from writing code to shipping, monitoring, and responding to incidents. Some are races (multiple contestants competing), others are solo narrations of a single process.

### Races

| Scenario | Contestants | Persona | Voice |
|---|---|---|---|
| **AI Model Race** | 6 AI models (Claude, GPT, Gemini) | NASCAR-style race announcer | `am_michael` |
| **Full-Stack Sprint** | 6 tech stacks (React, Next.js, SvelteKit, Remix, Nuxt, Astro) | Agile sprint commentator | `am_adam` |
| **Pipeline Wars** | 6 microservice CI pipelines | Dual-voice broadcast (anchor + correspondent) | `bf_emma` + `af_bella` |
| **Code Review Roundup** | 5 pull requests | Rodeo announcer | `af_sky` |

### Solo narrations

| Scenario | Subject | Persona | Voice |
|---|---|---|---|
| **App Build Journey** | Building a Next.js SaaS app from scratch | Encouraging dev mentor / pair programmer | `af_heart` |
| **Deploy Day** | Production deployment from staging to full rollout | Mission control operator | `am_adam` |
| **Incident Response** | P1 production incident from alert to resolution | War room coordinator | `bf_isabella` |

### Run a specific scenario

```
/livecaster-simulate ai-model-race with-announcer
/livecaster-simulate full-stack-sprint with-announcer
/livecaster-simulate pipeline-wars with-announcer        # dual-voice!
/livecaster-simulate code-review-roundup with-announcer
/livecaster-simulate app-build-journey with-announcer
/livecaster-simulate deploy-day with-announcer
/livecaster-simulate incident-response with-announcer
```

Or just run `/livecaster-simulate` and pick from the menu.

### Watch your own process

```
/livecaster-start my-app.log                 # watch a log file
/livecaster-start my-app.log with-announcer  # watch with voice commentary
```

### Manual announcer loop

If you opted out of the announcer initially, start it anytime:

```
/loop 1m /livecaster-announce    # check in every minute (good for simulations)
/loop 5m /livecaster-announce    # check in every 5 minutes (good for real runs)
```

The announcer dynamically scales how many log lines it reads based on the `/loop` interval.

### Stop everything

```
/livecaster-stop
```

Then cancel the `/loop` in your session (type `/loop` and select cancel, or close the session).

## Configuration

LiveCaster reads `livecaster.yaml` from your project root. When you run `/livecaster-simulate`, the selected scenario file from `simulations/` is copied to `livecaster.yaml` automatically.

```yaml
# Event name (used in transcripts and commentary)
name: "AI Model Race"

# String in the log that means "we're done"
completion_marker: "all tasks in all configurations have finished on all providers"

# Shell command to extract standings. {log_file} is replaced at runtime.
leaderboard_command: >
  grep "task has finished" {log_file}
  | sed 's/.*] //'
  | cut -d: -f1-2
  | sort | uniq -c | sort -rn

# Contestant names for natural commentary
contestants:
  - "Claude Sonnet 4.6"
  - "Claude Opus 4.6"
  - "GPT-5.4"
  - "GPT-5.2"
  - "Gemini 3.1 Pro"
  - "Gemini 2.5 Flash"

# Commentary style
persona: |
  Ken Squier narrating a championship race between AI models.
  Racing metaphors: pulling ahead, gaining ground, the homestretch.
  Call out the leader and close battles.
  Treat error lines as dramatic setbacks.
  2-4 sentences, under 80 words, plain ASCII only.

# TTS — single voice
voice: "am_michael"
speed: 0.9
```

### Dual-voice mode

The Pipeline Wars scenario uses two voices — a technical anchor and a field correspondent. Instead of a single `voice` key, use a `voices` list:

```yaml
voices:
  - role: "anchor"
    voice: "bf_emma"
    speed: 0.9
  - role: "correspondent"
    voice: "af_bella"
    speed: 0.95
```

The announcer generates labeled commentary (`[ANCHOR]` / `[CORRESPONDENT]`) and speaks each part with the appropriate voice. Any scenario can use dual-voice by switching from `voice` to `voices` in its YAML.

### Customizing for Your Own Process

Edit `livecaster.yaml` to match your log format:

1. **`completion_marker`** — what string appears when your process is done?
2. **`leaderboard_command`** — a shell pipeline that extracts "who's winning" from your log
3. **`contestants`** — the names of the things being compared
4. **`persona`** — what kind of announcer do you want?

**Example — CI/CD pipeline monitoring:**

```yaml
name: "Deploy Pipeline"
completion_marker: "Pipeline completed successfully"
leaderboard_command: "grep 'stage completed' {log_file} | awk '{print $4, $5}' | sort"
contestants:
  - "Build"
  - "Test"
  - "Security Scan"
  - "Deploy Staging"
  - "Deploy Production"
persona: |
  Mission control commentator tracking a deployment pipeline.
  Calm and focused. Celebrate completed stages, flag failures urgently.
  Under 60 words.
```

**Example — ML training run:**

```yaml
name: "Training Race"
completion_marker: "Training complete"
leaderboard_command: "grep 'epoch.*loss' {log_file} | tail -5"
contestants:
  - "ResNet-50"
  - "ViT-Large"
  - "EfficientNet-B7"
persona: |
  Excited boxing commentator calling a training bout.
  Reference loss values, learning rate changes, and validation accuracy.
  Treat loss spikes as dramatic upsets. Under 80 words.
```

## Sample Transcript

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CLAUDE LIVECASTER — LIVE COMMENTARY TRANSCRIPT
  Started: 2026-03-18 14:30:00
  Mode:    SIMULATION (no API calls)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━ (Update #1) ━━━
Gemini 2.5 Flash rockets to the front with 42 tasks complete, but Claude
Sonnet 4.6 is right on its tail at 38. GPT-5.2 sits in third, grinding
through the pack. An early rate-limit error hit Gemini 3.1 Pro on the
logic grid task — that could cost them down the stretch.

━━━ (Update #2) ━━━
Lead change! Claude Sonnet 4.6 surges past Gemini Flash into first with
67 tasks done. The Anthropic camp is rolling now. GPT-5.4 quietly climbs
to fourth, its high-reasoning mode eating through architecture tasks
like a machine on rails.

━━━ — FINAL ━━━
And that is the checkered flag! Claude Sonnet 4.6 takes the win with
134 tasks completed, edging out Gemini 2.5 Flash by just 3. What a race,
what a finish! Until next time, this is LiveCaster signing off.
```

## Tips

### Keep the session alive for long runs

`/loop` is session-scoped — it stops when you exit Claude Code. For multi-hour runs, use tmux:

```bash
tmux new -s livecaster
claude
# Run /livecaster-simulate or /livecaster-start
# Detach: Ctrl-B then D
# Reattach later: tmux attach -t livecaster
```

### Adjust the commentary interval

Shorter intervals = more frequent updates (more dramatic, more tokens). Longer = calmer, cheaper.

| Interval | Best for |
|---|---|
| 1 minute | Short simulations, demos |
| 2–5 minutes | Real eval runs, CI pipelines |
| 10 minutes | Long-running processes (hours) |

### Voice options

Each built-in simulation uses a different voice. Change the voice in `livecaster.yaml` or any scenario YAML:

| Voice | Style | Used in |
|---|---|---|
| `am_michael` | Confident American male | AI Model Race |
| `am_adam` | Deep American male | Full-Stack Sprint, Deploy Day |
| `bf_emma` | British female (BBC Sports energy) | Pipeline Wars (anchor) |
| `af_bella` | Bright American female | Pipeline Wars (correspondent) |
| `af_sky` | Dynamic American female | Code Review Roundup |
| `af_heart` | Warm American female | App Build Journey |
| `bf_isabella` | British female (understated) | Incident Response |

See [all Kokoro TTS voices](https://github.com/nazdridoy/kokoro-tts#supported-voices).

**Watch the transcript live in a split pane:**

```bash
tail -f results/simulation/*/$(date +%Y-%m-%d)/*/transcript.txt
```

## Project Structure

```
claude-livecaster/
├── livecaster.yaml                  # Active config (auto-copied from selected scenario)
├── CLAUDE.md                        # Project context for Claude Code
├── .claude/
│   └── commands/
│       ├── livecaster-simulate.md   # Simulation launcher (7 scenarios)
│       ├── livecaster-start.md      # Watch any log file
│       ├── livecaster-announce.md   # One commentary tick (for /loop)
│       └── livecaster-stop.md       # Stop and finalize
├── simulations/
│   ├── ai-model-race.yaml          # Race: 6 AI models
│   ├── full-stack-sprint.yaml      # Race: 6 tech stacks
│   ├── pipeline-wars.yaml          # Race: 6 CI pipelines (dual-voice)
│   ├── code-review-roundup.yaml    # Race: 5 pull requests
│   ├── app-build-journey.yaml      # Solo: build a Next.js SaaS app
│   ├── deploy-day.yaml             # Solo: production deployment
│   └── incident-response.yaml      # Solo: P1 incident response
├── scripts/
│   ├── simulate.py                  # Data-driven simulation engine (Python)
│   └── open-dashboard.sh            # Opens Terminal.app tail windows (macOS)
├── README.md
└── LICENSE                          # MIT
```

## Origin Story

Claude LiveCaster was extracted from [MindTrial](https://github.com/petmal/MindTrial), an AI model evaluation framework. The original voice announcer was built to narrate live model-vs-model eval races — see the [original PR](https://github.com/ryan-circleci/MindTrial/pull/2) for the full story.

This repo generalizes the announcer into a standalone tool that works with any log-producing process.

## Contributing

Contributions welcome! Some ideas:

- **New simulation scenarios** — ML training runs, game tournaments, migration projects, security audits
- **New personas** — nature documentary narrator, auctioneer, baseball announcer
- **Cross-platform dashboard** — `open-dashboard.sh` is currently macOS-only
- **Transcript viewer** — a nice HTML/web viewer for commentary transcripts
- **More dual-voice combos** — play-by-play + color commentary, narrator + analyst

## License

MIT — see [LICENSE](LICENSE).
