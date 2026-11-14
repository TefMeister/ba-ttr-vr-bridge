# Bridge mods

Our own small MO2 mods for the Begin Again + TTWVR bridge, kept here as their source. Each folder is copied as it is
into `<Begin Again>\mods\` and switched on in the rung profiles (`tools/ladder_groups.py` `BRIDGE_MODS` keeps them on
in every rung, VR and flat alike). Begin Again's and TTWVR's own files are never edited.

| mod | what it does | why |
| --- | --- | --- |
| `Bridge - Stewie grabbed weight off` | one Stewie's Tweaks setting off through its `Tweaks\INIs` folder: a world object held with the grab key no longer counts toward your weight (inventory weight unchanged) | the rung-5 start crash (`modding-notes/2026-11-14-the-rung-5-crash-is-stewie-s-grabbed-weight-hook.md`) |
| `Bridge - picture test DLSS off 150` | TEST ONLY, OFF since the 2026-11-14 17:05 run (was on in `rung-05 interface` alone) (not in `ladder_groups.py`): its own `TTWVR.ini` above TTWVR's, `Resolution=150%`, `Upscaler=Off`, every other line as TTWVR's | Tefa 2026-11-14: does the smudging and the swimming far skyline go away without DLSS? Switched off again after the run unless Tefa says keep it; mod list backup `modlist.txt.bak-2026-11-14-picture-test` |
