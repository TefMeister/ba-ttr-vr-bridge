# The water is older than rung 4; the "content no longer present" box known before a start (2026-11-13 evening, PC1, Opus)

Nobody in the headset; OpenXR Simulator + VR Bench; Tefa's own save from the rung-4 wear ("Save 4", 16:43, on the rock
above the water) loaded on each rung by `rung_simcheck.py --save "Save 4"` (saves put back after every run).

## 1. The water (Tefa's rung-4 points 2 and 3)

- Rung 4 `[verified-live 2026-11-13, simulator, n=1]` (`runs/2026-11-13 1902 rung-04 gameplay sim/`): the water shows as a
  flat olive-green sheet starting right behind the rocks Tefa stood on, as Tefa described.
- Rung 3 `[verified-live, n=1]` (`runs/2026-11-13 1909 rung-03 world sim/`): the same picture; mean difference of the
  straight-ahead stills 2.2 of 255 (noise). **The water is not rung 4's** (rung 4 adds gameplay mods only, as the reader
  expected).
- Rung 1 could not load this save (149 of its 167 mods off there; it stayed at the box through four Yes presses,
  `runs/2026-11-13 1914 rung-01 vr base sim/`). Rungs 1-2 need a save made on them, at the same water.
- NEXT: the same spot FLAT on `rung-03 world flat` (does the flat game draw the water the same way?). That needs
  `rung_flatcheck.py` to load a save (console `load`, the box's Yes). If flat looks right: it is the VR drawing (TTWVR's
  depth / water), `MODEL: FABLE`. If flat is the same: a rung 2-3 world mod, found by a save made on rung 2.

## 2. The "content no longer present" box (Tefa: "is there a way you can check for those, they do keep popping up")

Tefa's picture was this session's own rung-3 run waiting at the box: the five mods it names (B42Bash, VegasPlasticSurgeons,
Benny Humbles You..., CourierPatientClothing, QwibHeadBandage) are all in rung 3's missing list.

- `tools/save_needs.py` reads a save's mod list (a one-byte count, then `|` length `|` name, from FalloutNV.esm on;
  measured on Tefa's saves) and the profile's `plugins.txt` (New Vegas: every line is an active mod, no `*`), and says
  "opens clean" or which mods the box will name; `--all` gives every rung and the lowest one that opens clean. Nothing
  started, the save only read. Tefa's Save 4: clean on rung 4 and up; rung 3 35 missing, rung 2 132, rungs 0-1 149.
- `rung_simcheck.py` prints that forecast at the start and, when the box is expected, presses Enter (Yes is lit) by
  SCANCODE through SendInput into the game's own window (a plain virtual-key event did not reach the game: the first
  rung-3 run sat at the box until its time ran out). Rerun: one press, loaded after 50 s.
