# 2026-11-14: the rung-5 start crash is Stewie's Tweaks' grabbed-weight hook (and why it left no crash log)

Developer PC, Opus, nobody in the headset. Tefa: *"play fallout and add groups of mods to see if anything actually
crashes the game step by step, and if a crash happens please see why"*. Every VR rung (01 to 08c) started on the OpenXR
Simulator with the VR Bench hands through `tools/rung_simcheck.py`, twice over (`climb.sh`, kept with the run notes).

## What happened

Round 1, 13:14: rung 05 (interface) gone 17 s after the start, before the save loaded; rungs 01-04 and 06-07 up, save
loaded, world drawn, following the head, pause panel shown. The checker said "new crash logs 0".

## Why it left "no crash log" `[measured 2026-11-14]`

- Windows (Application log, 13:14:39): FalloutNV.exe, faulting module `ucrtbase.dll`, code `c0000409` sub-code 5: the C
  runtime's invalid-argument fail-fast.
- Windows also kept a full dump (`%LOCALAPPDATA%\CrashDumps\FalloutNV.exe.9520.dmp`, copied aside). Read with a small
  script (Python `minidump`, no debugger installed): the failing thread is the crash logger itself (`CrashLogger.dll`,
  `nvse_dbghelp.dll` on the stack) inside the C runtime; further down the same stack lies the FIRST error, an access
  violation at `nvse_stewie_tweaks.dll+0x7361E`, reading address `0x640` (an empty object plus an offset).
- So: Stewie's Tweaks crashed; the crash logger caught it and wrote `overwrite\Root\CrashLogger.log`; then the logger
  itself died in the C runtime before it copied that file into `overwrite\Root\Crash Logs\` with a date. The checker
  looked only in `Crash Logs`, and the next start rewrites `CrashLogger.log` (the run collector had kept a copy in
  `runs/2026-11-14 1314 rung-05 interface sim/`). Fixed: `rung_simcheck.py`'s `crash_logs()` counts that single file too
  when it holds an exception.

## The crash itself `[measured 2026-11-14, n=2 with 2026-11-12]`

`CrashLogger.log`: main thread, top frame `nvse_stewie_tweaks (0x1007361E) IsOverencumberedAddGrabbedWeightHook+0xE`
(`main.h:4356`), `eax = ecx = 0`, `ebx` = the player; called from the game's encumbrance code, called from TTWVR's frame
code (`TTWVR NVSEPlugin_Load+0x108A19`), during the save load. The SAME address as the rung-5 crash of 2026-11-12 09:19
(one start in seventeen then). `[inferred]`: TTWVR asks "is the player over-encumbered?" while the save is still loading;
Stewie's hook then adds the weight of the item held by hand, but the grabbed-item data is not there yet and the hook does
not check. A race: rung 6 and 7 (which also hold Stewie's Tweaks) came up fine the same minute.

Begin Again's `nvse_stewie_tweaks.ini` has `bEncumbranceIncludesGrabbedItems = 1` and `bMultiINISupport = 1` (INIs in
`NVSE\Plugins\Tweaks\INIs\` overrule the main one).

## The fix (the one that was ready since 2026-11-12, applied now the same top frame came back)

Our own MO2 mod `Bridge - Stewie grabbed weight off` (source `bridge-mods/`): one file,
`NVSE\Plugins\Tweaks\INIs\zzBridgeFixes.ini`, `[Tweaks] bEncumbranceIncludesGrabbedItems = 0`. On in every rung, VR and
flat (`ladder_groups.py` `BRIDGE_MODS`, just under TTWVR). Cost: an item carried by hand no longer counts toward the
weight limit. Begin Again's own files untouched.

## Round 2, before the fix: not rung 5 alone `[measured 2026-11-14]`

Rung 05 crashed again (13:29), then rung 07 (13:32) and rung 08a (13:33): the same first error each time
(`nvse_stewie_tweaks.dll+0x7361E`, address `0x640`, read from the Windows dumps, all three kept). Rung 06 of round 2 never
started: after each crashed start Steam's `x64launcher.exe` and Mod Organizer stay up waiting, and the next start refuses
(the board's open row about `x64launcher`; it also held Mod Organizer this time). Before the fix, of the nine starts with
Stewie's Tweaks today, four crashed; every rung from 05 up can do it. Rungs 01-04 (no Stewie's Tweaks): 8 of 8 up.

## With the fix: 18 of 18 `[verified-live 2026-11-14, n=18]`

`Bridge - Stewie grabbed weight off` switched on in every rung profile (VR and flat; 32 profiles, each `modlist.txt`
backed up as `*.bak-2026-11-14-stewie`; `rung-00 flat base`, the author's untouched list, left alone). Then rungs 05, 06,
07, 08a, 08b and 08c three times each (`tools/rung_repeat.sh`): 18 of 18 up, save loaded, world drawn, following the head,
pause panel shown, no crash log, no Windows crash report. Stewie's Tweaks does read `Data\NVSE\Plugins\Tweaks\INIs\`
(the folder name is in its DLL). Mod Organizer left on `rung-05 interface`.

## Still to do

- Tefa in the headset on any rung from 05 up: does it start first time now, and does carrying something by hand feel
  any different (it no longer counts toward the weight limit).
- The crash logger dying while it reports is its own fault (its dated copy is lost); not ours to fix, noted.
- `rung_simcheck.py` should itself end the hung `x64launcher.exe` and Mod Organizer after a crashed start
  (`rung_repeat.sh` does it from outside).
