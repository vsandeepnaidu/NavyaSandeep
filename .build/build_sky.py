#!/usr/bin/env python3
"""Process raw d3-celestial data into a compact sky payload and (optionally)
inject it into index.template.html to produce a self-contained index.html."""
import json
import os

SRC = os.path.dirname(os.path.abspath(__file__))          # .build/
ROOT = os.path.dirname(SRC)                               # project root


def load(name):
    with open(os.path.join(SRC, name)) as f:
        return json.load(f)


def ra360(lon):
    return round(lon + 360 if lon < 0 else lon, 3)


stars = load("stars.6.json")["features"]
lines = load("constellations.lines.json")["features"]
names = load("starnames.json")

MAGLIM = 5.5

# Stars: [ra(0-360), dec, mag]
star_out = []
hipmap = {}
for f in stars:
    lon, lat = f["geometry"]["coordinates"]
    mag = f["properties"]["mag"]
    hipmap[f["id"]] = (lon, lat, mag)
    if mag <= MAGLIM:
        star_out.append([ra360(lon), round(lat, 3), round(mag, 2)])

# Constellation lines: list per constellation of polyline paths of [ra, dec]
line_out = []
for f in lines:
    paths = []
    for path in f["geometry"]["coordinates"]:
        paths.append([[ra360(p[0]), round(p[1], 3)] for p in path])
    line_out.append(paths)

# Labels: famously bright named stars only -> [ra, dec, name, mag]
label_out = []
for hip, info in names.items():
    nm = (info.get("name") or "").strip()
    if not nm:
        continue
    try:
        h = int(hip)
    except ValueError:
        continue
    if h not in hipmap:
        continue
    lon, lat, mag = hipmap[h]
    if mag > 2.6:
        continue
    label_out.append([ra360(lon), round(lat, 3), nm, round(mag, 2)])
label_out.sort(key=lambda x: x[3])

sky = {"stars": star_out, "lines": line_out, "labels": label_out}
payload = json.dumps(sky, separators=(",", ":"), ensure_ascii=False)

with open(os.path.join(SRC, "skydata.json"), "w") as f:
    f.write(payload)

print(f"stars={len(star_out)} constellations={len(line_out)} "
      f"labels={len(label_out)} bytes={len(payload)}")

tpl = os.path.join(SRC, "index.template.html")
if os.path.exists(tpl):
    with open(tpl) as f:
        html = f.read()
    html = html.replace("__SKYDATA__", payload)

    # three.min.js and renders/*.jpg are shipped as separate files (the page
    # is hosted on GitHub Pages), so only the star data is inlined here.
    out = os.path.join(ROOT, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"wrote {out} ({len(html)} bytes)")
else:
    print("(no template yet; wrote skydata.json only)")
