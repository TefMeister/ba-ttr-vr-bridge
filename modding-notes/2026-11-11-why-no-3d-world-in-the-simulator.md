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

---

# Later the same evening: two desk runs of rung 1 (Tefa's yes), and a strong suspect

Runs kept: `runs/2026-11-11 2153 rung-01 vr base sim` (the script) and `runs/2026-11-11 2200 rung-01 vr base sim` (started
the same way, left up to look at). The game was closed politely both times; the saves are byte-identical to the copy
taken before; MO2 opens on `rung-02 fixes` again; the VR Bench layer is off.

## What the simulator's own log settled

- **No call is refused.** After the session starts the only errors in the log are the simulator's own preview window
  (see the next point). Cause 1 above is out. `[verified-live 2026-11-11, n=2]`
- **The session is healthy:** IDLE, READY, SYNCHRONIZED, VISIBLE, FOCUSED, and it stays FOCUSED. Cause 2 is out.
  `[verified-live 2026-11-11, n=2]`
- **The `the headset's session is gone` line is our own closing step.** A polite `taskkill /IM FalloutNV.exe` sends
  the close message to every window of the game's process, and the simulator's preview window lives in that process:
  the simulator takes it as "the user closed the headset view", stops the session, the mod connects again, and from
  then on the simulator cannot make its preview picture (`Failed to create DX11 preview swapchain`, 3,350 times) while
  the game takes up to 40 s more to go. Order in the log: head turned, then `STOPPING`, `WM_CLOSE`. `[measured, n=1]`
  This also explains the two copies that would not close on 2026-11-10. Harmless to the question, but the desk check
  should close the game some other way, or measure before it asks.
- **Full Body is on** in the running game: read from the mod's settings in memory (read-only): enabled 1, not parked,
  player scale 1.0. Cause 3 is out. `[measured, n=1]`
- **The mod's frame loop tracks the head.** With the head turned 40 degrees the eye pose the mod hands over with its
  pictures is turned the same. In the world it hands over two 4096x3648 pictures per frame (the upscaler's output; at
  the menu it is one 2944x2208 picture for both eyes). **Both are pure black**, and so is the game's own window.
  `[verified-live 2026-11-11, n=1]` So: tracking arrives, frames flow, the world is not in them.

## The suspect: Virtual Desktop's body memory exists on this PC, empty, and the mod trusts it

- `VirtualDesktop.BodyState` (the shared memory Virtual Desktop publishes body tracking in) **exists on this PC with
  nobody in the headset**, as long as the Virtual Desktop Streamer runs; its content is empty (the value the mod tests
  first is 0). `[measured 2026-11-11, n=1]`
- In the mod's code, each frame: it opens that memory; **when it is there, its own body solver is skipped**; when the
  memory's first value is not above zero the body is set to nothing and the step ends. `[inferred-static]` That is
  exactly a run with no `[camtrack]` line: that line belongs to the solver, and the solver never runs.
- On the headset evening (2026-11-09) the log says "no Virtual Desktop body": the memory was not there then, the
  solver ran, the world was fine. Whether the memory was there during the 2026-11-10 desk runs was not recorded.
- **Not established:** that an empty body is what blanks the world. It fits (the tag is "camtrack": the camera rides
  on the body; `[aim]` is missing too), but the link from "body is nothing" to "black eye pictures" was not read in
  the code and not tested. `[hypothesis]`

## The test that decides it

Quit the Virtual Desktop Streamer (tray icon, Quit), check `VirtualDesktop.BodyState` is gone, run
`rung_simcheck.py` on `rung-01 vr base`, start the Streamer again.

- `[camtrack] ... the body is solved from the headset and the controllers` appears and "world follows the head" says
  yes: solved. Every desk run then needs the Streamer closed (the check can refuse to start while that memory exists),
  and it is worth telling the mod's author: an empty Virtual Desktop body should fall back to the solver.
- the line appears and the world is still black: the body was one fault, not the fault; next is the picture path (the
  upscaler helper against the simulator's pictures).
- the line still does not appear: the reading of the code is wrong somewhere; back to the note above.

This session tried to close the Streamer itself and was refused by the session's own safety check (it is another
program's process), so the step waits for Tefa or an explicit yes.

---

# The decider, run the same night with the Streamer quit (Tefa quit it)

Runs kept: `runs/2026-11-11 2211 rung-01 vr base sim` (the script) and `runs/2026-11-11 2213 rung-01 vr base sim` (left up
to look at). `VirtualDesktop.BodyState` was checked gone before the start. Closed politely, saves identical, MO2 back
on `rung-02 fixes`, VR Bench off.

- **The reading of the code holds.** With the memory gone the mod logs, at the first frame, `[camtrack] ... Virtual
  Desktop's body memory is not there` and then `[camtrack] no body tracking and no Virtual Desktop body: the body is
  solved from the headset and the controllers (floor from the play space)`, exactly as on the headset evening.
  `[verified-live 2026-11-11, n=3 session starts]` So: **while the Virtual Desktop Streamer runs with nobody in the
  headset, TTWVR has no body at all** (the empty memory is trusted over the solver). That is a real fault for desk
  runs and worth telling KUPOkinz; with a headset on and streaming it does not arise.
- **It was one fault, not the fault.** The world's eye pictures are still pure black with the body solved (simulator
  screenshot, 70 s in, session FOCUSED); the script's "world follows the head" still says no. `[verified-live
  2026-11-11, n=2]` The pause menu now answers clearly (picture change 20.9 against 2.1 with the dead body).
- Still no `[aim]` line after the save loads.

## What is left: the picture path `[hypothesis]`

What the simulator's log shows of it: in the world the mod hands over the two 4096x3648 pictures every frame, but
the log records **no acquire of those two at all** (only of the 2944x2208 one used at the menu), where it lists the
first few acquires of every picture set. If that holds (the log may simply stop listing after the first few of the
session) the mod is handing over pictures it never took for drawing, which a strict runtime shows as black and
Virtual Desktop may forgive. Two more things differ from the headset and are not ruled out: the simulator caps
pictures at 4096 a side (the headset allowed 16384; 4096x3648 is not the shape of the 2944x2208 eye, so the upscaler
is asked for an odd stretch), and the upscaler helper (`ttwvr_dlss_host.exe`, a separate program) has to write into
pictures the simulator made.

Next, in order of cost:
1. `[PD]` read in the simulator's source or its log format whether acquires are listed for every picture set or only
   the first few lines of a session; that turns the "never acquired" reading into a fact or drops it.
2. `[FLAT]` one desk run with the VR menu's Upscaler off AND Resolution low enough that an eye fits in 4096 (both
   together; on 2026-11-10 they were tried, but with the dead body, so that result does not count any more).
3. If still black: the simulator's own frame tools (its per-eye freshness and D3D11 frame capture) on the two eye
   pictures, to see whether anything is ever drawn into them.

**Step 1 answered the same night (no game): the "never acquired" reading is dropped.** Eleven simulator logs from
three different games tonight (this one, a UEVR game, an RE Engine game) each list exactly 4 acquires and 10 releases,
whatever the game did: the simulator lists only a session's first few. So the log cannot say whether the two big eye
pictures are acquired. `[measured 2026-11-11, n=11 logs]`

**Every "not the cause" of 2026-11-10 has to be tried again:** the window in front, Continue by hand, the upscaler
off, the smaller eye were all measured while the body was dead, so none of them counts.

---

# Three more desk runs the same night (Streamer off, body solved): what is ruled out now, and one large clue

Runs kept: `runs/2026-11-11 2232 ... upscaler off, window in front` and `runs/2026-11-11 2235 ... continue by hand,
pause shows the world`. Every setting touched was put back and compared (the VR menu's settings file is byte-identical
to before; our own helper's auto-load is on again; saves identical; MO2 on `rung-02 fixes`; VR Bench off).

- **Not the upscaler, not the 4096 cap.** With `Upscaler=Off` and `Resolution=100%` the mod makes two 2944x2208 eye
  pictures (no 4096 ones, no helper in the path) and they are still empty. `[verified-live 2026-11-11, n=1]`
- **Not the game's window being covered.** With the game's own window brought to the front (checked: it was the front
  window) the eye pictures stay empty 20 s later. `[verified-live 2026-11-11, n=1]`
- **Not the auto-load.** With our auto-load off, the main menu shows in the simulator as a floating panel; Continue
  pressed with the robot hand's A loads the save; the eye pictures are empty all the same. `[verified-live, n=1]`
- **"Empty" is exact:** every in-world screenshot measures brightness 0 at every pixel (max 0), not "very dark".
  `[measured, n=4 screenshots]`
- **Not see-through pixels.** Our own probe handed the simulator eye pictures with colour but alpha 0: it shows the
  colours. `[measured 2026-11-11, n=1; the OpenGL path of the 64-bit runtime, the game uses D3D11 on the 32-bit one]`

## The clue: the game IS drawing the world

With the pause menu open (robot hand's Y) the mod hands over no eye pictures at all and shows the game's own picture
on a floating panel instead, and **in that panel the world is there**: the room of the save, the cages, the player's
arm. `[verified-live 2026-11-11, n=1]` So the game renders, the picture crosses from the game's renderer to the
headset session (the panel is the same size and kind of picture as an eye), and what stays empty is only **the mod's
two stereo eye pictures while playing**.

What that leaves `[hypothesis]`, most likely first:
1. The world is drawn for the eyes but from a camera that sees nothing: the eye's place or lens worked out wrongly from
   what the simulator reports. One thing seen: the mod hands its eye pictures over with a wider lens angle than the
   simulator gave it (left eye -61.5 to +52.5 degrees against the simulator's -54 to +40), so it is not simply passing
   the runtime's numbers through.
2. The mod's own stereo step (it draws once and makes the second eye from it, by its log's own words) does not start
   in the simulator: something it waits for after the body (a height it has not measured, a first both-eyes frame).
3. A difference in how the simulator's eye pictures may be written to that only the eye path meets.

Next: `[PD]` read in TTWVR.dll what the eye capture needs before it copies an eye (the strings around "stereo frame",
"capturing the left eye", "eye staging texture", "[eyeres]") and where its lens angles come from. `[FLAT]` with the
Streamer off: one run with the simulator's headset profile and lens set to match what the mod hands over, and one
with the robot doing the mod's height pose, each judged by the same zero-brightness test.

---

# Reading the mod's stereo step (no game, the same night)

All `[inferred-static]`, TTWVR 1.0.0 build 6AF014A8, read on disk only.

- The mod keeps a **state number**; its stereo frame (the step that draws and captures the two eyes; its own log
  texts: "stereo frame: before the left eye's draw", "after the one draw: capturing the left eye it made") runs
  **only in state 4**. Other states (5, 1, 3) are its menu and loading kinds: there it shows the game's picture on a
  panel, which is exactly what the pause menu showed on the desk run.
- Even in state 4 the stereo frame leaves at once unless four switches are on: two that the mod's own world step
  turns on once the player and the scene are ready, one "stereo allowed" flag (needs a setting, a game check and two
  inner flags), and a pointer.
- While playing on the desk run the mod does hand eye pictures over, so it believes it is in the stereo state or
  close to it; the pictures are empty because the capture inside never ran or captured nothing. Which switch is off
  cannot be read from the file: it depends on what the running game says.
- Not found: any wait for a measured height in this path. The lens angles are the mod's own (it has settings for a
  reference lens and an eye box); where they come from was not followed further.

**New tool, `tools/ttwvr_gates.py`:** reads those switches and the state from the running game, read-only, and refuses
on any other build of the mod. `[compile-verified]`, run once with no game (it says so and stops); not yet run
against the game.

**The next desk run** (Streamer off): start rung 1 in the simulator, wait for the save, then
`python tools/ttwvr_gates.py --watch 20`, press pause and back during it.
- state is not 4 while playing -> the mod thinks it is in a menu or loading: read what its state step waits for (one
  place in the code, known).
- state 4, a switch at 0 -> that switch names the missing piece; each has one or two places that set it.
- state 4 and every switch on -> the stereo frame runs and still captures nothing: then it is the capture itself
  (the mod's own renderer hand-over), and the place to look is what the eye capture copies from.

---

# The reader's run (Streamer off): the stereo step is fully on, and the world DOES appear, as one frozen picture

Run kept: `runs/2026-11-11 2250 ... gates all on, world appears frozen after pause`. Closed politely, saves identical,
MO2 on `rung-02 fixes`, VR Bench off.

- **`tools/ttwvr_gates.py` works against the game** and says: state 4, both stereo switches 1, "stereo allowed" 1,
  Full Body 1 and not parked. (Its two "session" lines read nonsense: wrong places, to be taken out.)
  `[verified-live 2026-11-11, n=2 readings]` So outcome three: the mod's stereo step runs and nothing comes of it.
- **First sight of the world in the simulator:** after one pause and un-pause (robot hand's Y, then B) both eye
  pictures show the room of the save, in stereo, with the player's arms. `[verified-live 2026-11-11, n=1]` Before
  that pause they were exactly empty, as in every run before.
- **But the picture is frozen.** With the head turned 50 degrees the mod hands its pictures over with the turned
  pose, and the picture is pixel for pixel the same. `[verified-live, n=2 screenshots]` The game's own window is
  frozen on the same picture too (change on a 90 degree turn: 0.00), in front or not. `[measured, n=2]` (The window
  reading uses a Windows call that may return an old picture for this kind of window; the eye reading does not.)
- The picture fills only the upper left 72% by 60% of each eye: the 2944x2208 eye inside the 4096x3648 picture the
  simulator's size cap forces. With the upscaler off the eye is 2944x2208 and would fill it.
- This is the 2026-11-10 symptom ("the picture stays on one frame, or black") seen properly: **the eye pictures are
  written once, at a pause change, and never refreshed.** Black is "never written yet".

What that means `[hypothesis]`: the per-frame copy of each eye into the headset's pictures is the piece that does not
run in the simulator, while one other path (used at a pause change) does write them. The mod's own texts name two
ways of copying an eye ("deferred eye copy ... the eyes are copied the old way (waiting for DXVK)", "eye staging
texture") and the class that starts it (`VRSystem::StereoCopyBegin`). A headset runtime like Virtual Desktop makes its
pictures shareable between programs and graphics systems; the simulator's are plain. If the mod's per-frame way
needs a shareable picture, that is the whole difference.

Next:
1. `[PD]` read `StereoCopyBegin` and the two copy ways in the DLL: what each needs from the headset's picture, and
   which is used at a pause change.
2. `[FLAT]` the same run with the upscaler off: black, then frozen after a pause, or live?
3. If it is the shareable-picture difference: that is something we can supply from our side, a small layer of our own
   between the mod and the simulator that hands the mod shareable pictures. Our code, nothing of the mod's changed,
   and only ever loaded on desk runs.

---

# Reading the mod's eye hand-over (no game, later the same night)

All `[inferred-static]`, TTWVR 1.0.0 build 6AF014A8, on disk only.

- **How an eye travels, by the mod's own texts and code:** the game draws through DXVK (Vulkan). The mod makes its
  own shareable Direct3D 11 pictures ("shared %s %ux%u", "shared handle for %s"), brings them into Vulkan, and has the
  eye copied there by DXVK's worker ("deferred eye copy"), timed by a Direct3D 11 fence brought into Vulkan. With the
  upscaler on, a second program (`ttwvr_dlss_host.exe`) turns that into the big picture, again in shared pictures.
  Last, on the Direct3D 11 side, the mod takes the headset's picture, waits on the fence, copies its own shared
  picture in and gives the headset's picture back.
- **So the shareable pictures are the mod's own, not the headset's.** The headset's picture only receives an ordinary
  copy at the end. The guess "the simulator's pictures are not shareable, that is the difference" is therefore
  **dropped**: `[disproved 2026-11-11]` by this reading. No layer of ours is called for.
- The last step has no hidden condition: frame begun, eye 0 or 1, a source picture, the headset's picture ready. If it
  is called, the copy is made. So a frozen eye means **the copy runs with a stale source, or is not called**: the
  fault sits before it, on the game's side of the chain (the Vulkan eye copy, or with the upscaler on the helper
  program never producing a frame).
- What the desk run showed fits "the helper never produces": the one picture that did arrive after the pause change
  was the small, un-upscaled eye (2944x2208, top left of the big picture), which is the mod's stated fallback ("the
  eyes go the old way") for a moment when the upscaler is reset. The mod has a warning for an eye left without an
  upscaled frame for 2 s; it did not appear, so this is `[hypothesis]`, not a finding.

**What decides it is the run already on the board:** rung 1 in the simulator with the VR menu's Upscaler off (then the
helper is out of the chain), one pause and un-pause, head turned.
- live picture that follows the head -> the helper program is the piece that does not work on a desk run; desk runs
  use Upscaler off (in a desk-only settings copy, never Tefa's), solved for our purpose.
- frozen or black again -> it is the Vulkan eye copy itself; next is DXVK's own log beside the mod's
  (`FalloutNV_d3d9.log`), which the run collector should start keeping.

---

# The upscaler-off run (Streamer off): not the helper; every pause change gives one fresh, correct still

Run kept: `runs/2026-11-11 2306 ... upscaler off, a fresh still at each pause change`. The VR menu's settings file is
byte-identical to before again; saves identical; MO2 on `rung-02 fixes`; VR Bench off.

- **Not the upscaler's helper program.** With `Upscaler=Off` the picture behaves exactly as with it on: empty until a
  pause change, then one frozen picture. `[verified-live 2026-11-11, n=1]`
- **Not the game's window being covered,** tested properly this time: with the world showing and the game's window in
  front, the picture stays frozen on a 100 degree head turn. `[verified-live, n=1]`
- **Each pause and un-pause writes one new, correct picture.** Head turned 50 degrees left, pause, un-pause: the eye
  now shows the room from that direction (the cages in the middle, the arms elsewhere). `[verified-live 2026-11-11,
  n=2 pause changes]` So the game draws the world for the eye from the live head, the mod's body and stereo steps
  work, and a picture can reach the headset. **What is missing is only the refresh on ordinary frames.**
- With `Resolution=165%` the eye pictures are 4096x3648 even with the upscaler off, and the 2944x2208 eye sits in
  their top left; that is the simulator's size cap at work (the headset's log had the same 2944x2208 eyes).

Where that points `[hypothesis]`: the mod has two ways to copy an eye, by its own texts: an immediate one ("the old
way (waiting for DXVK)") and a deferred one done by DXVK's worker and timed by a fence. A pause change plausibly
resets the stereo frame and takes the immediate way once; ordinary frames take the deferred way, and in the simulator
its result never lands. Why the deferred way would depend on the headset runtime is not known. One real difference:
the simulator does its own drawing (its preview, its timing queries) on the game's Direct3D 11 device inside the
frame calls, which Virtual Desktop does not.

**What a desk run can do today, without solving it:** a head-tracked still on demand. Set the head and hands, pause,
un-pause, take the simulator's screenshot. That is enough to check "does this rung draw the world, are the hands and
the gun where they should be, is anything missing or pink".

Next:
1. `[PD]` `rung_simcheck.py`: judge "world is drawn" from a simulator screenshot after a pause change (brightness
   above zero, and different after a head turn plus a second pause change), refuse to start while
   `VirtualDesktop.BodyState` exists, put MO2 back on the rung it found.
2. `[PD]` read what a pause change does to the mod's stereo frame (the "menu's stereo frames start / end" place) and
   which copy way the first frame after it takes.
3. `[FLAT]` with the Streamer off: the simulator's preview switched off or minimised for one run (does the picture go
   live when the simulator stops drawing on the game's device?).

Tool fix made on the way: the collector skipped the simulator's log whenever the run had a label after the word
`sim`; fixed, and the eight simulator logs of the evening are rescued in
`runs/2026-11-11 simulator logs of the labelled runs (rescued)`.

---

# The desk check rewritten to use it (no game, the same night)

`tools/rung_simcheck.py` now judges a rung by the picture the VR mod hands to the headset, taken with the simulator's
own screenshot request (never the desktop): pause (the panel must show), un-pause (the world must be in the eye),
turn the head, pause and un-pause again (the eye must show another view). It refuses to start while Virtual
Desktop's body memory exists, says whether the body was solved, closes last and never by force, leaves MO2 on the
profile it found, and keeps the two stills in the run's folder.

`[compile-verified]`; its pieces were run without the game: the refusal (the Streamer was running: it refused and
said why), the profile reader, the screenshot routine against our own probe in the simulator (a 669x697 picture,
the same picture twice gives change 0.0), and "no picture" when no session is up. **Not yet run against the game.**

---

# The rewritten desk check run on all eight rungs (2026-11-12 01h10, the Streamer quit, nobody in the headset)

`tools/rung_simcheck.py`, one run per rung, runs `runs/2026-11-12 0111 ...` to `0124 ...`. Every rung: up, body
solved, save loaded (18 to 30 s), no crash log, no hang warning, closed politely at the first ask, MO2 left on the
profile it was on. `[verified-live 2026-11-12, n=8 rungs, one run each]`

| rung | add-ons | pause panel (change) | world drawn (grey level) | follows the head (change) |
| --- | --- | --- | --- | --- |
| 1 vr base | 21 | YES 13.31 | YES 6.94 | YES 4.06 |
| 2 fixes | 45 | YES 13.32 | YES 6.87 | YES 4.04 |
| 3 world | 49 | YES 13.48 | YES 7.60 | YES 3.97 |
| 4 gameplay | 49 | YES 13.48 | YES 7.70 | YES 3.96 |
| 5 interface | 55 | YES 3.59 | YES 7.64 | YES 3.97 |
| 6 armor and people | 55 | YES 3.57 | YES 7.60 | YES 4.07 |
| 7 weapons | 55 | YES 3.56 | YES 7.55 | YES 4.07 |
| 8 animations and the rest | 57 | YES 4.55 | YES 7.61 | YES 4.05 |

The stills, looked at by eye (two per rung, head straight and head turned 60): the same cell room on every rung,
both arms with the Pip-Boy in place, nothing missing, nothing pink. From rung 3 the floor and wall textures are the
world mods' own (the picture's level goes from 6.9 to 7.6). `[verified-live 2026-11-12, n=1 per rung]`

Two things to follow, neither a failure:
- **The pause panel changes the picture much less from rung 5 on** (13.4 down to 3.6): the interface mods give the
  pause screen another look. Still far over the limit of 1.0, but the panel itself was not looked at by eye: the
  check keeps no still of it. `[measured]`; what the panel looks like is `[hypothesis]` until a still is kept.
- **Rung 8 alone has the mod's camera complaint** ("Camera1st's parents are not Bip01 Looking / NonAccum / Bip01 in
  this skeleton: only Camera1st itself is held at rest"); rung 7 does not have it. The still shows no harm with the
  body standing; the row about the rung 8 split already covers finding which mod brings that skeleton.
