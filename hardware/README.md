# Hardware

The Autodesk Fusion project **Presence sensor** holds the source designs. Exports are kept here so they are version controlled and usable without Fusion (see `AGENTS.md`, Hardware).

| Path | Contents |
|------|----------|
| `fusion/` | Fusion source exports (`.f3d`; `.f3z` for designs with inserted, referenced components) |
| `pcb/` | Fabrication outputs for the main PCB (once finalized) |
| `enclosure/` | Print outputs for the case (once finalized) |

## Designs

| Design | What it is |
|--------|------------|
| `ld2460 Board` | HLK-LD2460 radar: board, headers, pins, keep-outs |
| `xiao-esp32s3` | Seeed XIAO ESP32-S3: board, pin holes, USB-C, keep-out |
| `adafruit-scd40` | Adafruit SCD-40 breakout (for later case variants) |
| `adafruit-veml7700` | Adafruit VEML7700 breakout (for later case variants) |
| `presence-skeleton` | Master layout for the radar + PCB prototype. Derives the radar and XIAO models and holds every case, PCB, mount and antenna dimension |

## Changing dimensions

The dimensions you're likely to change are named user parameters, and most others are derived from them or from the component models. In Fusion, open `presence-skeleton` and go to **Modify → Change Parameters**. Edit the value in the *User Parameters* section, and everything that depends on it updates. Parameters ending in `_Ref` come from the component models; change those in the component design instead. The PCB and case designs derive from the skeleton, so changes made there flow through to them.

Values most people will want to check before printing are **bold**.

### Layout

| Parameter | Value | Description |
|-----------|-------|-------------|
| `pcb_thickness` | 1.6 mm | Main PCB thickness |
| **`pcb_socket_h`** | 4.3 mm | Height of the 2.0 mm female sockets the radar plugs into. Set to the part you buy |
| `pcb_margin` | 2 mm | PCB extends this far beyond the radar outline |
| `pcb_hole_inset` | 3 mm | PCB edge to mounting-hole centre |
| `pcb_pin_protrusion` | 2 mm | Through-hole pin length below the PCB |
| `layout_gap_radar_xiao` | 3 mm | Gap between the radar outline and the top of the XIAO |
| `xiao_side_offset` | 10 mm | XIAO shifted right (toward the antenna) to leave room on the left for a right-angle USB-C plug |

### Case

| Parameter | Value | Description |
|-----------|-------|-------------|
| `case_wall` | 2 mm | Wall thickness |
| `case_corner_r` | 3 mm | Outer corner radius |
| `case_margin` | 1 mm | Clearance from the PCB edge to the inner wall |
| **`case_radome_t`** | 1.4 mm | Wall thickness in front of the radar (community reports for 24 GHz; verify with a range test) |
| **`case_radome_gap`** | 2 mm | Radar antenna face to the inside of the front wall (1–3 mm) |
| **`case_bay_h`** | 12.5 mm | Cable bay below the PCB; sized for a right-angle USB-C plug |
| **`tol_clearance`** | 0.2 mm | General clearance between printed parts; tune for your printer |

### Fasteners

| Parameter | Value | Description |
|-----------|-------|-------------|
| `screw_clear_d` | 2.7 mm | M2.5 clearance hole in the PCB |
| **`insert_hole_d`** | 3.6 mm | Heat-set insert hole diameter. Inserts vary by brand; use your supplier's recommendation |
| **`insert_hole_h`** | 4 mm | Heat-set insert hole depth |
| `insert_boss_d` | 6.5 mm | Boss diameter around each insert |

### Wall mount (keyholes)

The back has two keyholes on the vertical centreline. Any accessory, such as a wedge or stand, that presents two #8 pan-head screw heads (or printed studs of the same shape) at this spacing can hold the case.

| Parameter | Value | Description |
|-----------|-------|-------------|
| **`mount_head_d`** | 7.9 mm | #8 pan-head diameter (ASME B18.6.3 nominal; measure yours) |
| **`mount_head_h`** | 2.8 mm | #8 pan-head height (nominal; measure yours) |
| `mount_shank_d` | 4.2 mm | #8 shank diameter |
| `mount_keyhole_spacing` | 40 mm | Keyhole centre-to-centre |
| `mount_slot_len` | 8 mm | Slot length above each entry hole |

### Hinge

| Parameter | Value | Description |
|-----------|-------|-------------|
| **`hinge_pin_d`** | 1.75 mm | Hinge pin: a piece of 1.75 mm filament or a metal pin |
| `hinge_knuckles` | 5 | Number of hinge knuckles |
| `hinge_clearance` | 0.3 mm | Knuckle and pin clearance |

### Wi-Fi / Bluetooth antenna

The XIAO's included flexible antenna sticks flat to the inside of the right-hand side wall. Its U.FL cable makes a 180° U-bend before reaching the XIAO, to take strain off the antenna joint.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `ant_len` × `ant_w` × `ant_t` | 37.5 × 17.5 × 0.25 mm | Antenna size (measured) |
| `ant_cable_len` | 60 mm | U.FL cable length (measured) |
| `ant_bend_gap` | 6 mm | Spacing of the U-bend |
| `ant_drop` | 5 mm | Antenna centre below the radar centreline |
| `xiao_ufl_from_edge`, `xiao_ufl_from_centre` | 1.72, 4.73 mm | U.FL connector position on the XIAO (from Seeed's 3D model) |

### USB cable

| Parameter | Value | Description |
|-----------|-------|-------------|
| `usb_plug_w` × `usb_plug_h` | 12 × 6.5 mm | Straight USB-C plug body (measure your cable) |
| `usb_cable_d` | 4 mm | Cable diameter |
| `usb_cable_bend_r` | 10 mm | Minimum bend radius |

### Derived values (don't edit)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `z_antenna_face` | 8.0 mm | Radar antenna face above the PCB front |
| `case_front_inner` | 10.0 mm | Inside of the front wall above the PCB front |
| `pcb_back_clear` | 6.3 mm | Space behind the PCB: the largest of pin clearance, insert depth and the depth the antenna needs |
| `case_inner_depth` | 17.9 mm | Inside depth of the case |
| `case_inner_half_w`, `case_inner_top`, `case_inner_bottom` | 27.75, 19.0, 52.455 mm | Inner case extents from the radar centre |
| `ant_path_len` | 44.2 mm | Estimated antenna cable route |
| `ant_path_slack` | 15.8 mm | Spare cable. **Must stay ≥ 0**; adjust `ant_drop` if it goes negative |

At these values the case is about 59.5 × 75.5 × 21.3 mm (W × H × D).
