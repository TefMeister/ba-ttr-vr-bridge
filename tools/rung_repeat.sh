# rung_repeat.sh: start rungs 05 to 08c three times each on the OpenXR Simulator (rung_simcheck.py) and write one result file
# per start into $OUT; after a crashed start the hung Steam launcher helper and Mod Organizer are ended (the game is
# already gone then), so one crash cannot block the next start. Used 2026-11-14 to prove the Stewie fix (18 of 18 up).
cd ~/github-backups/ba-ttr-vr-bridge
OUT="${OUT:-$(mktemp -d)}"; echo "results in $OUT"
# 2026-11-14: hold the one-game lock for the whole series (each start is told so), give it back at the end
python tools/bridge_clash.py take || exit 1
export BRIDGE_CLASH_TAKEN=1
trap 'BRIDGE_CLASH_TAKEN= python tools/bridge_clash.py release' EXIT
VB="$HOME/github-backups/_lanes-next-wt/plugins/lanes/tools/vrbench"
for round in 1 2 3; do
  for r in "rung-05 interface" "rung-06 armor and people" "rung-07 weapons" "rung-08a skeleton and animation" "rung-08b late loaders" "rung-08c optional mods"; do
    f="$OUT/fix${round}_$(echo "$r" | cut -d' ' -f1).txt"
    echo "=== fix round $round $r $(date +%H:%M:%S)" > "$f"
    timeout 600 python tools/rung_simcheck.py --mo2 "C:\Modlists\Begin Again" --game "C:\Steam\steamapps\common\Fallout New Vegas" \
      --rung "$r" --sim "$LOCALAPPDATA\Programs\OpenXR-Simulator\openxr_simulator-32.json" --vrbench "$(cygpath -w "$VB")" >> "$f" 2>&1
    echo "exit=$? $(date +%H:%M:%S)" >> "$f"
    for i in $(seq 20); do tasklist | grep -qi "FalloutNV.exe" || break; sleep 3; done
    if ! tasklist | grep -qi "FalloutNV.exe"; then
      for i in $(seq 10); do tasklist | grep -qi "ModOrganizer.exe" || break; sleep 2; done
      if tasklist | grep -qi -E "ModOrganizer.exe|x64launcher.exe"; then
        echo "left over after the run: $(tasklist | grep -i -E 'ModOrganizer|x64launcher' | awk '{print $1}' | tr '\n' ' ')ended" >> "$f"
        taskkill //F //IM x64launcher.exe >/dev/null 2>&1; sleep 2; taskkill //F //IM ModOrganizer.exe >/dev/null 2>&1; sleep 2
      fi
    fi
  done
done
echo PROOF DONE
