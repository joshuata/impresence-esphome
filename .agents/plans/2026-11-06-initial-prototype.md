# Roadmap to the initial prototype (radar + main PCB)

**Status:** in progress. Steps 1–2 and 5 done. Step 3 (firmware v0) is done on branch `worktree-firmware-v0` (ESPHome 2026.11.0b2), not yet merged.

Detailed reference data (LD2460, pins, power, mount interface, breakouts) lives in `2026-11-06-pcb-and-enclosure-layout.md`.

## Context

All four component models are on `main`. The first prototype is the minimum useful device: the **LD2460 radar and the XIAO ESP32-S3 on the main PCB**, in a wall-mount case that opens like a book. The case also holds the XIAO's 2.4 GHz antenna, which Wi-Fi and the Bluetooth proxy (Bermuda presence) need. The SCD40 and VEML7700 breakouts and the wedge come later as new case variants. The main PCB still gets the Qwiic socket, so those variants need no new PCB.

You've already done the bench test (XIAO wired to the LD2460).

## Answers to your questions

- **Linked references on export:** `.f3z` bundles *inserted* referenced components so the assembly re-imports intact, and Fusion only produces it for designs that contain them. `presence-skeleton` uses derive features instead, so it exports as `.f3d`; its derive links point to the cloud project, so the component `.f3d` files are always exported alongside it.
- **Hand-soldering the SMD Qwiic socket (JST-SH, SM04B-SRSS-TB):** moderate.
  - **The pads:** four signal pads on a 1.0 mm pitch, plus two large mounting tabs.
  - **What you need:** a fine tip, flux, tweezers and some magnification. Tack one tab first, then do the pins.
  - **How hard:** harder than 0805 passives, easier than fine-pitch ICs. Most people manage it on the first try with flux.
  - **Alternatives:** have the board house fit it (the part is standard), or use a 1×4 2.54 mm through-hole footprint wired in parallel. I'll include both footprints, so builders can use either the socket or a soldered-on cable or header.

## Steps

### 1. Skeleton v1: Fusion `presence-skeleton` ✅

Done. The radar and XIAO are derived from their models (favourite parameters come in with a `_Ref` suffix) and placed with parametric move features.

- **Radar:** long edge horizontal, JP103 (2×2) on the viewer's left, which matches the ESPHome `ld2460` side-mount axes. The headers rest on sockets of height `pcb_socket_h`.
- **XIAO:** offset `xiao_side_offset` to the right, USB-C down.
- **Depth:** `pcb_back_clear` is derived with `max(…)`, so the side-wall antenna always fits the case depth.
- **Sketches:** `Layout front`, `Layout section` and `Antenna zone`, all fully constrained and flex-tested.
- **Cable bay:** the right-angle-plug parameters were folded into `case_bay_h`.

- **User parameters,** each with a source or "design choice" comment:
  - **Case:**
    - `case_wall` 2.0, `case_corner_r`, `case_margin`
    - `case_radome_t` 1.4 and `case_radome_gap` 2.0 (community reports; range 1–3)
  - **PCB:**
    - `pcb_thickness` 1.6, `pcb_margin`
    - `pcb_socket_h` (2.0 mm female socket height)
    - `pcb_back_clear` (through-hole pin clearance)
  - **Heat-set inserts (vary by brand):**
    - `insert_hole_d`, `insert_hole_h`, `insert_boss_d`
    - `screw_clear_d` for M2.5
  - **Mount:**
    - `mount_head_d` 7.9, `mount_head_h` 2.8, `mount_shank_d` 4.2 (#8 pan head, nominal)
    - `mount_keyhole_spacing`, `mount_slot_len`
  - **Hinge:**
    - `hinge_pin_d` (e.g. 1.75 mm filament or a metal pin)
    - `hinge_knuckles`, `hinge_clearance`
  - **Antenna (measured):**
    - `ant_len` 37.5, `ant_w` 17.5, `ant_t` 0.25
    - `ant_cable_len` 60; the cable leaves the antenna centre and runs along the long axis, off one short side
    - `ant_bend_gap` 6: spacing of the 180° U-bend
  - **Tolerances:** `tol_clearance` 0.2
- **Component models:** insert `ld2460 Board` and `xiao-esp32s3` as linked references, positioned with joints driven by parameters.
- **All components on the front (room-facing) side of the main PCB.** The back stays flat apart from through-hole pins.
- **Front layout sketch** (PCB half):
  - Radar at the top.
  - XIAO below it at the **bottom edge of the PCB, with USB-C pointing down** and flush with the PCB edge (`xiao_edge_offset`), so the plug never collides with the radar. The U.FL end faces up toward the radar and antenna.
  - **Off-centre for right-angle cables:** the XIAO sits `xiao_side_offset` toward one side (the antenna side, so the U.FL run stays short), leaving room on the other side of the bay for a right-angle USB-C plug to turn and run along the bottom. Size `xiao_side_offset` so a right-angle plug fits in either orientation: `usb_ra_plug_len` and `usb_ra_plug_h` are design choices to start; measure a common right-angle cable. Straight cables still work.
  - **Cable bay:** an open space inside the case below the PCB edge, sized for the plug body plus a cable bend. Parameters: `usb_plug_len`, `usb_plug_w`, `usb_plug_h`, `usb_cable_d` and `usb_cable_bend_r`, all design choices to start; measure your cable. The bay is the one place every case variant routes power from, so a variant only changes where the cable leaves the bay, never the PCB.
  - PCB outline = radar + XIAO + `pcb_margin`.
  - PCB mounting holes clear of the antenna area.
  - Keyhole centres on the vertical centreline.
  - The antenna zone.
- **Antenna zone:**
  - **Where:** stuck flat to the inside of the outer side wall of the PCB half, beside the radar, with the long axis vertical. It stays in the same half as the XIAO, so the cable never crosses the hinge.
  - **Cable route:** the U.FL is at the XIAO's upper end. The cable leaves the antenna along its long axis, makes a 180° U-bend `ant_bend_gap` wide, and runs back to the U.FL. This takes strain off the joint between the cable and the antenna. The bend direction (antenna exit up or down) is whichever fits the 60 mm length.
  - **Check:** a constraint sketch confirms the path length (antenna centre → edge → U-bend → U.FL) is ≤ `ant_cable_len`, and moves the antenna along the wall to fit. The route stays clear of the cable bay.
  - **Clearance:** plastic only around it; no screws, inserts or copper pour near it.
- **Side section sketch (stack-up):**
  - **Radar column:** radome wall → `case_radome_gap` → radar → sockets → PCB.
  - **XIAO column:** cover wall → clearance → USB-C top → PCB.
  - **Behind the PCB:** heat-set insert bosses, then `pcb_back_clear`, then the back wall.
  - **Case depth:** set by the radar column.
- Fully constrained; flex-tested.

### 2. Hardware README: `hardware/README.md` ✅

- A table of every skeleton parameter: name, description, current value, unit and source. It covers what users are likely to change: insert size, wall and radome thickness, tolerances, hinge pin, screw size.
- Also: how to change a parameter in Fusion (Modify → Change Parameters), and a short description of the mount interface.
- AGENTS.md rule: when parameters change, update the table in the same commit.

### 3. Firmware v0: `firmware/presence.yaml`

- Add ESPHome to `mise.toml` (e.g. `"pipx:esphome"`) so `mise install` provides it. Pin a dev/beta version while the `ld2460` component is pre-release.
- Config:
  - `esphome.project`, `dashboard_import` (repo URL)
  - `wifi` + `captive_portal`, `improv_serial`, `esp32_improv`, `api`, `ota`, `logger`
  - `uart` + `ld2460`, using the board package substitutions
  - `esp32_ble_tracker` + `bluetooth_proxy` (active) for Bermuda, with the scan interval and window tuned for Wi-Fi/BLE coexistence
  - External U.FL antenna selection in the board package, if the board needs it
- Take keys from the ESPHome docs for the targeted version. `esphome config` and `esphome compile` must pass.

### 4. Main PCB v0: Fusion Electronics `presence-pcb`

- **Schematic:**
  - XIAO on the front side, edge pins only
  - 2×2 and 2×4 2.0 mm female sockets for the LD2460
  - LC filter + bulk capacitor on the radar's 5 V
  - Qwiic: a JST-SH socket and 1×4 2.54 mm pads in parallel, fed by a dedicated 3.3 V LDO
  - Optional **hardwired 5 V input:** 2-pin 2.54 mm pads (or a small screw terminal) at the PCB edge, feeding VBUS through a Schottky diode so USB and hardwired power can't back-feed each other. It lets a case take bare 5 V wires from anywhere, e.g. from behind, without a USB plug. Check Seeed's guidance on powering the XIAO through its 5V pin before finalizing.
  - Optional unpopulated I²C pull-up pads; test pads for spare pins
- **Board:**
  - Outline and M2.5 holes from the skeleton
  - No copper or parts in front of the radar antennas; ground pour kept away from the antenna zone side
  - Silkscreen labels with XIAO pin names
- DRC/ERC clean. Export a Gerber + drill zip, BOM and CPL to `hardware/pcb/`.

### 5. Case v1: Fusion `presence-enclosure` ✅

Done, with one change from the original plan: at the user's request the book-style hinge and snap latch were dropped for a **simple, sleek press-fit cover** (decided 2026-11-06). The `hinge_*` skeleton parameters are unused for now.

- [x] **Base:** back wall with M2.5 heat-set insert bosses; mount-interface keyholes with closed head pockets; antenna pocket (`ant_len` × `ant_w` + `tol_clearance`, `ant_t` deep) on the right inner wall, plus a U-bend guide post (truncated teardrop, prints without support).
- [x] **Cable exits,** each toggled by a 0/1 parameter (`exit_bottom` default on; `exit_left`, `exit_right`, `exit_back` off). Disabled cutters are moved out of the part, so the timeline stays healthy. Side and back exits are sized from `usb_cable_d` with strain-relief ribs. The bottom exit is sized from `usb_plug_w`/`usb_plug_h` instead: a straight plug is longer than the bay, so its body has to pass through the wall.
- [x] **Cover:** uniform `case_radome_t` radome at `case_radome_gap` in front of the radar; a lip into the base. The left and right lips press-fit (`case_press_fit`, lead-in chamfer); the right one stops below the antenna.
- [x] Small 45° chamfer on the front and back outer edges (`case_edge_chamfer`); no other external features.
- [x] Prints without supports: base on its back, cover radome-down.
- [x] All sketches fully constrained; flex-tested on every enclosure parameter and exit toggle; no interference with the PCB, radar, XIAO or keep-outs (only the intended press fit between cover and base).
- [x] Exports: `hardware/enclosure/presence-enclosure.3mf` (OrcaSlicer project with print settings), `presence-enclosure.step`; `hardware/fusion/presence-enclosure.f3d` and `presence-skeleton.f3d` (its user parameters are now Favourites so the enclosure can derive them; no values changed).
- [ ] Not done: pinholes for BOOT/RESET (the XIAO model has no button positions; would need measured values). Skeleton-parameter flex tests (they need skeleton edits, which are frozen while the PCB is in progress).

### 6. Build and test

- Order the PCB, print the case, fit the inserts, assemble.
- Test:
  - Presence range through the radome (PLA and PETG)
  - Cover press fit (`case_press_fit`)
  - Insert fit
  - USB cable fit in the gap and exit on both sides
  - Hanging on #8 screws
  - Wi-Fi RSSI and Bermuda/BLE proxy reception with the case closed, compared with the bare board
- Tune the `tol_`, `insert_`, radome and `case_press_fit` values, and update the parameter table.

### 7. Later (separate plans)

- Case variants for the SCD40 and/or VEML7700 breakouts (case posts, vents, light window).
- The 30° wedge.
- Web installer and full README.
- **Release pipeline and OTA updates (when ready for release):**
  - **Build:** a GitHub Actions workflow on each version tag builds `firmware/presence.yaml` with ESPHome's official build action, or with the reusable workflows ESPHome publishes. It produces the full first-flash image (`factory.bin`), the update image (`ota.bin`) and a manifest.
  - **Publish:** attach the images to the GitHub Release. Also host the manifest and images on GitHub Pages, so the web installer and devices read one fixed URL.
  - **Device updates:** add `ota: - platform: http_request` and an `update: - platform: http_request` entity pointing at the Pages manifest, so Home Assistant offers one-click updates for each release.
  - **Versioning:** the release tag sets `project_version`, so devices report the release they run.
  - **Before building it:** take the workflow inputs and `http_request` OTA/update keys from the ESPHome docs; this part isn't designed yet. Pin a stable ESPHome release that includes `ld2460` first.

## Process (each step)

- Sketches fully constrained; named parameters for values someone may change or that other designs use; everything else derived where reasonable (AGENTS.md, Modelling style); flex-tested.
- Before each commit: export the changed Fusion designs to `hardware/fusion/` (`.f3d`; `.f3z` only for designs with inserted references). Export fabrication files once a part is finalized.
- `hk run check --all`, a feature branch and one PR per step.

## Files

- `.agents/plans/2026-11-06-pcb-and-enclosure-layout.md`: now marked as reference.
- `AGENTS.md`: why `.f3z` is used; the rule to keep the parameter table updated.
- New: `hardware/README.md`, `firmware/presence.yaml`, an ESPHome entry in `mise.toml`, `hardware/fusion/presence-skeleton.f3d`, `hardware/fusion/presence-enclosure.f3d` (or `.f3z` if it inserts referenced components), `hardware/fusion/presence-pcb.*`, `hardware/pcb/*`, `hardware/enclosure/*`.

## Verification

- **Fusion:** no unhealthy timeline items; fully constrained; flex tests return to the original shape exactly; no interference at default values, including the cover closed against the radar keep-out and the antenna path ≤ cable length.
- **Firmware:** `mise install` provides ESPHome; `esphome config` and `esphome compile` pass.
- **PCB:** DRC/ERC clean; Gerbers previewed before ordering.
- **Prototype:** presence detected through the radome; Bermuda readings comparable to the bare board.
