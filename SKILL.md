---
name: freeride
description: Manages free AI models from OpenRouter for Hermes Agent. Automatically ranks models by quality, configures fallbacks for rate-limit handling, and updates ~/.hermes/config.yaml. Use when the user mentions free AI, OpenRouter, model switching, rate limits, or wants to reduce AI costs.
env:
  - name: OPENROUTER_API_KEY
    description: OpenRouter API key — get a free one at openrouter.ai/keys
    required: true
    secret: true
network:
  - openrouter.ai
writes:
  - ~/.hermes/config.yaml (keys: model, fallback_providers only)
  - ~/.hermes/.freeride-cache.json
  - ~/.hermes/.freeride-watcher-state.json
install: pip install -e .
---

# FreeRide - Free AI for Hermes Agent

## What This Skill Does

Configures Hermes Agent to use **free** AI models from OpenRouter. Sets the best free model as primary, adds ranked fallbacks so rate limits don't interrupt the user, and preserves existing config.

## Prerequisites

Before running any FreeRide command, ensure:

1. **OPENROUTER_API_KEY is set.** Check with `echo $OPENROUTER_API_KEY`. If empty, the user must get a free key at https://openrouter.ai/keys and set it:
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-..."
   # Or persist it in Hermes .env:
   hermes config set OPENROUTER_API_KEY "sk-or-v1-..."
   ```

2. **The `freeride` CLI is installed.** Check with `which freeride`. If not found:
   ```bash
   cd ~/.hermes/skills/free-ride
   pip install -e .
   ```

## Primary Workflow

When the user wants free AI, run these steps in order:

```bash
# Step 1: Configure best free model + fallbacks
freeride auto

# Step 2: Restart gateway so Hermes picks up the changes
hermes gateway restart
```

That's it. The user now has free AI with automatic fallback switching.

Verify by telling the user to send `/status` to check the active model.

## Commands Reference

| Command | When to use it |
|---------|----------------|
| `freeride auto` | User wants free AI set up (most common) |
| `freeride auto -f` | User wants fallbacks but wants to keep their current primary model |
| `freeride auto -c 10` | User wants more fallbacks (default is 5) |
| `freeride list` | User wants to see available free models |
| `freeride list -n 30` | User wants to see all free models |
| `freeride switch <model>` | User wants a specific model (e.g. `freeride switch qwen3-coder`) |
| `freeride switch <model> -f` | Add specific model as fallback only |
| `freeride status` | Check current FreeRide configuration |
| `freeride fallbacks` | Update only the fallback models |
| `freeride refresh` | Force refresh the cached model list |
| `freeride rotate` | User is rate-limited / fallback chain is dead — live-test and rebuild |

**After any command that changes config, always run `hermes gateway restart`.**

## What It Writes to Config

FreeRide updates only these keys in `~/.hermes/config.yaml`:

```yaml
# Primary model
model:
  provider: openrouter              # e.g. openrouter
  default: qwen/qwen3-coder:free   # the best free model

# Fallback chain (tried in order when primary fails)
fallback_providers:
  - provider: openrouter
    model: openrouter/free          # smart router — auto-picks best available
  - provider: openrouter
    model: nvidia/llama-3.1-nemotron:free
  - provider: openrouter
    model: google/gemini-flash:free
```

Everything else in `config.yaml` (terminal, auxiliary, delegation, cron, tools, etc.) is preserved.

The first fallback is always `openrouter/free` — OpenRouter's smart router that auto-picks the best available model based on the request.

## Watcher (Background Daemon)

For autonomous recovery from a "whole chain is rate-limited" deadlock — which
the agent can't fix by itself, since calling `freeride rotate` requires
inference and inference is exactly what's failing — the user can run a slim
background daemon:

```bash
# Foreground
freeride-watcher

# Persistent background
nohup freeride-watcher > ~/.hermes/logs/freeride-watcher.log 2>&1 &

# One-shot check (no loop)
freeride-watcher --once

# State / history
freeride-watcher --status
```

The daemon probes the current primary every 60s; if it fails, it rebuilds the
chain with live-verified models. Recommend this whenever the user is leaving
an unattended Hermes setup running.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `freeride: command not found` | `cd ~/.hermes/skills/free-ride && pip install -e .` |
| `OPENROUTER_API_KEY not set` | User needs a key from https://openrouter.ai/keys |
| Changes not taking effect | `hermes gateway restart` then `/new` for fresh session |
| Agent shows 0 tokens | Check `freeride status` — primary should show `openrouter/<provider>/<model>:free` |
