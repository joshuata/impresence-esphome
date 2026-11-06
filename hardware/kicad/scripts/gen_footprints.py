"""Generate the project footprints in presence.pretty.

Pad positions come from presence-skeleton (Fusion) and the LD2460 manual
(Fig. 1 dimensions, Fig. 3 pin numbering), see hardware/README.md.
KiCad footprint coordinates: x right, y down, mm.
"""
import os, uuid

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "presence.pretty")


def u():
    return str(uuid.uuid4())


def fp_line(x1, y1, x2, y2, layer, w):
    return f'  (fp_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{u()}"))\n'


def rect(x1, y1, x2, y2, layer, w):
    return (fp_line(x1, y1, x2, y1, layer, w) + fp_line(x2, y1, x2, y2, layer, w)
            + fp_line(x2, y2, x1, y2, layer, w) + fp_line(x1, y2, x1, y1, layer, w))


def fp_text(kind, text, x, y, layer, hide=False, size=1.0):
    h = " (hide yes)" if hide else ""
    return (f'  (property "{kind}" "{text}" (at {x:.4f} {y:.4f} 0) (layer "{layer}"){h} (uuid "{u()}")\n'
            f'    (effects (font (size {size} {size}) (thickness {size*0.15:.3f}))))\n')


def silk_text(text, x, y, size=0.8, layer="F.SilkS"):
    return (f'  (fp_text user "{text}" (at {x:.4f} {y:.4f} 0) (layer "{layer}") (uuid "{u()}")\n'
            f'    (effects (font (size {size} {size}) (thickness {size*0.15:.3f}))))\n')


def tht(num, x, y, w, h, drill, shape="oval", offset=None):
    off = f" (offset {offset[0]:.4f} {offset[1]:.4f})" if offset else ""
    return (f'  (pad "{num}" thru_hole {shape} (at {x:.4f} {y:.4f}) (size {w} {h}) (drill {drill}{off}) '
            f'(layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{u()}"))\n')


def footprint(name, descr, body, ref_y, val_y):
    return (f'(footprint "{name}" (version 20241229) (generator "presence-gen_footprints")\n'
            f'  (layer "F.Cu")\n  (descr "{descr}")\n  (attr through_hole)\n'
            + fp_text("Reference", "REF**", 0, ref_y, "F.Fab")
            + fp_text("Value", name, 0, val_y, "F.Fab")
            + body + ')\n')


def write(name, text):
    with open(os.path.join(OUT, name + ".kicad_mod"), "w") as f:
        f.write(text)


# --- XIAO ESP32-S3, edge pins only, USB toward -y (top) ----------------------
# Board 17.78 x 20.955 (xiao_width/xiao_length). Pin rows 15.24 apart, pitch 2.54.
# Pin 1 (D0) is 2.921 mm from the USB end; the far end pin is 2.794 mm from the
# other edge (xiao_pin1_offset). Pins 1-7 left (D0..D6), 8-14 right (D7..5V,
# 14 at the USB end). Source: Seeed XIAO ESP32S3 schematic v1.4 (header J9) and
# the xiao-esp32s3 Fusion model.
W, L = 17.78, 20.955
y0 = -L / 2 + 2.921
body = ""
for i in range(7):
    y = y0 + 2.54 * i
    body += tht(str(i + 1), -7.62, y, 2.6, 1.6, 1.0, "rect" if i == 0 else "oval", (-0.5, 0))
    body += tht(str(14 - i), 7.62, y, 2.6, 1.6, 1.0, "oval", (0.5, 0))
names_l = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
names_r = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
for i in range(7):
    y = y0 + 2.54 * i
    body += silk_text(names_l[i], -4.9, y, 0.8)
    body += silk_text(names_r[i], 4.9, y, 0.8)
body += rect(-W / 2, -L / 2, W / 2, L / 2, "F.Fab", 0.1)
body += rect(-4.48, -L / 2 - 1.537, 4.48, -L / 2 - 1.537 + 7.32, "F.Fab", 0.1)  # USB-C
body += rect(-W / 2 - 0.25 - 1.1, -L / 2 - 1.537 - 0.25, W / 2 + 0.25 + 1.1, L / 2 + 0.25, "F.CrtYd", 0.05)
sx, sy = W / 2 + 0.12, L / 2 + 0.12
# The pads reach the board edges, so only the far end is drawn.
body += fp_line(-sx, sy, sx, sy, "F.SilkS", 0.12)
write("XIAO_ESP32S3_EdgePins", footprint(
    "XIAO_ESP32S3_EdgePins",
    "Seeed XIAO ESP32-S3, 14 edge pins only (C6-compatible). Pads fit pin headers or flush castellation soldering",
    body, -L / 2 - 3, L / 2 + 1.5))


# --- LD2460 sockets: 2.0 mm female, pads numbered with LD2460 pin numbers ----
# Coordinates from presence-skeleton (radar centre = 0,0, y up), converted to
# footprint coords relative to the header centre (y down). Pin numbering from
# LD2460 manual V1.1 Fig. 3, mirrored because the PCB faces the module's
# component side.
def socket(name, pins, centre, cols, descr):
    cx, cy = centre
    b = ""
    for num, (x, y) in pins.items():
        b += tht(str(num), x - cx, -(y - cy), 1.35, 1.35, 0.8,
                 "rect" if num == min(pins) else "circle")
    hx, hy = 2.0, cols  # half body: 2 rows x 2.0 = 4.0 wide, cols x 2.0 long
    b += rect(-hx, -hy, hx, hy, "F.Fab", 0.1)
    b += rect(-hx - 0.12, -hy - 0.12, hx + 0.12, hy + 0.12, "F.SilkS", 0.12)
    b += rect(-hx - 0.5, -hy - 0.5, hx + 0.5, hy + 0.5, "F.CrtYd", 0.05)
    return footprint(name, descr, b, -hy - 1.5, hy + 1.5)


j1 = {5: (19.75, -3.78), 6: (19.75, -1.78), 7: (19.75, 0.22), 8: (19.75, 2.22),
      9: (21.75, 2.22), 10: (21.75, 0.22), 11: (21.75, -1.78), 12: (21.75, -3.78)}
jp = {1: (-21.75, -2.31), 2: (-21.75, -0.31), 3: (-19.75, -0.31), 4: (-19.75, -2.31)}
write("LD2460_J1_Socket_2x04_P2.00mm", socket(
    "LD2460_J1_Socket_2x04_P2.00mm", j1, (20.75, -0.78), 4.0,
    "2x4 2.0 mm female socket for HLK-LD2460 J1; pads numbered 5-12 as on the module"))
write("LD2460_JP103_Socket_2x02_P2.00mm", socket(
    "LD2460_JP103_Socket_2x02_P2.00mm", jp, (-20.75, -1.31), 2.0,
    "2x2 2.0 mm female socket for HLK-LD2460 JP103; pads numbered 1-4 as on the module"))
print("ok")
