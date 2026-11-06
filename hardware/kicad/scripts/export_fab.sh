#!/bin/sh
# Regenerate hardware/pcb/ fabrication outputs from the KiCad project.
# Usage: hardware/kicad/scripts/export_fab.sh   (needs kicad-cli 10)
set -eu
here=$(cd "$(dirname "$0")/.." && pwd)
out="$here/../pcb"
pcb="$here/presence-pcb.kicad_pcb"
sch="$here/presence-pcb.kicad_sch"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$out"

kicad-cli sch erc --exit-code-violations -o "$tmp/erc.rpt" "$sch"
kicad-cli pcb drc --refill-zones --save-board --schematic-parity --severity-all \
  --exit-code-violations -o "$tmp/drc.rpt" "$pcb"

mkdir "$tmp/gerbers"
kicad-cli pcb export gerbers --no-protel-ext --use-drill-file-origin \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts \
  -o "$tmp/gerbers" "$pcb"
kicad-cli pcb export drill --format excellon --drill-origin plot --excellon-units mm \
  --excellon-separate-th -o "$tmp/gerbers/" "$pcb"
rm -f "$out/presence-pcb-gerbers.zip"
(cd "$tmp/gerbers" && TZ=UTC zip -q -X -D "$out/presence-pcb-gerbers.zip" ./*)

# Full BOM (every part, DNP marked) and JLCPCB assembly BOM + CPL.
kicad-cli sch export bom --fields 'Reference,Value,Footprint,MPN,Manufacturer,LCSC,${QUANTITY},${DNP}' \
  --labels 'Designator,Value,Footprint,MPN,Manufacturer,LCSC Part #,Qty,DNP' \
  --group-by 'Value,MPN,Footprint,${DNP}' --ref-range-delimiter '' \
  -o "$out/presence-pcb-bom.csv" "$sch"
kicad-cli pcb export pos --format csv --units mm --side front --use-drill-file-origin \
  --exclude-dnp -o "$tmp/pos.csv" "$pcb"
python3 -I "$here/scripts/jlcpcb_files.py" "$out/presence-pcb-bom.csv" "$tmp/pos.csv" "$out"
echo "fab outputs written to $out"
