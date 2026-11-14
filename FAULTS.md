# Fault ledger

In the order they must be sorted: a fault high on the list blocks the ones under it. When one is fixed it moves to
**Sorted** with the date and how. **Ask** = only that mod's author can answer it; Tefa asks them (we never fill other
people's support channels with our own problems).

## Open

| # | Fault | Blocks | Where it shows | Ask | State |
| --- | --- | --- | --- | --- | --- |
| 1 | Fallout 3's launcher crashes on the RTX 5080 (`0xc0000005`) | nothing now: its INIs were made by hand | Windows error log, 2026-11-09 | no | worked around |

## Sorted

| # | Fault | Sorted | How |
| --- | --- | --- | --- |
| 2 | Rung 0 (TTWVR's five requirements only) crashed loading: Stewie's Tweaks switched itself off without its INI | 2026-11-09 | the INI lives in Begin Again's `Begin Again Configs` mod; superseded by #4 |
| 3 | `ttw_nvse.dll is missing` (TTW 3.4's own NVSE plugin, opcode 3807, the "Gun Nut" perk script): the real cause of the first crash | 2026-11-09 | it ships in Begin Again's `ROOGNVSE Plugin` mod; superseded by #4 |
| 4 | TTW's own self-check at the main menu: ShowOff xNVSE missing (needs 1.80+), JohnnyGuitar NVSE missing (needs 5.01+), `falloutcustom.ini` misconfigured; a new game then started in the Mojave without asking | 2026-11-09 | rung 0 rebuilt as the list author's **Debug Mode (Base TTW and req mods)** profile (`rung-00b debug base`): its mods and its `falloutcustom.ini`, windowed. All 20 NVSE plugins load, no boxes, a new game asks which wasteland. Lesson: TTW needs more than TTWVR's guide lists; the author's debug profile is the real floor |
| 5 | The debug profile's own `fallout.ini` / `falloutprefs.ini` made `FalloutNV.exe` open the launcher instead of the game | 2026-11-09 | rung 0's working two INIs used instead; cause not pinned down (`[hypothesis]`: the author's prefs come from another PC) |
| 6 | The first `rung-02` left `Begin Again Configs` off (the author files it in a late group): the game stopped on "NVTF.ini not found" | 2026-11-10 | every rung's floor is rung 1's own mod set; `ladder.py check` now names a settings file whose mod is off before the launch |
| 7 | Rungs 05 and up sometimes crashed at the start with no crash log: Stewie's Tweaks' grabbed-weight hook read an empty object while TTWVR asked about encumbrance during the load; the crash logger then died itself in the C runtime | 2026-11-14 | our mod `Bridge - Stewie grabbed weight off` (`bEncumbranceIncludesGrabbedItems = 0` through `Tweaks\INIs`), on in every rung: 18 of 18 starts up, against 4 of 9 crashed before (`modding-notes/2026-11-14-the-rung-5-crash-is-stewie-s-grabbed-weight-hook.md`) |
| 8 | `rung_simcheck.py` said "new crash logs 0" through every crash: it looked only in `Crash Logs\`, while the crash logger writes `overwrite\Root\CrashLogger.log` first and (when it survives) copies it there | 2026-11-14 | `crash_logs()` also counts that single file when it holds an exception |

## Questions for mod authors

None, and none will be asked: decided 2026-11-12 (Tefa), we do not take anything about the modding process to the
VR mod's author. Two faults of TTWVR 1.0.0 that a desk run meets are written down for ourselves only; our desk add-on
steps around both (`modding-notes/2026-11-12-live-picture-in-the-simulator.md`):

1. With the Virtual Desktop Streamer running and nobody in the headset, the empty `VirtualDesktop.BodyState` memory is
   trusted over the mod's own body solver: no body at all.
2. On a headset runtime whose pictures give no old-style shared handle, DLSS mode shows a frozen eye with no log line
   (the previous picture is copied forward).
