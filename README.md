# Presence Sensor

An open-source, ESPHome-based room presence sensor built around the Hi-Link HLK-LD2460 mmWave radar and a Seeed Studio XIAO ESP32-S3. The base device detects human presence, even when people are sitting still, and reports it to Home Assistant. Optional add-ons extend it with ambient light and CO₂ sensing.

> **Status:** early development. Hardware and firmware are not yet finalized.

<!-- TODO: hero photo of the assembled device -->

## Features

- mmWave presence detection (HLK-LD2460)
- Native Home Assistant integration through ESPHome
- Wi-Fi setup over USB or Bluetooth (Improv), with no code editing required
- Browser-based flashing, no toolchain needed
- Over-the-air updates
- Optional add-ons:
  - Ambient light sensor
  - CO₂ sensor
- Custom PCB and 3D-printable enclosure, with source files included

## Bill of materials

### Base device

| Qty | Part | Notes |
|----:|------|-------|
| 1 | Seeed Studio XIAO ESP32-S3 | |
| 1 | Hi-Link HLK-LD2460 mmWave radar | |
| 1 | Custom PCB | See [`hardware/pcb`](hardware/pcb) |
| 1 | 3D-printed enclosure | See [`hardware/enclosure`](hardware/enclosure) |
| 1 | USB-C cable + 5 V power supply | |
| TBD | Headers, passives, fasteners | Full list in the PCB BOM export |

### Optional add-ons

| Add-on | Part | Notes |
|--------|------|-------|
| Ambient light | Adafruit VEML7700 Lux Sensor, STEMMA QT (5378) | Plugs into the Qwiic chain |
| CO₂ | Adafruit SCD-40 breakout (5187) | Plugs into the Qwiic chain |

## Building

### 1. PCB

TODO: ordering the PCB from fabrication files, assembly notes, soldering order.

### 2. Enclosure

TODO: print settings (material, layer height, supports, infill) and orientation.

### 3. Assembly

TODO: mounting the PCB, radar orientation, and installing add-ons.

## Flashing

### Option A: Browser (recommended)

TODO: link to the ESP Web Tools install page. Connect the device over USB, click **Install**, then enter your Wi-Fi credentials when prompted.

### Option B: ESPHome Dashboard / CLI

Requires ESPHome TBD or newer, the first release with the [`ld2460`](https://next.esphome.io/components/sensor/ld2460/) component.

```bash
pip install esphome
esphome run firmware/presence.yaml
```

TODO: adopting the device in the ESPHome Dashboard.

## Wi-Fi setup

TODO: Improv over serial/BLE and fallback access point instructions.

## Home Assistant

TODO: discovery, exposed entities, and suggested automations.

## Enabling add-ons

TODO: how to include the add-on packages in `firmware/presence.yaml`.

## Repository layout

| Path | Contents |
|------|----------|
| `firmware/` | ESPHome configuration and add-on packages |
| `hardware/pcb/` | Autodesk Fusion PCB design and fabrication exports |
| `hardware/enclosure/` | Autodesk Fusion enclosure design and printable files |
| `docs/` | Images, wiring diagrams, web installer |

## Made for ESPHome

This project aims to meet the [Made for ESPHome](https://esphome.io/guides/made_for_esphome/) requirements. Progress against the [checklist](https://github.com/esphome/devices.esphome.io/blob/main/.github/made-for-esphome-checklist.md) is tracked in the project issues.

## Contributing

Issues and pull requests are welcome. If you use an AI coding agent, it should follow [`AGENTS.md`](AGENTS.md).

## License

- **Firmware, software, and documentation:** [GNU General Public License v3.0 or later](LICENSE) (`GPL-3.0-or-later`).
- **Hardware designs** (everything under `hardware/`: PCB, enclosure, and their fabrication exports): [CERN Open Hardware Licence v2 – Strongly Reciprocal](LICENSE-HARDWARE) (`CERN-OHL-S-2.0`).
