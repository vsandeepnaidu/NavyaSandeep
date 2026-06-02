#!/usr/bin/env python3
"""Compute the 'since you were born' facts for the finale, pinned to the
33rd birthday (00:35 IST, 4 Jun 2026). Every figure here is derived from a
measured physical constant so the page can claim 'science verified'.

Sources for the constants used (all standard / peer-reviewed):
  Earth mean orbital speed ........ 29.78 km/s        (NASA Earth fact sheet)
  Sun's galactocentric speed ...... 230 km/s          (IAU / Gaia, ~220-235)
  Solar apex motion (-> Hercules) . 19.5 km/s         (Sun's peculiar velocity)
  Andromeda<->Milky Way approach .. 110 km/s          (van der Marel et al. 2012)
  Moon recession rate ............. 3.8 cm/yr         (lunar laser ranging)
  speed of light .................. 299792.458 km/s   (exact, SI)
  light-year ...................... 9.4607e12 km
  resting heart rate (adult) ...... 72 beats/min      (typical)
  resting breathing rate .......... 14 breaths/min    (typical 12-16)
"""
from datetime import datetime, timezone

birth  = datetime(1993, 6, 3, 19, 5, 0, tzinfo=timezone.utc)   # 00:35 IST 4 Jun 1993
target = datetime(2026, 6, 3, 19, 5, 0, tzinfo=timezone.utc)   # 33rd birthday

seconds = (target - birth).total_seconds()
days    = seconds / 86400.0
years   = days / 365.25

def bn(km):   # billions of km
    return km / 1e9

print(f"interval: {days:.0f} days = {years:.4f} Julian years = {seconds:,.0f} s\n")

galaxy_km = 230.0 * seconds
apex_km   = 19.5  * seconds
androm_km = 110.0 * seconds
earth_km  = 29.78 * seconds
light_ly  = years                       # light travels 1 ly per year
moon_m    = (3.8 * years) / 100.0        # cm -> m
sunrises  = round(days)
heartbeat = 72.0 * seconds / 60.0
breaths   = 14.0 * seconds / 60.0

print(f"Milky Way ride ........ {bn(galaxy_km):7.1f} billion km   (230 km/s)")
print(f"toward Hercules ....... {bn(apex_km):7.1f} billion km   (19.5 km/s)")
print(f"Andromeda closer ...... {bn(androm_km):7.1f} billion km   (110 km/s)")
print(f"Earth around the Sun .. {bn(earth_km):7.1f} billion km   (29.78 km/s)")
print(f"light bubble radius ... {light_ly:7.2f} light-years")
print(f"Moon receded .......... {moon_m:7.3f} m              (3.8 cm/yr)")
print(f"sunrises (= days) ..... {sunrises:,}")
print(f"heartbeats ............ {heartbeat/1e9:7.3f} billion        (72 bpm)")
print(f"breaths ............... {breaths/1e6:7.1f} million        (14 /min)")
