#!/usr/bin/env bash
# Copy the day or night versions of the farm and the cat divider into place based on
# the UTC hour (day 06:00-17:59 UTC). Set HOUR to override, e.g. HOUR=20 for testing.
set -euo pipefail
hour=$((10#${HOUR:-$(date -u +%H)}))
if (( hour >= 6 && hour < 18 )); then scene=day; else scene=night; fi
for name in hero cat; do
  cp "assets/$name-$scene.svg" "assets/$name.svg"
done
echo "$scene"
