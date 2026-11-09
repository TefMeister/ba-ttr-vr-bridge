# Notebook

A tight, dated log of everything we do and what came of it. Newest at the bottom of each day. Faults go to
[FAULTS.md](FAULTS.md), in the order they must be sorted; questions only a mod's author can answer are marked there.

Claim tags: `[verified-live]` seen in the running game, `[measured]` read from files or logs, `[inferred]` reasoned,
`[reported]` someone said so.

## 2026-11-09

**Setup, no game run yet.**

- Both games installed through Steam, English, untouched (no extra files in either folder); registry paths present.
  `[measured]`
- Fallout 3's launcher crashes on an RTX 5080 (Windows: `Fallout3Launcher.exe` 1.3.1.0, `0xc0000005`). Its INIs were
  made by hand: `Fallout_default.ini` as `Fallout.ini`, `VeryHigh.ini` as `FalloutPrefs.ini`, 3440x1440. New Vegas's
  launcher worked (its Exit button ignores window messages; stopped once its INIs were written). `[measured]`
- **Begin Again V6.1.0** installed by the Wabbajack CLI (`install -m Beginagain/beginagain`, Nexus Premium): 885
  archives (874 downloaded, 30.5 GB), no errors, 23 min. 638 mods, profiles "Begin Again" and "Debug Mode (Base TTW
  and req mods)". `[measured]`
- **TTW 3.4** installed into the list's `[NoDelete] TTW 3.4` mod (the installer's output field takes only a real
  Browse click): 18 GB, all 18 master files (FalloutNV, the NV DLCs and packs, Fallout3 and its DLCs,
  TaleOfTwoWastelands, YUPTTW). The mod is ticked in both list profiles. `[measured]`
- **TTWVR 1.0.0** (KUPOkinz, DLL of 2026-11-08) downloaded, not installed. An MO2 archive: `TTWVR.dll`, its own dxvk
  d3d9, openvr_api, DLSS / FSR, `TTWVR.ini`, ~380 resized armor and clothing meshes, weapons, `characters/_male`.
  `[measured]`
- **Conflict report** (`tools/conflict_report.py`, `reports/`): 498 files both supply; 476 are Skinned Mesh
  Improvement Mod's armor. 0 inside the list's BSAs. 29 list mods touch the player skeleton / body, 39 are kNVSE
  animation sets, 39 replace weapon meshes. `[measured]`
- **The ladder** (`tools/ladder.py`): each rung is its own MO2 profile, mods switched on or off in the author's
  order, never reordered; `check` reads every active plugin's masters before a launch.
- **Rung 0 built: `rung-00 flat base`.** TTW + the five things TTWVR requires (xNVSE, the 4GB patch, JIP LN NVSE + its
  INI, lStewieAl's Tweaks, lStewieAl's Engine Optimizations) + Yvile's Crash Logger (writes a log only on a crash).
  18 plugins, all masters present and in order. The game's own INIs (as its launcher wrote them), windowed 1280x720,
  music on. MO2 opens on this profile now (`ModOrganizer.ini` backed up first). `[measured]`
- **The log collector** (`tools/collect_run.py`): after every launch, every log written since it (game, xNVSE and its
  plugins, crash logger, Root Builder, MO2, TTWVR) and the Windows error events, into `runs/`. The home folder,
  login and PC name are scrubbed out (this repo is public).
