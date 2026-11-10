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

**First runs (evening, Tefa at the PC).**

- Rung 0 as built (TTW + TTWVR's five requirements) failed three ways: Stewie's Tweaks disabled without its INI, then
  a crash loading (`ttw_nvse.dll` missing, from `ROOGNVSE Plugin`), then TTW's own self-check (ShowOff, JohnnyGuitar,
  `falloutcustom.ini`) with a new game dropped in the Mojave. TTWVR's guide lists less than TTW 3.4 needs. `[measured]`
- **Rung 0b `rung-00b debug base` = the list author's Debug Mode profile** (its 28 mods, its `falloutcustom.ini`,
  windowed; rung 0's `fallout.ini` / `falloutprefs.ini`, since the author's opened the launcher). 20 NVSE plugins
  loaded, no TTW boxes, a new game asks Capital Wasteland or Mojave (Tefa). PASS `[verified-live 2026-11-09, n=1]`
- MO2 unticked the three GECK mods in rung 0b on its own (editor only, no effect on the game).
- **Rung 1 `rung-01 vr base` = rung 0b + TTWVR 1.0.0 at the top (wins every clash). PASS in the headset**
  (Quest 3, Virtual Desktop): Tefa: *"this mod is just insanely well done, it's like playing the game just within
  it ... i don't think i encountered anything that is wrong right now, it just plays with the usual Bethesda jank"*.
  TTWVR's DLSS and voice helpers start beside the game. `[verified-live 2026-11-09, n=1]`
- The game reads its own cursor: a Menu-o-matiC click does nothing, Down moves the menu highlight, Enter / E sent the
  same way do not select (control profile `routes/tale-of-two-wastelands/KNOWN.md`).
- The Lanes collector skipped runs 1-4 (the project had no game set); set to Steam 22380 during run 4.
  `tools/collect_run.py` kept all of them (two bugs fixed in it: `shutil` not imported, seconds in `--since`).
- Next: rung 2, Begin Again's groups back one at a time on top of rung 1, weapons and animations last.

## 2026-11-10

**The night after the first VR play: the rest of the ladder built and desk-checked (nobody in the headset).**

- `tools/ladder_groups.py`: rungs 2 to 8 from the author's own groups, each as a VR profile (TTWVR on top) and a
  flat twin; plan and table in `docs/rungs-02-to-08-plan.md`. No mod had to be held back for a missing master.
- The first rung 2 stopped on a box, "NVTF.ini not found": the settings files are in `Begin Again Configs`, which
  the author files in a late group. The floor of every rung is now rung 1's own mod set. `[measured]`
- `tools/ladder.py check` now says before a launch what the game said after it on the first evening: an xNVSE
  add-on that is on while its settings file is in a mod that is off, and the three add-ons TTW 3.4 asks for. It flags
  the original rung 0 (ShowOff, JohnnyGuitar) and the first rung 2 (three settings files). `[measured]`
- `tools/rung_flatcheck.py`: starts a flat rung through MO2, reads and answers any box by message, waits, says
  whether the game is up, how many xNVSE plugins loaded, whether a crash log appeared, saves a small picture of the
  game's own window, closes it, keeps the logs. **All seven flat twins: up after 60-110 s, no box, no plugin
  disabled, no crash log, main menu in the picture** (rung 8 shows Begin Again's own menu).
  `[verified-live 2026-11-10, n=1 each]` This says the list side loads; it says nothing about VR.
- A near miss, mine: a tool was pointed at "the window with Fallout in its title" and took the chat program open on
  the TTWVR thread; the quit keys were sent at it. Nothing was posted (checked on the thread). The checker now uses
  only windows that belong to FalloutNV.exe and sends no keys at all. Control profile KNOWN.md, Hazards.
- The main menu ignores its window's close message; a polite `taskkill /IM` (no /F) closes it.
- MO2 opens on `rung-02 fixes` now: the next headset run.
- Next: rung 2 in the headset, then up the ladder one rung per launch.


**Morning (home PC): music set to zero for every rung profile, before rung 2 in the headset.**

- `fDefaultMusicVolume=0` and `fMainMenuMusicVolume=0` added under `[Audio]` in each rung profile's own
  `falloutcustom.ini` (17 profiles; a `.bak-2026-11-10-music` copy beside each; the list's own two profiles untouched).
  Effects and voices unchanged. `[hypothesis]`: not yet heard in the game; an existing save may carry its own slider value.
