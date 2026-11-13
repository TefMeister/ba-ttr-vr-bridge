# 2026-11-13 reader: TTWVR's command file `NVVR-cmd.txt`, pinned from the DLL

From: the static reader (read-only). Method: disassembled a scratch copy of `TTWVR.dll` (32-bit, image base
0x10000000, TTWVR 1.0.0 build 6AF014A8) around the string references, using capstone. Addresses are virtual
addresses in that build. For: the modding lane.

## 1. Where and how often `[measured]` unless tagged

- **Folder: the folder that holds `TTWVR.log`.** The handler (0x1022DAC0) takes the global path string at
  0x10D774A8, cuts it at its last `\` or `/`, and appends `NVVR-cmd.txt`. 0x10D774A8 is the log file's full path:
  the crash/exit writer opens it with CreateFileA and writes the "[exit] ..." line into it.
  - On this PC `TTWVR.log` is written in `~/Documents/My Games/FalloutNV/` `[measured]`.
  - So the file is **`~/Documents/My Games/FalloutNV/NVVR-cmd.txt`**.
- **How often:** the handler keeps its own call counter and acts on every **15th** call (`counter % 15 == 0`).
  - Its first use registers the path with a file-watch helper, which starts its own background thread
    (CreateThread). The file is then opened only when that helper reports something for it.
  - The handler is reached only through an incremental-link jump stub (0x10002C8E). No static caller was found, so
    it is called through a pointer set up at run time.
  - That it runs from the per-frame code, i.e. roughly every 15 frames (about 0.2 s at 72-90 Hz), is
    `[inferred]`.

## 2. After reading: the file is DELETED `[measured]`

The file is opened `"rb"` and up to **2,047 bytes** are read. It is closed, then removed with `DeleteFileA`
**before** any command runs. Write the whole file in one go (write to a temporary name, then rename it to
`NVVR-cmd.txt`), or the watcher may catch it half-written `[inferred]`.

## 3. Syntax `[measured]` (parser in 0x1022DAC0..0x1022EA9C)

- **One command per line.** Lines are split on CR/LF; leading spaces are skipped. Most verbs are matched as a
  **prefix** (`strncmp`), some as **exact** (`strcmp`); both are marked below.
- What each command does is `[inferred]` from names and log strings unless stated.

| line | match | what it does |
| --- | --- | --- |
| `console <command>` | prefix `"console "` | runs the rest of the line as a game console command; logs `[cmd] no console` if the console is not available. **This is the useful one: `console player.moveto SpringvaleElementaryMapMarker`, `console player.setangle z 121`, `console tm`.** |
| `pipboy [stats\|data\|...]` | prefix | opens the Pip-Boy on a tab: `stats` → menu 1003, `data` → 1023, anything else → 1002 (items) `[measured]` IDs |
| `gorebench <args>`, `worldbench <args>` | prefix | start TTWVR's own gore/world bench runs (rest of line passed on) |
| `tab` | exact | steps the Pip-Boy tab |
| `localmap`, `worldmap` | exact | **removed**: prints `[cmd] %s: removed - a bare write of the map page crashed lStewieAl's Tweaks ...` |
| `mapdump`, `dumpoverflow`, `dumpburst`, `pmflag` | prefix | map / Pip-Boy diagnostics (`pmflag` needs the Pip-Boy manager) |
| `message ...` | prefix | shows a game message box (the "Do you want to set your marker?" / "Yes" strings are used) |
| `dumpfront [name]`, `dumpback [name]` | prefix | arms a one-shot picture dump, written by the Direct3D 9 hook the next time it passes that point. Mode 1 = front, 2 = back. The optional name is up to 64 characters; defaults are **`NVVR-cmd-front.bmp`** / **`NVVR-cmd-back.bmp`**. |
| `dump [name]` | prefix | immediate dump, default name **`NVVR-cmd-dump.bmp`** |
| `probe ...` | prefix | a probe (arguments parsed; purpose not read) |
| `key <n>` | prefix | `n` read as a **decimal** number: sends a key code |
| `pad <hex>` | prefix | `hex` read as a **base-16** number: sends a gamepad button mask |
| `focus <...>`, `dispatch ...` | prefix | menu focus / dispatch on a named tile |
| `set ...`, `cull <node>`, `show <node>`, `root ...`, `status` (exact) | mixed | menu-tile / scene-node operations: `[cmd] no tile '%s' in menu 0x%X` on a miss. `cull` / `show` hide or show a NAMED NODE. They are **not** the far-view culling switch (`bFogCull`). |

**Where the BMPs go** `[measured]`: the writer (0x10565980) builds its path from the same log path at 0x10D774A8.
They land beside `TTWVR.log` in `~/Documents/My Games/FalloutNV/`.

Which picture "front" and "back" are is `[inferred]`. The write happens inside the Direct3D 9 device-call path,
around a device call, so it is probably the game's own frame buffer at two points, not a stereo eye. One test run
answers it.

## 4. Is it gated? `[measured]` / `[inferred]`

- **No setting is tested inside the handler.** The only gates are the 1-in-15 counter and the file watcher
  `[measured]`. Whether its caller tests a setting is not known (caller not found statically).
- TTWVR does read **hidden keys beyond the VR menu's own**, via section + key. The same reader call that sets the
  `[VR]` options also reads these `[measured]`:
  - **[DLSS]** `bDiagnostics`, `bRigidMotion`;
  - **[Debug]** `bProfiler`, `iProfilerWindows`, `fProfilerStartS`, `bHitchProfiler`, `iStereoCheckFrames`,
    `iRenderWidth`, `iLogFirstFrames`, `bLogWeaponTree`, `bLogPerf`, `bLogShots`, `bLogRenderPasses`,
    `bTestHeldPassWithoutVR`, `sDebugLoadSave`.
- None of them is named like a command-file switch. That they come from `TTWVR.ini` is `[inferred]` (the log says
  "Settings: built in + the VR menu's choices in ...TTWVR.ini").
- So the command file is most likely **always on** `[inferred]`.

**Cheapest proof:** one simulator run with a file containing `console tm` plus `dumpback`. Then check:
- the file vanishes within about a second;
- the HUD toggles;
- a BMP appears beside `TTWVR.log`.
