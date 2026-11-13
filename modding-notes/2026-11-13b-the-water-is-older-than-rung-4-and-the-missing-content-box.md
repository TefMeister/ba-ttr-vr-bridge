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

## 3. Flat against VR at the same water: it is the VR drawing (later the same evening)

- `rung_flatcheck.py --save "Save 4"` (new: a `<rung> desk` copy of the flat profile with our flat desk mod
  `Bridge desk test - continue on start (flat)`, only the Stewie auto-continue INI, kept in `desk-flat-mod/`; the saves
  put back after). Rung 4 flat opens the save clean and loads in 13 s.
- `[verified-live 2026-11-13, flat, n=1]` (`runs/2026-11-13 1923 rung-04 gameplay flat desk/`): the same spot draws a
  grey-blue lake, well below the rock, with banks and reflections, ONE colour. VR rung 4 and rung 3 (simulator): a flat
  olive-green sheet starting right behind the rocks. **The water fault is TTWVR's drawing, not a Begin Again mod**
  `[verified-live, n=1 each]`. Where in TTWVR (its forced graphics preset turning water reflections / refraction off, the
  near and far water drawn differently, the water's depth in stereo) is the next question: `MODEL: FABLE`.
- The flat box (rung 3 flat): the scancode Enter that answered it in VR did NOT answer it flat (four presses, the box stayed;
  picture `runs/2026-11-13 1919 rung-03 world flat desk/`). A save that needs no box (`save_needs.py`) avoids it; a mouse click
  on Yes is the next thing to try if a flat box must be answered.

## 4. Kupo's "posing tool" (Tefa: "i think Kupo already provides some sort of a posing tool")

What TTWVR 1.0.0 has, read from its plugin and Kupo's control text `[inferred-static]`:
- The hand grips are authored TEXT TABLES packed in `NVSE/Plugins/TTWVR/TTWVR.dat` (a "TVPK" pack): `grips-pose.txt`,
  `pistol-zones.txt`, `melee-fingers.txt`, `melee-lowgrip.txt`, `handling.txt`, `reload-anim.txt`, `hand-skin.txt`,
  `blades.txt`, `scopes.txt`, `casing.txt` (log lines "[pose] no authored grip table at ...", "[grip] no pistol zones at ...").
  No in-game pose editor was found in the strings.
- In-game adjustments the player makes and the mod keeps: "Adjust Spare Pouch Position = Hold Left Grip or Right Grip for
  3 seconds, then move and release" (Kupo's controls); the plugin also keeps `SavedMagazineHolds`, `SavedPouch`,
  `SavedWristBoy`, `SavedScopeZoom` (where they are written was not found: not in TTWVR.ini, perhaps in the save).
  **Likely the cause of Tefa's "the ammo holster spot moved to my right" on rung 4** `[hypothesis]`: a grip held 3 s
  near the pouch drags it.
- An outside command file `NVVR-cmd.txt` is read by the plugin (its use not worked out).

## 5. Rung 8c at the same spot, and the water pinned down (Tefa: "carry on with opus ... see the wasteland in all it's glory")

- Rung 8c `[verified-live 2026-11-13, simulator + flat, n=1 each]` (`runs/2026-11-13 1945 rung-08c optional mods sim/`,
  `... flat desk/`): Tefa's save opens clean (32 s VR, 16 s flat); the city skyline and the far buildings are there in VR as
  in the flat picture (at the stills' resolution). The water is the same green sheet in VR.
- TTWVR's forced preset, read from its plugin `[inferred-static]`: `bUseWaterReflections` off, `iWaterReflectWidth/Height`
  low, `bUseWaterDisplacements` off, `bUseWaterDepth` off ("Depth Fog: off - fps144 T2"), `bUseWaterRefractions` on.
  `SetNumericINISetting "bUseWaterDepth:Water" 1` typed live changed nothing visible (`[measured]`, n=1; may need a load).
- **The sheet IS water and it is drawn over the land in front of it** `[verified-live, simulator, n=1]`: console `tws`
  (water off) made it vanish, and under it lies the real lake bed, lower down, where the flat picture has the lake. So in
  VR the (far) water is not hidden by the nearer ground: a depth / draw-order matter in TTWVR's drawing (it has its own
  depth switches `bSolidDepth`, `iSolidDepthAt`, `bFirstPersonOwnDepth` in the built-in table, not reachable from the INI).
  `[hypothesis]`: the far (LOD) water is drawn in a pass whose depth does not hold the near terrain. Next: `MODEL: FABLE`.
- `console_type.py` now types ":" and "_" (it had no key for them). `rung_flatcheck.py --save` now puts MO2's profile
  back (it had left MO2 on the "desk" copy; put back to `rung-04 gameplay` by hand this time).
