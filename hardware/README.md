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
| `presence-skeleton` | Master layout for the radar + PCB prototype. Derives the radar and XIAO models and holds every case, PCB, mount and antenna dimension. All user parameters are Favourites so other designs can derive them |
| `presence-enclosure` | Case v1: base and press-fit cover. Derives the skeleton's parameters (`_Ref`), layout sketches and reference bodies |

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

Not used by case v1 (press-fit cover); kept in the skeleton for later variants.

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

## Case v1 (`presence-enclosure`)

A plain box in two printed parts:

- **Base:** back wall, four side walls, M2.5 heat-set insert bosses for the PCB, two keyholes with head pockets (mount interface above), the antenna pocket on the inside of the right wall, and a U-bend guide post for the antenna cable below it.
- **Cover:** the flat radome (`case_radome_t`), with a lip that drops inside the base. The left and right lips are a press fit (`case_press_fit`) with a lead-in chamfer; the top and bottom lips only locate. The right lip stops below the antenna so it never presses on it. Pry the cover off at the seam.
- **Edges:** a small 45° chamfer (`case_edge_chamfer`) on the front and back outer edges; nothing else sticks out.
- **Cable exits:** four options, each switched on or off with a parameter (1/0). Disabled cutters are moved out of the part, so the timeline stays healthy either way.

| Exit | Parameter | Default | What it is |
|------|-----------|---------|------------|
| Bottom | `exit_bottom` | 1 | Opening for a straight USB-C plug body (`usb_plug_w` × `usb_plug_h` + clearance) through the bottom wall, in line with the XIAO's USB-C |
| Left / right | `exit_left`, `exit_right` | 0 | U-slot for the cable (`usb_cable_d`) from the wall top, at the bay floor; the cover closes it. Strain-relief ribs pinch the cable by `exit_grip` |
| Back | `exit_back` | 0 | Hole for the cable (`usb_cable_d`) through the back wall into the wall cavity, with strain-relief ribs. Thread the far end through first |

Enclosure parameters (in `presence-enclosure`, **Modify → Change Parameters**):

| Parameter | Value | Description |
|-----------|-------|-------------|
| **`case_press_fit`** | 0.1 mm | Interference per side between the cover's side lips and the base walls. Tune for your printer; 0 = slip fit |
| `case_lip_h` | 2 mm | Cover lip height into the base |
| `case_lip_t` | 1.2 mm | Cover lip thickness |
| `case_edge_chamfer` | 0.8 mm | Chamfer on the front and back outer edges. Must stay below `case_radome_t` |
| `mount_hood_roof` | 1 mm | Roof over each keyhole head pocket. Above ~1.2 mm it reaches the through-hole pins behind the PCB |
| `ant_cable_d` | 1.13 mm | U.FL pigtail coax diameter (sizes the U-bend guide post); measure yours |
| `exit_grip` | 0.4 mm | How much the strain-relief ribs pinch the cable |
| `exit_bottom`, `exit_left`, `exit_right`, `exit_back` | 1, 0, 0, 0 | Cable exit toggles (see above) |
| `case_back_z`, `case_front_z`, `case_outer_half_w` | 9.9, 11.4, 29.75 mm | Derived; don't edit |

### Printing

`enclosure/presence-enclosure.3mf` is an OrcaSlicer project with both parts in print orientation: the base on its back, the cover radome-down. Neither needs supports (the keyhole pocket roofs and the bottom exit opening are short bridges; the edge chamfers are 45°). The embedded settings:

| Setting | Value |
|---------|-------|
| Printer profile | Bambu Lab A1 0.4 nozzle (any 0.4 mm printer works; switch it in the slicer and keep the process) |
| Material | PLA (Generic PLA). PETG also works; check radar range through the radome |
| Layer height | 0.2 mm (first layer 0.2 mm) |
| Walls | 3 |
| Top / bottom layers | 5 / 4 |
| Infill | 20 % gyroid |
| Supports | Off |
| Brim | Off |

`enclosure/presence-enclosure.step` holds both parts assembled (cover closed) for anyone who wants to modify them.

### Assembly

1. Press M2.5 heat-set inserts into the four bosses.
2. Stick the antenna into its pocket, run the cable down around the guide post and back up to the XIAO's U.FL.
3. Screw the PCB onto the inserts, plug in the cable and route it out of the enabled exit.
4. Press the cover on.
