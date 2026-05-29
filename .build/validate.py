#!/usr/bin/env python3
"""Validate the astronomy before porting to JS. Anchors:
- Sun must be well below the horizon at 00:35 IST (it is night).
- Moon should read ~full (4 June 1993 was a full-moon / lunar-eclipse date).
- Polaris should sit at altitude ~= latitude, azimuth ~0 (due north).
"""
import math
from datetime import datetime, timezone

RAD = math.pi / 180.0
DEG = 180.0 / math.pi


def norm360(x):
    return x % 360.0


def rev(x):
    return x % 360.0


LAT = 12.5847   # Maddur
LON = 77.0437   # east positive

birth = datetime(1993, 6, 3, 19, 5, 0, tzinfo=timezone.utc)  # 00:35 IST 4 Jun
JD = birth.timestamp() / 86400.0 + 2440587.5
d = JD - 2451543.5  # Schlyter day number


def kepler(M_deg, e):
    M = M_deg * RAD
    E = M + e * math.sin(M) * (1 + e * math.cos(M))
    for _ in range(5):
        E = E - (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    return E


def sun_pos(d):
    w = 282.9404 + 4.70935e-5 * d
    e = 0.016709 - 1.151e-9 * d
    M = rev(356.0470 + 0.9856002585 * d)
    E = kepler(M, e)
    xv = math.cos(E) - e
    yv = math.sqrt(1 - e * e) * math.sin(E)
    v = math.atan2(yv, xv) * DEG
    r = math.hypot(xv, yv)
    lon = rev(v + w)
    xs = r * math.cos(lon * RAD)
    ys = r * math.sin(lon * RAD)
    return lon, r, xs, ys, M


def obliquity(d):
    return 23.4393 - 3.563e-7 * d


def ecl_to_eq(xe, ye, ze, ecl):
    e = ecl * RAD
    xq = xe
    yq = ye * math.cos(e) - ze * math.sin(e)
    zq = ye * math.sin(e) + ze * math.cos(e)
    ra = rev(math.atan2(yq, xq) * DEG)
    dec = math.atan2(zq, math.hypot(xq, yq)) * DEG
    return ra, dec


PLANETS = {
    "Mercury": dict(N=lambda d: 48.3313 + 3.24587e-5 * d, i=lambda d: 7.0047 + 5.00e-8 * d,
                    w=lambda d: 29.1241 + 1.01444e-5 * d, a=lambda d: 0.387098,
                    e=lambda d: 0.205635 + 5.59e-10 * d, M=lambda d: 168.6562 + 4.0923344368 * d),
    "Venus":   dict(N=lambda d: 76.6799 + 2.46590e-5 * d, i=lambda d: 3.3946 + 2.75e-8 * d,
                    w=lambda d: 54.8910 + 1.38374e-5 * d, a=lambda d: 0.723330,
                    e=lambda d: 0.006773 - 1.302e-9 * d, M=lambda d: 48.0052 + 1.6021302244 * d),
    "Mars":    dict(N=lambda d: 49.5574 + 2.11081e-5 * d, i=lambda d: 1.8497 - 1.78e-8 * d,
                    w=lambda d: 286.5016 + 2.92961e-5 * d, a=lambda d: 1.523688,
                    e=lambda d: 0.093405 + 2.516e-9 * d, M=lambda d: 18.6021 + 0.5240207766 * d),
    "Jupiter": dict(N=lambda d: 100.4542 + 2.76854e-5 * d, i=lambda d: 1.3030 - 1.557e-7 * d,
                    w=lambda d: 273.8777 + 1.64505e-5 * d, a=lambda d: 5.20256,
                    e=lambda d: 0.048498 + 4.469e-9 * d, M=lambda d: 19.8950 + 0.0830853001 * d),
    "Saturn":  dict(N=lambda d: 113.6634 + 2.38980e-5 * d, i=lambda d: 2.4886 - 1.081e-7 * d,
                    w=lambda d: 339.3939 + 2.97661e-5 * d, a=lambda d: 9.55475,
                    e=lambda d: 0.055546 - 9.499e-9 * d, M=lambda d: 316.9670 + 0.0334442282 * d),
}


def planet_pos(p, d, xs, ys, ecl):
    N = rev(p["N"](d)); i = p["i"](d); w = rev(p["w"](d))
    a = p["a"](d); e = p["e"](d); M = rev(p["M"](d))
    E = kepler(M, e)
    xv = a * (math.cos(E) - e)
    yv = a * math.sqrt(1 - e * e) * math.sin(E)
    v = math.atan2(yv, xv)
    r = math.hypot(xv, yv)
    Nr, ir, wr = N * RAD, i * RAD, w * RAD
    vw = v + wr
    xh = r * (math.cos(Nr) * math.cos(vw) - math.sin(Nr) * math.sin(vw) * math.cos(ir))
    yh = r * (math.sin(Nr) * math.cos(vw) + math.cos(Nr) * math.sin(vw) * math.cos(ir))
    zh = r * (math.sin(vw) * math.sin(ir))
    xg, yg, zg = xh + xs, yh + ys, zh
    return ecl_to_eq(xg, yg, zg, ecl)


def moon_pos(d, sun_M, ecl):
    N = rev(125.1228 - 0.0529538083 * d)
    i = 5.1454
    w = rev(318.0634 + 0.1643573223 * d)
    a = 60.2666
    e = 0.054900
    M = rev(115.3654 + 13.0649929509 * d)
    E = kepler(M, e)
    xv = a * (math.cos(E) - e)
    yv = a * math.sqrt(1 - e * e) * math.sin(E)
    v = math.atan2(yv, xv)
    r = math.hypot(xv, yv)
    Nr, ir, wr = N * RAD, i * RAD, w * RAD
    vw = v + wr
    xh = r * (math.cos(Nr) * math.cos(vw) - math.sin(Nr) * math.sin(vw) * math.cos(ir))
    yh = r * (math.sin(Nr) * math.cos(vw) + math.cos(Nr) * math.sin(vw) * math.cos(ir))
    zh = r * (math.sin(vw) * math.sin(ir))
    lon = math.atan2(yh, xh) * DEG
    lat = math.atan2(zh, math.hypot(xh, yh)) * DEG
    # perturbations
    Ls = rev(282.9404 + 4.70935e-5 * d + sun_M)        # sun mean longitude
    Lm = rev(N + w + M)                                # moon mean longitude
    Ms = sun_M
    Mm = M
    Dm = rev(Lm - Ls)
    F = rev(Lm - N)
    def s(x): return math.sin(x * RAD)
    lon += (-1.274 * s(Mm - 2*Dm) + 0.658 * s(2*Dm) - 0.186 * s(Ms)
            - 0.059 * s(2*Mm - 2*Dm) - 0.057 * s(Mm - 2*Dm + Ms)
            + 0.053 * s(Mm + 2*Dm) + 0.046 * s(2*Dm - Ms)
            + 0.041 * s(Mm - Ms) - 0.035 * s(Dm) - 0.031 * s(Mm + Ms)
            - 0.015 * s(2*F - 2*Dm) + 0.011 * s(Mm - 4*Dm))
    lat += (-0.173 * s(F - 2*Dm) - 0.055 * s(Mm - F - 2*Dm)
            - 0.046 * s(Mm + F - 2*Dm) + 0.033 * s(F + 2*Dm)
            + 0.017 * s(2*Mm + F))
    xe = math.cos(lon*RAD) * math.cos(lat*RAD)
    ye = math.sin(lon*RAD) * math.cos(lat*RAD)
    ze = math.sin(lat*RAD)
    ra, dec = ecl_to_eq(xe, ye, ze, ecl)
    return ra, dec, lon


def gmst_deg(JD):
    return norm360(280.46061837 + 360.98564736629 * (JD - 2451545.0))


def altaz(ra, dec, lst, lat):
    H = (lst - ra)
    Hr, dr, pr = H*RAD, dec*RAD, lat*RAD
    sinalt = math.sin(pr)*math.sin(dr) + math.cos(pr)*math.cos(dr)*math.cos(Hr)
    alt = math.asin(max(-1, min(1, sinalt)))
    cosA = (math.sin(dr) - math.sin(pr)*sinalt) / (math.cos(pr)*math.cos(alt))
    cosA = max(-1, min(1, cosA))
    A = math.acos(cosA)
    if math.sin(Hr) > 0:
        A = 2*math.pi - A
    return alt*DEG, (A*DEG) % 360


ecl = obliquity(d)
sun_lon, sun_r, xs, ys, sun_M = sun_pos(d)
lst = norm360(gmst_deg(JD) + LON)
print(f"JD={JD:.5f}  d={d:.4f}  obliquity={ecl:.4f}  LST={lst:.3f} deg")

# Sun
sra, sdec = ecl_to_eq(xs, ys, 0.0, ecl)
salt, saz = altaz(sra, sdec, lst, LAT)
print(f"\nSUN   RA={sra:7.2f} Dec={sdec:6.2f}  alt={salt:6.2f} (expect well below 0)")

# Moon
mra, mdec, mlon = moon_pos(d, sun_M, ecl)
malt, maz = altaz(mra, mdec, lst, LAT)
elong = (mlon - sun_lon) % 360
illum = (1 - math.cos(elong*RAD)) / 2
print(f"MOON  RA={mra:7.2f} Dec={mdec:6.2f}  alt={malt:6.2f} az={maz:6.1f}  "
      f"elong={elong:6.1f}  illuminated={illum*100:5.1f}%  (expect ~full)")

# Planets
print()
for name, p in PLANETS.items():
    ra, dec = planet_pos(p, d, xs, ys, ecl)
    alt, az = altaz(ra, dec, lst, LAT)
    vis = "UP  " if alt > 0 else "down"
    print(f"{name:8s} RA={ra:7.2f} Dec={dec:6.2f}  alt={alt:6.2f} az={az:6.1f}  {vis}")

# Star sanity checks
print()
for nm, ra, dec in [("Polaris", 37.95, 89.26), ("Vega", 279.23, 38.78),
                    ("Sirius", 101.29, -16.72), ("Antares", 247.35, -26.43)]:
    alt, az = altaz(ra, dec, lst, LAT)
    print(f"{nm:8s} alt={alt:6.2f} az={az:6.1f}")

# Orbit counts (for the poetic passage)
print("\n--- orbit counts ---")
periods = dict(Mercury=87.969, Venus=224.701, Earth=365.256, Mars=686.980,
               Jupiter=4332.59, Saturn=10759.22)
now = datetime(2026, 5, 29, 12, 0, 0, tzinfo=timezone.utc)
bday = datetime(2026, 6, 3, 19, 5, 0, tzinfo=timezone.utc)  # 33rd birthday 00:35 IST
for label, when in [("now 2026-05-29", now), ("33rd bday 2026-06-04", bday)]:
    days = (when - birth).total_seconds() / 86400.0
    print(f"\n{label}: {days:.2f} days = {days/365.2425:.3f} yr")
    for pl, per in periods.items():
        print(f"   {pl:8s} {days/per:8.2f} orbits")
    print(f"   Moon orbits  {days/27.32166:8.2f}")
    print(f"   Full moons   {days/29.530589:8.2f}")
