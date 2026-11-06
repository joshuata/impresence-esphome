# PCB and enclosure layout

**Status:** draft, awaiting approval

## Goal

Design the main PCB and the 3D-printed wall-mount enclosure in Autodesk Fusion. Everything is parametric and fully constrained: every sketch is fully constrained, and every dimension comes from a named user parameter or a reference to other geometry, with no bare numbers.

## Decisions

| Topic | Decision |
|-------|----------|
| Mounting | Flat back with a standard keyhole mount interface (see below). The case hangs directly on wall screws (radar parallel to the wall), or on an optional printed wedge set to the recommended angle |
| Wedge | Fixed-angle wedge, `wedge_angle` default 30° (manual: 25–40°). The back has the same keyholes as the case, so it hangs on the same wall screws. The front has studs that mate with the case keyholes. Set the radar's mounting angle in its config to match |
| Add-ons | Plug-in STEMMA QT/Qwiic breakouts (SCD40, VEML7700) on one daisy chain from a JST-SH socket on the main PCB. Connect only what you want |
| CO₂ | Sensirion SCD40 on a breakout board (I²C). The SCD41's extended range isn't needed, and a breakout avoids hand-soldering an LGA part |
| Light | Adafruit VEML7700 Lux Sensor, STEMMA QT (product 5378) or a clone with the same layout. Daisy-chained on the Qwiic bus with the SCD40 |
| PIR | None; the radar covers motion detection |
| Breakout mounting | Mount to the case, not to PCB standoffs. M2.5 screws into posts on the front shell, with heat-set inserts or holes for self-tapping screws (`tol_` parameters). Post positions come from each breakout model, and the posts stay even when a breakout isn't fitted. This keeps the VEML7700 aligned to its window and the SCD40 away from heat, and the main PCB doesn't need to know where the sensors are |
| Assembly | Mixed: hand-solderable SMD (≥0805 passives, leaded ICs where possible) with optional factory assembly; through-hole headers |
| MCU | XIAO ESP32-S3, edge pins only (C6-compatible footprint) |
| Power | USB-C on the XIAO |

## Fusion structure

All files live in the Fusion project **Presence sensor**.

1. **`presence-skeleton`**: master design that holds only user parameters and the layout sketches: board outline, component keep-outs, case envelope, and the radar window. This is the single place to change dimensions.
2. **Component models**, one design each, parameterized from datasheets:
   - `ld2460 Board` (exists; refactor to named parameters)
   - XIAO ESP32-S3 (use the Seeed STEP if its license allows redistribution, otherwise model it)
   - `adafruit-scd40` and `adafruit-veml7700` breakouts (dimensions from Adafruit's MIT-licensed CAD parts)
3. **`presence-pcb`**: Fusion Electronics design (schematic + board). The board outline and mounting holes are taken from the skeleton. Component placement is constrained to skeleton sketch geometry.
4. **`presence-enclosure`**: front shell and flat back plate with mount-interface keyholes. Derives parameters and sketches from the skeleton and inserts the PCB's 3D model.
5. **`presence-wedge`**: angled wall wedge. Derives the mount interface from the skeleton.
6. **`presence-assembly`**: top-level assembly (case on wall, case on wedge) for interference checks and renders.

Naming: parameters use `snake_case` with a prefix per area: `pcb_`, `case_`, `mount_`, `wedge_`, `ld2460_`, `xiao_`, `scd40_`, `light_`, `tol_`.

## Mount interface

A small, documented interface, so that anyone can design a new accessory (wedge, desk stand, ceiling plate, …) from a handful of numbers:

- **Keyholes:** two on the back, `mount_keyhole_spacing` apart on the vertical centreline. Each is an entry hole (`mount_head_d` + clearance) with a slot (`mount_shank_d` + clearance) running `mount_slot_len` upward. Behind each slot, a pocket `mount_head_h` + clearance deep holds the head.
- **Mating feature:** anything that presents two "screw heads" at `mount_keyhole_spacing`. That can be a real wall screw (default: #8 / 4 mm pan or round head) or a printed stud with the same head and shank geometry.
- **Printed studs:** the head undersides are chamfered at 45°, so they print without supports when the part lies on its side. A matching chamfer in the slot pulls the case tight against the accessory.
- **Single source:** all `mount_*` parameters live in the skeleton. The case, the wedge and future accessories derive them from there. Document the interface (drawing plus parameter table) in `hardware/README.md` for people designing their own accessories.
- **Optional:** a small detent or a set-screw hole at the bottom of the case, so it can't be lifted off the studs. Every parameter has a comment that cites its source: a datasheet section, "design choice", or "derived".

## LD2460 reference data (Manual V1.1)

- Board 32.00 × 49.50 mm (Fig. 1; confirmed by measurement). Thickness 1.2 mm (measured). Corner radius ≈1.5 mm (estimated from Fig. 1; not critical). Tallest components (measured): 1.45 mm on the header side (main IC); 0.8 mm on the antenna side (two ICs).
- Headers are male, 2.0 mm pitch, on the component side. The antennas are on the opposite side. There are no mounting holes.
  - 2×4 J1: outer pin columns 12.22 mm from the left edge and 13.78 mm from the right edge. Pins 5–8 = VDD33, GND, Tx2, Rx2 (inner row); 9–12 = IO1–IO4 (edge row).
  - 2×2 JP103 on the opposite end: pin columns 13.69 mm from the left edge and 16.32 mm from the right edge. Pins 1–4 = 5V, GND, Tx1, Rx1.
  - 2×2 body (measured): 4.0 mm (perpendicular to the near edge) × 3.8 mm, spanning 2.0–6.0 mm from the near short edge. With pins centred in the body, the pin rows are 3.0 and 5.0 mm from the edge, which matches the existing model.
  - Inner pin rows of the two headers are 39.5 mm apart centre to centre (measured: 39.0 between inner faces, ~40.0 across outer faces). So the 2×4 rows are also 3.0 / 5.0 mm from their edge. This matches the model.
  - Header height (measured): plastic body top 2.5 mm above the board surface; pin tips ≈6.5 mm above it (4.0 mm exposed above the body).
  - 2×4 body size: not measured; assume the same 4.0 mm depth as the 2×2 and 2 mm per column (≈7.8 mm wide).
- Tx2/Rx2 carry the radar data and commands. Default 115200 8N1.
- Supply: 5 V (4.2–5.4 V), ≤250 mA average, low ripple required (§9.4). VDD33 is not connected.
- Side mount: recommended 25–40° between module and wall, at 2.2–2.7 m height. Field of view: 90° horizontal × 50° vertical.

## Layout constraints to respect

- **Radar:** the antenna side faces the room. No copper pour, components or screws in front of the antennas. Keep the case wall in front of the radar uniform: `case_radome_t` = 1.4 mm, with a `case_radome_gap` of 1–3 mm (default 2 mm) between the antenna face and the wall. These values come from community reports, not the manual, so verify detection range on a test print. The gap must stay larger than the 0.8 mm antenna-side keep-out.
- **SCD40 (Adafruit 5187 breakout or a pin-compatible clone):** mounts on M2.5 posts in the case, at the bottom near the intake vents (warm air rises), away from the ESP32, radar and regulators. It connects to the main PCB by a short STEMMA QT/Qwiic cable. Leave cable-bend clearance beyond the JST-SH connector on the cable side. The case needs inlet and outlet vents so air flows through.
- **Light sensor (Adafruit VEML7700 breakout):** the sensor is mounted top-view at one long edge of the breakout, so it looks out from the board face. The breakout mounts on M2.5 posts in the case with the sensor behind a window or light pipe in the front face, outside the radar's footprint. Use the `Sensitive area centre` sketch to place the window. Keep it away from the XIAO's LEDs.
- **XIAO:** USB-C reachable through the case for power and flashing. The BOOT/RESET buttons reachable or exposed via pin holes.
- **Pins:** use only XIAO edge pins. Label nets by XIAO pin name.

## Steps

### 1. Reference data

- [x] Collect the datasheets: LD2460, XIAO ESP32-S3, SCD40 and VEML7700. Store them locally per `docs/datasheets/README.md`.
- [x] Confirm the LD2460 pinout, supply voltage and mounting (see "LD2460 reference data"). The manual gives no antenna keep-out or radome guidance.
- [x] Settle the add-on parts: VEML7700 light sensor, no PIR.

### 2. Pin assignment

- [x] Assign XIAO pins (sources: XIAO ESP32S3 schematic v1.4, ESP32-S3 datasheet v2.2, XIAO ESP32-C6 schematic v1.0):

  | Function | XIAO pin | S3 GPIO | C6 GPIO | Notes |
  |----------|----------|---------|---------|-------|
  | I²C SDA | D4 | 5 | 22 | SCD40 0x62, VEML7700 0x10. Pull-ups are on the breakouts |
  | I²C SCL | D5 | 6 | 23 | |
  | Radar TX → LD2460 Rx2 (pin 8) | D8 | 7 | 19 | |
  | Radar RX ← LD2460 Tx2 (pin 7) | D9 | 8 | 20 | |
  | Radar 5V (LD2460 pin 1) | VBUS (pin 14) | – | – | Through an LC filter and bulk capacitor (§9.4: low ripple) |
  | GND | GND (pin 13) | – | – | Both radar GND pins (2, 6) |
  | Spare, to test pads | D0, D1, D3, D6, D7, D10 | 1, 2, 4, 43, 44, 9 | 0, 1, 21, 16, 17, 18 | Not D2: GPIO3 is an S3 strapping pin |

  - The radar isn't on D6/D7 because those are UART0 (U0TXD/U0RXD) on both chips, and boot-ROM log output there would reach the radar's Rx.
  - S3 strapping pins: GPIO0, 3, 45, 46. The C6 schematic says to avoid GPIO4, 5, 8, 9 and 15, and its RF switch uses GPIO3 and GPIO14. None of these are used.
- [x] Write `firmware/boards/xiao-esp32s3.yaml` substitutions to match. `esphome config` passes with a test config that uses the package.

### 2b. Power

- Qwiic chain (SCD40 + VEML7700 breakouts): the main PCB's JST-SH socket supplies **3.3 V** from a dedicated LDO (fed from 5 V, separate from the XIAO 3V3). Not 5 V: both breakouts pull their connector-side I²C lines up to V+ (Adafruit schematics rev B: SCD-40 10 kΩ, VEML7700 4.7 kΩ), and the ESP32 isn't 5 V tolerant. A clean, separate 3.3 V also meets Sensirion's ≤30 mV ripple / separate-LDO recommendation for the SCD40 (peak 205 mA at 3.3 V).
- VEML7700: XIAO 3V3 (2.5–3.6 V).
- LD2460: 5 V from VBUS through an LC filter.

### 3. Skeleton

- [ ] Create `presence-skeleton` with all user parameters.
- [ ] Sketch the board outline, the component zones, the radar window and the case envelope. All sketches fully constrained.

### 4. Component models

- [x] Refactor `ld2460 Board`: all dimensions driven by `ld2460_*` user parameters; corner fillet, header bodies, pins and keep-out bodies for the header side and antenna side added. All sketches are fully constrained, and the model rebuilds cleanly after changing width, length, pitch, column count and margins. Limitation: the pin extrude uses a fixed profile selection, so changing `ld2460_j1_cols`/`ld2460_jp103_cols` moves the header bodies but doesn't add or remove pins.
- [x] XIAO ESP32-S3 model (saved as `xiao-esp32s3`): `xiao_*` parameters measured from Seeed's STEP; board, 2×7 pin holes (feature pattern, count-driven), mid-mount USB-C, top keep-out. Fully constrained, flex-tested, matches the STEP within 0.01 mm. Not modelled: bottom pads (unused by design), buttons and U.FL (inside the keep-out).
- [x] Adafruit SCD-40 breakout model (saved as `adafruit-scd40`): `scd40_*` parameters measured from Adafruit's MIT-licensed STEP and fab print. Board with corner radius, 2×2 mounting holes and 5-pin header (count-driven patterns), SCD40 body, mirrored JST-SH connectors, top keep-out. Fully constrained, flex-tested, matches the STEP exactly.
- [x] Adafruit VEML7700 breakout model (saved as `adafruit-veml7700`): board 25.4 × 17.78 mm, Ø2.5 mounting holes on 20.32 × 12.7 mm, 5-pin header, VEML7700 body and sensitive-area marker, mirrored JST-SH, top keep-out. Measured from Adafruit's MIT-licensed STEP and fab print; fully constrained and flex-tested; matches the STEP within 0.01 mm. The bare-chip `veml7700` design is superseded.

### 5. PCB

- [ ] Schematic: XIAO, LD2460 headers, LD2460 5 V filter, JST-SH (Qwiic) socket with dedicated 3.3 V LDO, decoupling, test pads for spare pins. Both breakouts have 10 kΩ pull-ups; add optional unpopulated pull-up pads on the main PCB.
- [ ] Board: outline and holes from the skeleton; placement; routing; ground pour with radar keep-out; silkscreen labels for optional parts.
- [ ] Pass DRC/ERC; export Gerbers, drill, BOM and pick-and-place to `hardware/pcb/`.

### 6. Enclosure

- [ ] Front shell with radome area, light window and vents.
- [ ] Back plate with PCB standoffs and USB-C opening.
- [ ] Breakout posts on the front shell: SCD40 (4 × Ø3.0 holes, 20.32 × 17.78 mm) near the intake vents; VEML7700 (4 × Ø2.5 holes, 20.32 × 12.7 mm) behind the light window. Hole positions are derived from the breakout models. Leave cable routing room for the Qwiic chain.
- [ ] Flat back with mount-interface keyholes.
- [ ] Wedge: back keyholes, front studs, `wedge_angle` driven; prints on its side without supports.
- [ ] Document the mount interface in `hardware/README.md`.
- [ ] Print-friendly: no supports needed, and clearances from `tol_` parameters.
- [ ] Export STL/3MF/STEP to `hardware/enclosure/` (case and wedge).

### 7. Verify

- [ ] Interference check in `presence-assembly`, both on the wall and on the wedge.
- [ ] Change key parameters (board size, wall thickness, `wedge_angle`, `mount_keyhole_spacing`) and confirm every design rebuilds without errors.
- [ ] Test-print the keyhole and stud fit; tune the `tol_` values.
- [ ] Update the README parts list and wiring table.

## Open questions

- Radome: 1.4 mm wall, 1–3 mm gap (community reports; the manual gives no guidance). Confirm with a range test in PLA and PETG.
- Mount screw: #8 pan head (decided). Nominal sizes from ASME B18.6.3: head Ø ≈7.9 mm, head height ≈2.8 mm, shank Ø ≈4.2 mm. Measure real screws before finalizing `mount_head_d` / `mount_head_h` / `mount_shank_d`.
- Breakout mounting holes measure Ø3.0 mm in Adafruit's STEP (M2.5 screws). Confirm on a real board or clone.
- Can the Seeed XIAO and Sensirion STEP models be redistributed under CERN-OHL-S, or do we model them ourselves?
- Where Fusion's native files will live in the repo: export `.f3d`/`.fbrd`/`.fsch` archives to `hardware/`, plus a link to a public Fusion share?
