# Rung 0: flat, TTW + TTWVR's requirements only

**Question it answers:** does Tale of Two Wastelands itself run on this PC with only what TTWVR needs? If not, the
fault is TTW or its requirements, never VR and never the list.

**Profile:** `rung-00 flat base` (built by `tools/ladder.py`, checked: 8 mods, 18 plugins, all masters present and in
order). Started from MO2 with its **Run** button (the "Begin Again" executable: `FalloutNV.exe`, the 4GB-patched one
Root Builder puts in place, which loads xNVSE).

## Before the launch

1. Restart the PC (Tefa).
2. `python tools/ladder.py check --mo2 "C:/Modlists/Begin Again" --name "rung-00 flat base"`: must say "all masters
   present and in order".
3. Note the time to the minute (the log collector keeps everything written after it).

## What we expect `[inferred]`

| Step | Expected | If not |
| --- | --- | --- |
| Launch | a 1280x720 window, Bethesda logos, the main menu within about a minute | a crash log (Yvile's) or a Windows error: TTW / requirements fault |
| xNVSE | `nvse.log` lists JIP LN, Stewie's Tweaks, Engine Optimizations and the Crash Logger as loaded | a plugin missing from the log: wrong version or not deployed |
| New game | TTW's start in Vault 101 (Fallout 3's birth scene) | a hang or crash on load: TTW install |
| Quit | Main menu > Quit, the process leaves | a crash on exit is common in this engine and noted, not a blocker |

## After the launch

`python tools/collect_run.py --mo2 "C:/Modlists/Begin Again" --game "C:/Steam/steamapps/common/Fallout New Vegas" --rung "rung-00 flat base" --since "<launch time>"`

Then: a NOTEBOOK.md line for the run, a FAULTS.md row for anything wrong, and rung 1 (the same plus TTWVR, in the
headset) only when rung 0 is clean.
