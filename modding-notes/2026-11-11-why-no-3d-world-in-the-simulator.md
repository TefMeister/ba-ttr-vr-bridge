# Why the OpenXR Simulator gets menus but no 3D world from TTWVR: what a no-game pass could and could not say

2026-11-11, /pd on the Developer PC (Fable). **The game was not launched and nothing of TTWVR's was changed or run.**
TTWVR.dll (1.0.0, build 6AF014A8) was read on disk only, to see what its own log lines mean. Not solved; narrowed, and
the next run is now built to answer it.

## What the missing `[camtrack]` line really means

- The line `[camtrack] no body tracking and no Virtual Desktop body: the body is solved from the headset and the
  controllers (floor from the %s)` is printed once, by the body solver, **on the first frame where its own head
  reading succeeds** (xrLocateSpace of the head against the mod's base space, at the frame's display time plus a small
  look-ahead, needing both "valid" flags). `[inferred-static]`
- The solver is only reached when all of these hold: Full Body is on (`[Body] bEnabled`, the VR menu's "Full Body"),
  the runtime gave no body tracker, Virtual Desktop's body memory (`VirtualDesktop.BodyState`) is not there, and the
  head and hand spaces exist. `[inferred-static]`
- `%s` is `play space` when a STAGE space could be made, else `head, 1.65 m below it`: the mod has its own fallback
  for a missing floor, so a missing play space cannot be what stops it. `[inferred-static]`

## What was ruled out

- **The simulator does give a valid head reading.** Our own probe (a small OpenXR program, no game; 64-bit runtime
  1.7.1, GL session) asked for the head in LOCAL and in STAGE at the display time, +11 ms, +50 ms, +1 s and -100 ms
  over six frames: both "valid" and both "tracked" flags every time, head at 1.70 m. `[measured 2026-11-11, n=60]`
  Caveat: the game uses the 32-bit runtime and a D3D11 session; same release, not the same file.
- **STAGE exists in the simulator; LOCAL_FLOOR does not** (refused as unsupported). `[measured 2026-11-11]` The mod
  names `XR_EXT_local_floor` among the extensions it knows; whether it needs it was not established.
- **The frame loop itself is healthy.** The one file of the simulator's that survived from 2026-11-10
  (`runs/2026-11-10 0901 sim projection record ...`) shows the mod handing over two 2944x2208 eye pictures on every
  one of 64 frames in a row, each from a newly released image. `[measured, n=1 file]` So frames are not being
  refused: fresh pictures arrive, and it is their content that does not change.
- So the 2026-11-10 `[hypothesis]` "the body solve waits for something the simulator does not give, and the world
  view hangs on it" is **not supported as written**: `[disproved 2026-11-11]` for the head reading and the play space;
  open for anything else.

## What it most likely is `[hypothesis]`

Two lines are missing in the simulator, not one: `[camtrack]` (printed at the main menu in the headset run) and
`[aim]` (printed when a weapon mesh is first handled). Together with fresh-but-unchanging eye pictures and menus that
do follow the head, that reads as **the mod's in-world part never starting**, with only its menu path alive. What
could hold it back, in the order the next run should check:

1. a call the simulator refuses that Virtual Desktop accepts (the mod's frame step leaves silently on any refusal
   except "session lost");
2. the session never reaching the state the mod waits for, or dropping out of it when the simulator's window is not
   in front (one sim run did log `the headset's session is gone`);
3. Full Body switched off for the run. Side fact found on the way: the mod parks Full Body off while the player's
   scale is under 0.6 `[inferred-static]` (worth knowing for any mod on the list that shrinks the player).

## Why it could not be settled today, and the fix

The simulator writes a log of every call, every refusal and every session state, but keeps only its newest few; the
2026-11-10 Fallout logs were gone, and `collect_run.py` had never kept them. **Fixed:** for any rung whose name ends
in ` sim`, `collect_run.py` now also keeps the simulator's own log files and its per-frame record (top level only,
home paths scrubbed as before). `[compile-verified]` and run once against a scratch folder (12 files kept, no home
path in any). Not yet run after a real game start.

## The one run that answers it

`python tools/rung_simcheck.py ... --rung "rung-01 vr base"` (as on 2026-11-10), then in the new run folder:

- `simulator__openxr_simulator.<number>.log` has lines with `ERROR` after the session starts -> cause 1: the refused
  call is named there. Whether we can step around it from our side (an API layer of our own between the mod and the
  simulator) depends on which call.
- no refusals, but the last `SESSION_STATE_CHANGED` is not `FOCUSED`, or it leaves FOCUSED -> cause 2: keep the
  simulator's window in front or set the focus from the simulator's own tool, and run again.
- neither, and `TTWVR.log` still has no `[camtrack]` line -> cause 3, or something not on this list; then the
  simulator's log shows which calls the mod stops making after the save loads (hands located? views located?), which is
  the next thing to read.

If `[camtrack]` does appear and the world still stands still, the body solver is cleared for good.
