# Claude LiveCaster

Real-time AI voice announcer for Claude Code. See README.md for full documentation.

## Project structure

- `.claude/commands/` — Slash commands (the core of LiveCaster)
- `scripts/` — Supporting scripts (simulation, dashboard)
- `livecaster.yaml` — Default configuration (matches the built-in simulation)
- `results/` — Runtime output directory (gitignored)

## Key patterns

- State is stored in `/tmp/.livecaster_*` files during a session
- The announcer runs via `/loop` — never as a background Task agent (they lose Bash permissions)
- Commentary passes through `sed` decimal-to-word conversion before TTS (`4.6` → `4 point 6`)
- Config is read from `livecaster.yaml` in the project root

## TTS

Requires [kokoro-tts](https://github.com/nazdridoy/kokoro-tts): `pip install kokoro-tts`
Default voice: `am_michael` at speed 0.9

## Slash commands

- `/livecaster-simulate` — Demo with simulated data (no API keys needed)
- `/livecaster-start` — Watch a real log file
- `/livecaster-announce` — One commentary tick (for `/loop`)
- `/livecaster-stop` — Stop and finalize transcript
