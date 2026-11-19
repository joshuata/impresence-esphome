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
| 1 | Custom PCB, assembled | Order it with assembly; see [1. PCB](#1-pcb) |
| 1 | 3D-printed enclosure | See [`hardware/enclosure`](hardware/enclosure) |
| 1 | USB-C cable + 5 V power supply | |
| 1 | PCB parts (radar sockets, Qwiic socket, LDO, passives) | Only if you assemble the PCB yourself. Full list in [`hardware/pcb/presence-pcb-bom.csv`](hardware/pcb/presence-pcb-bom.csv) |
| 4 | M2.5 screws + heat-set inserts | Length TBD with the case |

### Optional add-ons

| Add-on | Part | Notes |
|--------|------|-------|
| Ambient light | Adafruit VEML7700 Lux Sensor, STEMMA QT (5378) | Plugs into the Qwiic chain |
| CO₂ | Adafruit SCD-40 breakout (5187) | Plugs into the Qwiic chain |

## Building

### 1. PCB

The fabrication files are in [`hardware/pcb`](hardware/pcb):

| File | What it's for |
|------|---------------|
| `presence-pcb-gerbers.zip` | Gerber and drill files. Upload this to any PCB maker |
| `presence-pcb-bom.csv` | Every part on the board, with manufacturer and LCSC part numbers |
| `presence-pcb-bom-jlcpcb.csv` | Assembly BOM in JLCPCB's format |
| `presence-pcb-cpl-jlcpcb.csv` | Pick-and-place (CPL) file in JLCPCB's format |

The board has two layers and is 53.5 × 57.955 mm, 1.6 mm thick. It uses 0.2 mm minimum tracks and clearances and 0.3 mm via drills, which any standard PCB service can make. Every part is on the top side.

#### Ordering from JLCPCB with assembly

JLCPCB can build the board with everything fitted except the XIAO, which you solder yourself. The optional parts (R1, R2, J4) are left off; see [Optional parts](#optional-parts).

1. On [jlcpcb.com](https://jlcpcb.com), start a PCB order and upload `presence-pcb-gerbers.zip`. Check that it detects 2 layers and a size of about 53.5 × 58 mm.
2. Set the PCB options:
   - **Base material:** FR-4
   - **Layers:** 2
   - **PCB thickness:** 1.6 mm
   - **Surface finish:** lead-free HASL or ENIG
   - **Quantity:** however many bare boards you want
   - Leave the other options at their defaults. Some colours and finishes aren't offered with Economic assembly; the site greys those out.
3. Turn on **PCB Assembly** and set:
   - **PCBA type:** Economic
   - **Assembly side:** Top side
   - **PCBA quantity:** the number of boards to assemble. The minimum is 2.
   - **Confirm parts placement:** yes. A JLCPCB engineer checks the part orientations and sends them to you to approve before assembly, for a small fee. It's worth it until the files have been proven on a real order.
4. Upload `presence-pcb-bom-jlcpcb.csv` as the BOM and `presence-pcb-cpl-jlcpcb.csv` as the CPL (pick-and-place) file.
5. On the parts page, check that every line matched the LCSC part number in the file. There should be eight lines:
   - **Basic parts:** C1–C5, FB1
   - **Extended parts:** U2, J1, J2, J3. Each unique extended part adds a feeder-loading fee.
   - **J1 and J2:** the radar sockets are through-hole, so JLCPCB solders them by hand and adds a small through-hole fee. To solder them yourself instead, untick them and buy HCTL PM200-2-04-Z-4.3 and PM200-2-02-Z-4.3. Any substitute must be 4.3 mm tall (`pcb_socket_h`), or the radar won't line up with the case.
   - **Out-of-stock parts:** choose one with the same value, rating and footprint. For J3, use only the JST BM04B-SRSS-TB or an exact equivalent: the case is shaped around its height.
6. In the placement preview, check that every part sits on its pads and that the polarised parts point the right way:
   - **J1:** the 2×4 socket lies along its two columns of four holes. The CPL file already corrects for JLCPCB's model being drawn at 90° to the footprint
   - **U2:** pin 1
   - **J3:** the four contacts on the small pads and the mounting tabs on the two large ones
7. Add the order to your cart and check out. JLCPCB asks for a product description for customs; pick the closest one.

The Gerber zip works with any other PCB maker too. Other assembly services need their own BOM and CPL formats; build them from `presence-pcb-bom.csv`.

#### After the boards arrive

1. **XIAO ESP32-S3 (U1):** solder it flush, with its castellated edges on the pads, or on pin headers. Only the 14 edge pins are used. There's no copper under the XIAO's bottom pads, so don't solder those.
2. **Check before powering:** before powering the first board, check the radar socket pinout against a module, following [Wiring](hardware/README.md#wiring). In short: JP103 pin 1 (5 V) is the bottom pin of the column nearest the board edge.

#### Optional parts

| Ref | Part | When to fit it |
|-----|------|----------------|
| R1, R2 | 4.7 kΩ 0805 resistors (I²C pull-ups) | Only for a Qwiic breakout without its own pull-ups. The Adafruit breakouts have them |
| J4 | 1×4 2.54 mm header | To solder an I²C cable instead of using the Qwiic socket |

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
