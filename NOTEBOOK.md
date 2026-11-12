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

**Day (home PC, Fable, nobody in the headset): the game runs in the OpenXR Simulator; all eight rungs desk-checked WITH the VR mod.**

- **TTWVR takes the OpenXR Simulator as its headset.** It has two ways to the headset (OpenXR first, OpenVR as the
  fallback) and reads `XR_RUNTIME_JSON`; pointed at the simulator's 32-bit manifest for the one start, its log says
  `VR backend: OpenXR`, runtime `OpenXR Simulator Runtime`, `Head tracking active`. `[verified-live 2026-11-10, n=12]`
- **Nobody presses Continue:** our own MO2 mod `Bridge desk test - continue on start` (one small settings file for
  Stewie's Tweaks, read through its multi-file support): `bAutoContinueGame`, `bNoAltTabPause`, `bNoPipboyOnAltTab`.
  Only the `<rung> sim` profiles have it on; the rung profiles Tefa plays are untouched. The flat base with it goes
  straight into the save with the HUD up. `[verified-live 2026-11-10, n=1]`
- **The robot hands work:** with the VR Bench layer on (32-bit), Y opens the game's pause menu and B closes it; on the
  main menu A presses the highlighted Continue; the mod's two small hand panels follow the hand positions set.
  `[verified-live 2026-11-10, n=10]`
- **What does NOT work in the simulator: the 3D world never refreshes.** After the save loads the picture is the frame
  the save was made on (auto-load) or black (Continue pressed by hand); head turns, the walk stick, the turn stick, a
  raised hand, the height-calibration pose all change nothing (picture difference exactly 0.0), while the menus draw
  and follow the head. Not the cause: the window not being in front, the pause-on-lost-focus, the upscaler (off), the
  eye size (50%), the auto-load (Continue by hand does the same). The one difference in the mod's log against last
  night's headset run: the line `[camtrack] no body tracking and no Virtual Desktop body: the body is solved from the
  headset and the controllers` never appears in the simulator. `[hypothesis]`: the mod's body solve waits for
  something the simulator does not give, and the world view hangs on it. Its hidden switches (`bDiagnostics` ...) are
  not read from `TTWVR.ini`.
- **`tools/rung_simcheck.py`**: one rung, one command: makes `<rung> sim`, starts it in the simulator, waits for the
  save, presses pause and back, turns the head, closes politely, keeps the logs. All eight:

  | Rung | Started | Save loaded | Pause menu answers | New crash logs | New complaints in the mod's log |
  | --- | --- | --- | --- | --- | --- |
  | 01 vr base | yes | yes | yes | 0 | none |
  | 02 fixes | yes | yes | yes | 0 | none |
  | 03 world | yes | yes | yes | 0 | none |
  | 04 gameplay | yes | yes | yes | 0 | none (one long-load warning) |
  | 05 interface | yes | yes | yes | 0 | none |
  | 06 armor and people | yes | yes | yes | 0 | none |
  | 07 weapons | yes | yes | yes | 0 | none |
  | 08 animations and the rest | yes | yes | yes | 0 | `[camera] Camera1st's parents are not Bip01 Looking / NonAccum / Bip01 in this skeleton: only Camera1st itself` |

  `[verified-live 2026-11-10, n=1 each]`. What this says: with the VR mod on top, every rung starts, loads a save made
  on rung 1 and keeps running for a minute. What it does not say: anything a player would see (the world is not drawn
  in the simulator), so the headset ladder still stands.
- **Rung 8's complaint has one source `[inferred-static]`:** of the mods on at rung 8, only `NVCS Vanilla Weights`
  supplies `meshes/characters/_1stperson/skeleton.nif`, it is new at rung 8, and TTWVR ships no first-person skeleton
  of its own (only `characters/_male`). The first thing to split when rung 8 is worn.
- Housekeeping: the saves are byte-identical to the copy taken before (`Saves.bak-2026-11-10-before-sim` beside
  them); MO2 opens on `rung-02 fixes` again; the VR Bench layer is switched off. The game ignored a polite close
  twice while two copies ran (my own doing: started the next before the last had gone); no forced close was needed.
- Tool faults met: the VR Bench tool's own picture command returns nothing with this simulator version (the
  simulator's own screenshot works); the flat checker lists the simulator's window as a "box" (harmless).

**2026-11-11 evening (Developer PC, Fable, no game running): the hunt for the missing 3D world in the simulator.**

- Not solved, narrowed. The simulator does give a valid head reading and a play space (our own probe, `[measured]`),
  and its surviving per-frame record shows the mod handing over fresh eye pictures every frame: so it is not the body
  solve waiting on the headset, and not refused frames. The `[camtrack]` line is only the solver's first success;
  with `[aim]` missing too, the mod's in-world part seems never to start `[hypothesis]`.
- `collect_run.py` now keeps the simulator's own log on every ` sim` run: that log names any refused call and every
  session state, and it was gone a day later. One desk run of rung 1 answers it.
- Full note: `modding-notes/2026-11-11-why-no-3d-world-in-the-simulator.md`.
- **Later, two desk runs of rung 1 (Tefa's yes).** The simulator's kept log: no call refused, session FOCUSED
  throughout; "the headset's session is gone" is our own polite close reaching the simulator's window. Full Body is on
  (read from memory). The mod's pictures follow the head but are black. **Suspect:** Virtual Desktop's body memory
  exists here, empty, whenever its Streamer runs, and the mod skips its own body solver when that memory is there
  `[measured]` + `[inferred-static]`; the link to the black world is `[hypothesis]`. Decider: quit the Streamer, run
  rung 1 again. `collect_run.py` also no longer stops on a file the game still holds.
- **The decider (Streamer quit by Tefa).** The `[camtrack]` lines appear: with the Virtual Desktop Streamer running
  and nobody in the headset, TTWVR has no body (it trusts the empty memory). `[verified-live 2026-11-11]` But the
  world is still black with the body solved: one fault found, not the fault. Left: the picture path (the two big eye
  pictures, the 4096 cap, the upscaler helper). The 2026-11-10 "upscaler off / small eye: no change" was measured with
  the dead body and has to be done again.
- **Three more desk runs (Streamer off).** Ruled out with the body solved: the upscaler and the 4096 cap, the game's
  window being covered, the auto-load, see-through pixels. **The clue:** with the pause menu open the mod shows the
  game's own picture on a panel and the world is in it, so the game draws and the picture reaches the headset; only
  the mod's two stereo eye pictures stay exactly empty while playing. Next: what its eye capture waits for, and its
  lens numbers.
- **Late: the reader, the eye hand-over, the upscaler-off run.** The mod's stereo step is fully on (read live with
  `tools/ttwvr_gates.py`). The world does reach the simulator: every pause and un-pause writes one fresh, correct,
  head-tracked stereo picture, and then it stays frozen. Not the upscaler's helper, not the window, not the body.
  Missing is only the refresh on ordinary frames (the mod's deferred eye copy is the suspect). A desk run can already
  take head-tracked stills on demand. Everything in `modding-notes/2026-11-11-why-no-3d-world-in-the-simulator.md`.

## 2026-11-12

**Morning (Developer PC, Fable, nobody in the headset, the Virtual Desktop Streamer running): a LIVE picture in the simulator.**

- The Streamer could not be quit from a session (admin rights). Our own desk add-on `desk-shim/bridge_desk.dll`
  (an xNVSE plugin in our desk-test MO2 mod, never in a played profile) now answers TTWVR's question about Virtual
  Desktop's body memory with "not there" inside the game: body solved with the Streamer up.
  `[verified-live 2026-11-12, n=8 starts]`
- **The frozen eye, found:** with DLSS on, TTWVR's helper program draws each finished eye straight into the
  headset's own picture, through an old-style shared handle. The simulator's pictures are plain, the handle call
  fails, and the mod silently copies the previous headset picture forward, every frame, with every counter healthy
  and no log line. Found with a Direct3D 11 probe of our own (`desk-shim/d3d11_probe.cpp`) and the reader's reading
  of the DLL. `[verified-live]` + `[inferred-static]`
- **Worked around from our side:** the add-on has the simulator's swapchain pictures made with the old sharing flag.
  The eye is live, head-tracked and upscaled at Tefa's own settings (165%, DLSS Performance).
  `[verified-live 2026-11-12, n=3 starts]`
- Ruled out live: the simulator's preview window, the game's window in front, the 4096 cap, a stalled Direct3D
  queue, the headset's draw flag.
- `tools/rung_simcheck.py` judges a live eye now (no pause trick) and no longer needs the Streamer quit.
- Full note: `modding-notes/2026-11-12-live-picture-in-the-simulator.md`.

