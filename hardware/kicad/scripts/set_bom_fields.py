"""Set MPN/LCSC fields and DNP / BOM flags on the schematic symbols (idempotent)."""
import re, sys

SCH = sys.argv[1]
PARTS = {  # ref: (MPN, Manufacturer, LCSC, dnp, in_bom)
    "U1": ("XIAO ESP32S3", "Seeed Studio", "", False, True),
    "J1": ("PM200-2-04-Z-4.3", "HCTL", "C2906072", False, True),
    "J2": ("PM200-2-02-Z-4.3", "HCTL", "C2906070", False, True),
    "FB1": ("BLM21PG221SN1D", "Murata", "C85840", False, True),
    "C1": ("CL21A226MAQNNNE", "Samsung", "C45783", False, True),
    "C2": ("CC0805KRX7R9BB104", "Yageo", "C49678", False, True),
    "C3": ("CL21A106KAYNNNE", "Samsung", "C15850", False, True),
    "C4": ("CL21A106KAYNNNE", "Samsung", "C15850", False, True),
    "C5": ("CL21A226MAQNNNE", "Samsung", "C45783", False, True),
    "U2": ("AP2112K-3.3TRG1", "Diodes Inc.", "C51118", False, True),
    "J3": ("SM04B-SRSS-TB(LF)(SN)", "JST", "C160404", False, True),
    "D1": ("SS34", "MDD", "C8678", False, True),
    "R1": ("0805W8F4701T5E", "UNI-ROYAL", "C17673", True, True),
    "R2": ("0805W8F4701T5E", "UNI-ROYAL", "C17673", True, True),
    "J4": ("1x4 2.54 mm pin header", "", "", True, True),
    "J5": ("1x2 2.54 mm pin header or 2-pin 2.54 mm screw terminal", "", "", True, True),
}
for i in range(1, 9):
    PARTS[f"TP{i}"] = ("", "", "", False, False)
for i in range(1, 5):
    PARTS[f"H{i}"] = ("", "", "", False, False)

text = open(SCH).read()
out, pos = [], 0
for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "[^"]+"\)', text):
    start = m.start()
    # find block end: next "\n\t)" at depth 1
    end = text.index("\n\t)\n", start) + 3
    block = text[start:end]
    ref = re.search(r'\(property "Reference" "([^"]+)"', block).group(1)
    if ref in PARTS:
        mpn, mfr, lcsc, dnp, in_bom = PARTS[ref]
        block = re.sub(r"\(dnp (yes|no)\)", f"(dnp {'yes' if dnp else 'no'})", block, count=1)
        block = re.sub(r"\(in_bom (yes|no)\)", f"(in_bom {'yes' if in_bom else 'no'})", block, count=1)
        block = re.sub(r'\n\t\t\(property "(MPN|Manufacturer|LCSC)" "[^"]*"\n.*?\n\t\t\)', "", block, flags=re.S)
        at = re.search(r'\(at ([\d.\-]+) ([\d.\-]+)', block)
        props = ""
        for k, v in (("MPN", mpn), ("Manufacturer", mfr), ("LCSC", lcsc)):
            if v:
                props += (f'\n\t\t(property "{k}" "{v}"\n\t\t\t(at {at.group(1)} {at.group(2)} 0)\n'
                          f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)')
        i = block.index('\n\t\t(property "Footprint"')
        block = block[:i] + props + block[i:]
    out.append(text[pos:start]); out.append(block); pos = end
out.append(text[pos:])
open(SCH, "w").write("".join(out))
print("ok")
