import json, collections, sys
d = json.load(open(sys.argv[1]))
for k in ("violations", "unconnected_items", "schematic_parity"):
    v = d.get(k, [])
    print(k, len(v), dict(collections.Counter((x["type"], x["severity"]) for x in v)))
    for x in v:
        if x["type"] not in ("text_height",) and (len(sys.argv) < 3 or x["type"] == sys.argv[2]):
            print("  ", x["type"], "|", x["description"], "|", [ (i["description"], i["pos"]) for i in x["items"]])
