#!/usr/bin/env python3
"""
Claude LiveCaster — simulation script.

Generates realistic log output without making any API calls.
The voice announcer can't tell the difference from a real run.

Usage:
    python3 scripts/simulate.py <log_file> <num_tasks> <speed> [--scenario <yaml_path>]

    log_file       — output path (default: logs/eval.log)
    num_tasks      — tasks per contestant (default: 15)
    speed          — simulation speed multiplier (default: 1, higher = faster)
    --scenario     — path to a simulation YAML file (optional; uses built-in defaults if omitted)
"""

import sys
import os
import time
import random
import string
from datetime import datetime

DEFAULT_RUNS = [
    ("openai",    "GPT-5.4 (high reasoning)",             "gpt-5.4",          10, (20, 35)),
    ("openai",    "GPT-5.2 (high reasoning)",             "gpt-5.2",          20, (15, 27)),
    ("google",    "Gemini 3.1 Pro (high thinking)",        "gemini-3.1-pro",    3, (10, 20)),
    ("google",    "Gemini 2.5 Flash",                      "gemini-2.5-flash", 10, (5, 13)),
    ("anthropic", "Claude Opus 4.6 (extended thinking)",   "claude-opus-4-6",  10, (18, 32)),
    ("anthropic", "Claude Sonnet 4.6 (extended thinking)", "claude-sonnet-4-6", 10, (12, 22)),
]

DEFAULT_TASKS = [
    "reasoning - logic grid puzzle - v1",
    "reasoning - bridge crossing - v1",
    "reasoning - color and number - v1",
    "coding - binary search implementation - v1",
    "coding - linked list reversal - v1",
    "coding - async pipeline - v1",
    "debugging - race condition - v1",
    "debugging - memory leak detection - v1",
    "debugging - off by one error - v1",
    "architecture - microservice design - v1",
    "architecture - caching strategy - v1",
    "architecture - event sourcing - v1",
    "devops - pipeline optimization - v1",
    "devops - container orchestration - v1",
    "devops - secret management - v1",
    "testing - property based testing - v1",
    "testing - integration test design - v1",
    "testing - mutation testing - v1",
    "security - input validation - v1",
    "security - auth flow design - v1",
    "data - query optimization - v1",
    "data - schema migration - v1",
    "api - rate limiter design - v1",
    "api - versioning strategy - v1",
    "system - distributed consensus - v1",
    "system - load balancer config - v1",
    "system - circuit breaker - v1",
    "refactoring - extract service - v1",
    "refactoring - dependency injection - v1",
    "documentation - api specification - v1",
]

DEFAULT_ERROR_RATE = 0.08

DEFAULT_ERROR_MESSAGES = [
    'API rate limit exceeded (429)',
]


def parse_args():
    args = sys.argv[1:]
    scenario_path = None
    positional = []

    i = 0
    while i < len(args):
        if args[i] == "--scenario" and i + 1 < len(args):
            scenario_path = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1

    log_file = positional[0] if len(positional) > 0 else "logs/eval.log"
    num_tasks = int(positional[1]) if len(positional) > 1 else 15
    speed = float(positional[2]) if len(positional) > 2 else 1.0

    return log_file, num_tasks, speed, scenario_path


def load_scenario(path):
    import yaml
    with open(path) as f:
        cfg = yaml.safe_load(f)

    sim = cfg.get("simulation", {})

    runs = []
    for r in sim.get("runs", []):
        timing = r.get("timing", [10, 25])
        runs.append((
            r["provider"],
            r["display_name"],
            r.get("model_id", r["display_name"]),
            r.get("rpm", 10),
            (timing[0], timing[1]),
        ))

    tasks = sim.get("tasks", DEFAULT_TASKS)
    error_rate = sim.get("error_rate", DEFAULT_ERROR_RATE)
    error_messages = sim.get("error_messages", DEFAULT_ERROR_MESSAGES)

    return runs or DEFAULT_RUNS, tasks, error_rate, error_messages


LOG_FILE, NUM_TASKS, SPEED, SCENARIO_PATH = parse_args()

if SCENARIO_PATH:
    RUNS, TASKS, ERROR_RATE, ERROR_MESSAGES = load_scenario(SCENARIO_PATH)
else:
    RUNS, TASKS, ERROR_RATE, ERROR_MESSAGES = DEFAULT_RUNS, DEFAULT_TASKS, DEFAULT_ERROR_RATE, DEFAULT_ERROR_MESSAGES

os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)

task_count = min(NUM_TASKS, len(TASKS))
providers = sorted(set(r[0] for r in RUNS))


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def trace_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=26))


def log(line):
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
        f.flush()


with open(LOG_FILE, "w") as f:
    pass

log(f"{ts()} INF starting {task_count} tasks on {len(providers)} providers...")

for provider in providers:
    configs = sum(1 for r in RUNS if r[0] == provider)
    log(f"{ts()} INF {provider}: starting {task_count} tasks on this provider in {configs} configurations...")

for provider, run_name, _, rpm, _ in RUNS:
    log(f"{ts()} INF {provider}: {run_name}: request rate limited to {rpm} requests/min.")

print(f"=== Simulation: {task_count} tasks x {len(RUNS)} configs, speed={SPEED}x ===", file=sys.stderr)

race_start = time.time()

run_state = {run_name: 0 for _, run_name, *_ in RUNS}
provider_done = {p: False for p in providers}

while any(idx < task_count for idx in run_state.values()):
    for provider, run_name, model, rpm, (lo, hi) in RUNS:
        idx = run_state[run_name]
        if idx >= task_count:
            continue

        task = TASKS[idx]
        trace = trace_id()

        log(f"{ts()} INF [{trace}] {provider}: {run_name}: {task}: starting task...")

        base_time = random.uniform(lo, hi)
        wait = base_time / (10 * SPEED)
        time.sleep(wait)

        duration = f"{base_time:.6f}s"

        if random.random() < ERROR_RATE:
            err_msg = random.choice(ERROR_MESSAGES)
            log(
                f'{ts()} ERR [{trace}] {provider}: {run_name}: {task}: '
                f'task finished with error error="{err_msg}"'
            )

        log(f"{ts()} INF [{trace}] {provider}: {run_name}: {task}: task has finished in {duration}.")

        run_state[run_name] = idx + 1

        if idx + 1 >= task_count:
            all_done = all(
                run_state[rn] >= task_count
                for p, rn, *_ in RUNS if p == provider
            )
            if all_done and not provider_done[provider]:
                elapsed = time.time() - race_start
                log(
                    f"{ts()} INF {provider}: all tasks in all configurations "
                    f"have finished on this provider in {elapsed:.0f}s."
                )
                provider_done[provider] = True

total = time.time() - race_start
log(f"{ts()} INF all tasks in all configurations have finished on all providers in {total:.0f}s.")
print(f"=== Simulation complete. Log written to {LOG_FILE} ===", file=sys.stderr)
