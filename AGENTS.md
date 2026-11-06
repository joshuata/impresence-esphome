# AGENTS.md

Instructions for AI coding agents working in this repository. These apply to every agent (Claude Code, Codex, Copilot, Cursor, Gemini, etc.). Keep this file and everything under `.agents/` tool-neutral: no vendor-specific syntax, commands, or file paths.

## Project

Open-source room presence sensor built on ESPHome.

- **MCU:** Seeed Studio XIAO ESP32-S3
- **Core sensor:** Hi-Link HLK-LD2460 24 GHz mmWave presence radar (UART)
- **Optional add-ons:** ambient light sensor, PIR motion sensor, CO₂ sensor
- **Hardware design:** Autodesk Fusion (PCB + 3D-printed enclosure)
- **Goal:** meet the [Made for ESPHome checklist](https://github.com/esphome/devices.esphome.io/blob/main/.github/made-for-esphome-checklist.md). Treat it as the acceptance criteria; re-read it before changing firmware, docs, or release process.

## Repository layout (target)

```text
firmware/            ESPHome configuration
  presence.yaml      Main device config (what users adopt / flash)
  boards/            Board package: XIAO pin-to-GPIO substitutions and platform settings
  packages/          One package per optional add-on (light, pir, co2)
hardware/
  pcb/               Fusion electronics design + exported Gerbers/BOM/CPL
  enclosure/         Fusion design + exported STL/3MF/STEP
docs/                Images, wiring diagrams, web installer page
.agents/plans/       Active implementation plans (see below)
  archived/          Completed plans
.agents/skills/      Generic agent skills (see below)
AGENTS.md            This file
README.md            User-facing documentation
```

Create directories as they are needed; do not add empty placeholders.

## Board compatibility

The XIAO ESP32-S3 is the only supported board. Don't mention other boards in the README or user-facing docs. Do avoid any design decision that would stop us from adding XIAO ESP32-C6 support later:

- **PCB:** route only to the 14 edge pins (D0–D10, 5V, 3V3, GND), which sit in the same positions across XIAO boards. Don't use the bottom-side pads. Label nets by XIAO pin name (`D0`, `D6`, …), not GPIO number.
- **Firmware:** reference pins only through substitutions defined in the board package (`firmware/boards/`). Shared config must not hard-code GPIOs or board-specific options, so a C6 package can be added later.
- **Framework:** use ESP-IDF.
- **Peripherals:** when assigning pins or choosing features, check that the C6 has an equivalent: UART count, BLE for Improv, ADC on the chosen pin, and no conflict with C6 strapping or internally used pins. If an S3-only choice is clearly better, it's allowed, but flag the trade-off to the user first.

## Conventions

### Firmware (ESPHome YAML)

- The main config must work with **no add-ons installed**. Each add-on lives in its own file under `firmware/packages/` and is enabled by including the package.
- Keep `esphome.project` name/version, `dashboard_import`, and Wi-Fi provisioning settings in line with the Made for ESPHome checklist.
- Never commit secrets. Use `!secret` references; real `secrets.yaml` files are git-ignored.
- Use substitutions for pins and names so alternative board variants only change substitutions.
- Validate every change with `esphome config firmware/presence.yaml` before considering it done. Compile (`esphome compile ...`) when touching components or platform settings.
- The LD2460 uses ESPHome's native `ld2460` component ([docs](https://next.esphome.io/components/sensor/ld2460/)). It is currently only on the dev channel. Assume it will be in a stable ESPHome release before this project ships, so build against the dev/beta channel during development. Don't add workarounds or an external component for it. Once it ships, set the minimum ESPHome version in the README.
- Take config keys from the ESPHome docs for the version you are targeting; don't guess them. The same applies to add-on sensor components.

### Hardware (Fusion)

- Fusion source files are the source of truth. Commit the native files **and** fabrication exports (Gerbers, drill, BOM, pick-and-place, STL/3MF/STEP) so users without Fusion can build the device.
- Regenerate exports whenever the source design changes, in the same commit.
- Pin assignments in the PCB must match `firmware/` substitutions. When changing either, update both and the README wiring table.

### Documentation

- `README.md` is for builders/users: what it is, BOM, build, flash, add-ons, Home Assistant integration.
- Keep the BOM in the README in sync with the PCB BOM export.
- Prefer concrete part numbers and supplier-neutral links (manufacturer pages) over affiliate or single-store links.

### General

- License: firmware, software, and docs are GPL-3.0-or-later (`LICENSE`); everything under `hardware/` is CERN-OHL-S-2.0 (`LICENSE-HARDWARE`). Don't add dependencies or assets with incompatible licenses.
- Keep changes small and focused; one logical change per commit.
- Don't fabricate part specs, pinouts, or datasheet values. Cite the datasheet or mark the value `TBD`.

## Plans

Write implementation plans for multi-step work as Markdown files in `.agents/plans/`, named `YYYY-MM-DD-short-description.md`. Each plan states the goal, the steps as a checklist, and open questions. Update the checklist as work progresses. When a plan is complete (or abandoned), move it to `.agents/plans/archived/` with `git mv` and note the outcome at the top of the file.

## Skills

Reusable, tool-agnostic task instructions live in `.agents/skills/<skill-name>/SKILL.md`. Each skill is plain Markdown with a short YAML front matter (`name`, `description`) followed by step-by-step instructions that any agent can follow using ordinary shell commands. Don't reference tool-specific features inside a skill.

## hk

- Ask the hk MCP server to inspect the project and plan checks before execution.
- Scope work to changed files (`--files0-from` accepts exact NUL-delimited paths) and use `--cd` for another project root.
- Prefer safe checks and safe fixes. Inspect command effects and ask before any unknown or destructive command.
- Read normalized diagnostics from structured results, then inspect the patch before reporting or committing a fix.
- If MCP is unavailable, run `hk run check --format jsonl --safe`; the final event is the authoritative summary.
