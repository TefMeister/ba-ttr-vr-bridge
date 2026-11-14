# Gold Digger: a Stewie's Tweaks crash in a rung 4 simulator run (2026-11-13 15:41)

From the full scan of 2026-11-14 (Keeper PC). Shelf `logs`, item `2026-11-13_15-41-20_PC1_CrashLogger.log`.

Of the 18 crash-logger files shelved for this project, only this one holds a real crash; the others are the
logger's empty start-up banner. `[measured 2026-11-13, the crash log]`

- `EXCEPTION_ACCESS_VIOLATION (C0000005)`, top of the call trace:
  `nvse_stewie_tweaks (0x1007361E) IsOverencumberedAddGrabbedWeightHook+0xE`, called from `FalloutNV 0x00954CFC`
  and `0x008BA351`.
- Time: 15:41:20, inside the run folder `runs/2026-11-13 1540 rung-04 gameplay sim` (the next run, rung 5, started at
  15:41). The notes so far name rung 5's failed first start (`2026-11-13b`), not a rung 4 crash.
- "Topmost module is not always the cause" (the logger's own warning): Stewie's hook adds the weight of a grabbed
  object; with TTWVR the hands grab things, so a grab with no valid object is one possibility `[hypothesis]`.

Proposed board row: `[FLAT]` or `[VR CLAUDE]` — does the rung 4 sim run crash again at the same hook; if so, which
Stewie's Tweaks setting (grabbed-weight) to switch off in Begin Again's INI for the VR rungs.
