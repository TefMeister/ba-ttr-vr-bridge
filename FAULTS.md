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

## Questions for mod authors

(none yet; added here the moment one is needed, with who to ask and where)
