# Hardware

The Autodesk Fusion project **Presence sensor** holds the mechanical source designs; Fusion exports are kept here so they are version controlled and usable without Fusion. The main PCB is a KiCad project in this folder (see `AGENTS.md`, Hardware).

| Path | Contents |
|------|----------|
| `fusion/` | Fusion source exports (`.f3d`; `.f3z` for designs with inserted, referenced components) |
| `kicad/` | KiCad 10 project for the main PCB: schematic, board, project symbol/footprint library and build scripts |
| `pcb/` | Fabrication outputs for the main PCB: Gerber + drill zip, BOM, JLCPCB assembly files |
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

The dimensions you're likely to change are named user parameters, and most others are derived from them or from the component models. In Fusion, open `presence-skeleton` and go to **Modify → Change Parameters**. Edit the value in the *User Parameters* section, and everything that depends on it updates. Parameters ending in `_Ref` come from the component models; change those in the component design instead. The case derives from the skeleton, so changes made there flow through to it. The KiCad PCB takes its outline, holes and part positions from the same values (in `kicad/scripts/build_board.py`), so update the script and rebuild the board after changing a layout parameter.

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

## Main PCB

KiCad project `kicad/presence-pcb.kicad_pro`; two layers, 53.5 × 57.955 mm, 1.6 mm. The outline, the four M2.5 holes, the radar sockets and the XIAO position come from `presence-skeleton` (radar centre = origin, PCB front facing the room). Every part is on the front; the back carries only through-hole pins and a GND pour.

### Rebuilding

```sh
cd hardware/kicad
kicad-cli sch export netlist --format kicadsexpr -o /tmp/presence.net presence-pcb.kicad_sch
"/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3" \
  scripts/build_board.py /tmp/presence.net      # placement, routing, pours, silkscreen
scripts/export_fab.sh                           # ERC + DRC + parity, then hardware/pcb/*
```

`build_board.py` routes with its own small grid router, so the board is reproducible from the schematic without an autorouter. The custom footprints in `presence.pretty` come from `scripts/gen_footprints.py`.

### Wiring

Nets are named after XIAO pins. These match `firmware/boards/xiao-esp32s3.yaml`.

| Net | XIAO pin | Goes to |
|-----|----------|---------|
| `D8` | D8 (TX) | LD2460 J1 pin 8, Rx2 |
| `D9` | D9 (RX) | LD2460 J1 pin 7, Tx2 |
| `D4` | D4 (SDA) | Qwiic J3 pin 3, J4 pin 3 |
| `D5` | D5 (SCL) | Qwiic J3 pin 4, J4 pin 4 |
| `5V` | 5V (VBUS) | Radar filter, Qwiic LDO, hardwired input diode |
| `RADAR_5V` | – | LD2460 JP103 pin 1, after FB1 + 22 µF + 100 nF |
| `QWIIC_3V3` | – | Qwiic J3/J4 pin 2, from the AP2112K LDO U2 |
| `GND` | GND | LD2460 pins 2 and 6, Qwiic pin 1 |
| `D0` `D1` `D3` `D6` `D7` `D10` | spare | Test pads TP1–TP6 (through-hole, wire-solderable). D2 is left unconnected: GPIO3 is an S3 strapping pin |

LD2460 pin numbers follow manual V1.1, Fig. 3. The PCB faces the module's component side, so the socket footprints are mirrored relative to that photo: on the PCB, JP103 pin 1 (5 V) is the bottom pin of the column nearest the board edge, and J1 pin 5 is the bottom pin of the inner column. **Check the first board against a module before powering it.**

### Parts

`pcb/presence-pcb-bom.csv` lists every part. `pcb/presence-pcb-bom-jlcpcb.csv` and `pcb/presence-pcb-cpl-jlcpcb.csv` are for JLCPCB assembly: they include the SMD parts, the radar sockets and the Qwiic socket, and leave out the XIAO (hand-soldered) and the DNP parts. Check the part rotations in JLCPCB's placement preview before ordering.

- **XIAO (U1):** solder it flush (castellated edges onto the pads) or on pin headers. The footprint uses the 14 edge pins only; there is no copper on the front under the XIAO's bottom pads.
- **Radar sockets (J1, J2):** 2.0 mm female, 4.3 mm tall (`pcb_socket_h`). The radar plugs in with its antennas facing out.
- **Qwiic (J3):** JST SH BM04B-SRSS-TB, top entry (the cable plugs in from the front), body centre at (-22.8, -27.5) skeleton coordinates, 3.45 mm in from the left PCB edge. The header is 4.25 mm tall and the SHR-04V-S plug housing is 5 mm tall (JST SH catalogue eSH, pp. 2–3); JST gives no mated height, so measure a real cable before finalizing the cover. J4 is the same bus on 2.54 mm pads for a soldered cable or header. Both are fed 3.3 V by a dedicated AP2112K-3.3 LDO (U2), separate from the XIAO's 3V3.
- **I²C pull-ups (R1, R2, DNP):** the Adafruit breakouts have their own. Fit 4.7 kΩ only for a breakout without pull-ups.
- **Hardwired 5 V (J5, DNP):** 2-pin 2.54 mm pads at the bottom edge for bare 5 V wires, feeding VBUS through an SS34 Schottky (D1). The XIAO's 5V pin is wired straight to its USB VBUS (XIAO ESP32S3 schematic v1.4), so D1 stops USB from back-feeding the hardwired supply, but not the reverse: a hardwired supply more than about 0.3 V above USB VBUS would feed the USB host. Unplug the hardwired supply before connecting USB to a computer.
- **Antenna side:** no copper pour within 5.5 mm of the right edge, next to the antenna on the side wall.

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
