"""Turn the KiCad BOM and position file into JLCPCB assembly files.

Only parts with an LCSC number that are not DNP go to the assembly files; the
XIAO (no LCSC part) is hand-soldered and the DNP parts are optional.
JLCPCB may still need rotation fixes for some parts: check their placement
preview before ordering.
"""
import csv, sys

# Degrees added to KiCad's rotation where JLCPCB's model of the LCSC part has a
# different zero orientation than our footprint. Keyed by footprint name.
# LD2460 J1 (C2906072): our footprint has the 2x4 long axis along Y; JLCPCB's
# model has it along X. The socket is symmetric under 180 degrees, so +90 and
# -90 place it the same way.
JLCPCB_ROTATION = {
    "LD2460_J1_Socket_2x04_P2.00mm": 90,
}

bom_in, pos_in, out = sys.argv[1:4]
assembled = {}
rows = []
with open(bom_in, newline="") as f:
    for r in csv.DictReader(f):
        if r["DNP"] or not r["LCSC Part #"]:
            continue
        refs = r["Designator"].split(",")
        for ref in refs:
            assembled[ref] = r
        rows.append([r["Value"], ",".join(refs), r["Footprint"].split(":")[-1], r["LCSC Part #"]])
with open(f"{out}/presence-pcb-bom-jlcpcb.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    w.writerows(rows)
with open(pos_in, newline="") as f, open(f"{out}/presence-pcb-cpl-jlcpcb.csv", "w", newline="") as g:
    w = csv.writer(g)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in csv.DictReader(f):
        if r["Ref"] in assembled:
            rot = r["Rot"]
            offset = JLCPCB_ROTATION.get(assembled[r["Ref"]]["Footprint"].split(":")[-1])
            if offset:
                rot = f"{(float(rot) + offset) % 360:.6f}"
            w.writerow([r["Ref"], r["PosX"] + "mm", r["PosY"] + "mm",
                        "Top" if r["Side"] == "top" else "Bottom", rot])
