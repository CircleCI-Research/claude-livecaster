#!/usr/bin/env python3
"""
Claude LiveCaster — simulation script.

Generates realistic log output for an AI model race without making any API calls.
The voice announcer can't tell the difference from a real eval run.

Usage:
    python3 scripts/simulate.py [log_file] [num_tasks] [speed]

    log_file   — output path (default: logs/eval.log)
    num_tasks  — tasks per model config (default: 15)
    speed      — simulation speed multiplier (default: 1, higher = faster)
"""

import sys
import os
import time
import random
import string
from datetime import datetime

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "logs/eval.log"
NUM_TASKS = int(sys.argv[2]) if len(sys.argv) > 2 else 15
SPEED = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)

# Model configurations: (provider, display_name, model_id, rpm, (min_secs, max_secs))
RUNS = [
    ("openai",    "GPT-5.4 (high reasoning)",             "gpt-5.4",          10, (20, 35)),
    ("openai",    "GPT-5.2 (high reasoning)",             "gpt-5.2",          20, (15, 27)),
    ("google",    "Gemini 3.1 Pro (high thinking)",        "gemini-3.1-pro",    3, (10, 20)),
    ("google",    "Gemini 2.5 Flash",                      "gemini-2.5-flash", 10, (5, 13)),
    ("anthropic", "Claude Opus 4.6 (extended thinking)",   "claude-opus-4-6",  10, (18, 32)),
    ("anthropic", "Claude Sonnet 4.6 (extended thinking)", "claude-sonnet-4-6", 10, (12, 22)),
]

TASKS = [
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


# Clear log
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

        # ~8% chance of a rate-limit error
        if random.random() < 0.08:
            log(
                f'{ts()} ERR [{trace}] {provider}: {run_name}: {task}: '
                f'task finished with error error="API rate limit exceeded (429)"'
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
