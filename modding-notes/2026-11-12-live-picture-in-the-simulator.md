# The live picture in the OpenXR Simulator: found and worked around from our side

2026-11-12 morning, /lm on the Developer PC (Fable), nobody in the headset, the Virtual Desktop Streamer RUNNING the
whole time. Continues `2026-11-11-why-no-3d-world-in-the-simulator.md`. Nothing of TTWVR's or Begin Again's was
changed on disk; everything new is our own desk-test add-on, loaded only by the `<rung> sim` profiles.

## Outcome

Rung 1 in the simulator shows a **live, head-tracked, upscaled stereo picture** at Tefa's own settings (Resolution
165%, DLSS Performance): change on a 40 degree head turn 8.19, back 0.40, with no pause trick; four views at 0 / 30 /
60 / 90 degrees looked at by eye (the cell room turns, both arms stay with the body).
`[verified-live 2026-11-12, n=3 game starts]`

## The two faults a desk run met, and what our add-on does about each

Our add-on is `desk-shim/` (an xNVSE plugin, `bridge_desk.dll`, in our MO2 mod `Bridge desk test - continue on
start`). It writes `bridge_desk.log` beside `TTWVR.log`.

### 1. No body while the Virtual Desktop Streamer runs (known since 2026-11-11)

The Streamer runs with admin rights; a desk session cannot quit it (Windows: access denied). `bridge_desk.cpp`
answers TTWVR's own question "is `VirtualDesktop.BodyState` there?" (its imported `OpenFileMappingW`) with "not
there", for that one name, inside the game's process. The mod then logs its usual `[camtrack] ... the body is solved
from the headset and the controllers`. `[verified-live 2026-11-12, n=8 game starts]`

### 2. The frozen eye: the upscaler's helper draws into the HEADSET's pictures, and the simulator's cannot be shared

How TTWVR 1.0.0 (build 6AF014A8) hands over an eye with DLSS on, by reading the DLL and watching it live:

- With OpenXR and DLSS the mod is always in a "direct" mode: its helper program (`ttwvr_dlss_host.exe`) draws each
  finished eye **straight into the headset runtime's own swapchain picture**. The mod's own output pictures are then
  16x16 stand-ins. `[inferred-static]` (decision at 0x1045D0AE; the OpenXR backend answers "direct possible" with a
  plain yes) + `[measured]`: the six output pictures read live are 16x16.
- To give the helper the headset's pictures, the mod asks each swapchain image for a handle **the old way**
  (`IDXGIResource::GetSharedHandle`, 0x10541140). `[inferred-static]`
- Virtual Desktop's pictures give such a handle. The simulator's are plain pictures (no sharing flags): the call
  fails, nothing is published to the helper, and the helper reports "none" for every frame (six indexes, all -1).
  `[measured live]`
- The mod's last copy (0x1054BD60) then has three routes: use the picture the helper drew into (never: index -1);
  copy from the mod's own output (refused: 16x16 is smaller than the eye); or, silently, **copy the headset picture of
  the frame before into the new one**. That third route is what ran, 180 times a second.
  `[verified-live 2026-11-12]` with our probe: the only copies into the eye pictures were image i-1 into image i.
- Every counter of the mod's meanwhile reads healthy (posted = shown, nothing "not produced"), and there is no log
  line. The one fresh still per pause change was the mod's plain path writing its small picture once.

What we do: `shareable.cpp` has every picture of the simulator's swapchain shape (typeless colour, draw + read, no
flags) made with the old sharing flag (`D3D11_RESOURCE_MISC_SHARED`, 0x2) added. Nothing else about the picture
changes; the simulator works with them as before.

- flags 0x802 (the newer kind, what TTWVR uses for its own pictures): pictures made, eye still frozen.
  `[verified-live, n=1]` (the old-way handle call refuses the newer kind)
- flags 0x2: live. `[verified-live 2026-11-12, n=3 game starts]`

## Ruled out on the way (all `[verified-live 2026-11-12]`, rung 1)

- The simulator's preview window: minimised, the eye stays frozen (the board's `[FLAT]` row; answer: no).
- The game's window in front: no change.
- The mod's drawing step: its stereo switch flips 90 times a second, the game process uses about 13% of the GPU.
- The 4096 size cap: at Resolution 100% (no cap involved) it froze the same way.
- A stalled Direct3D queue: the simulator's own drawing stayed live throughout.
- The headset's "draw this frame" flag: on for the whole 6 ms a frame is begun.

## Tools made

- `desk-shim/bridge_desk.cpp`, `shareable.cpp`: the two workarounds above. `build.bat` builds the 32-bit DLL.
- `desk-shim/d3d11_probe.cpp`: off unless `BRIDGE_DESK_D3D11_PROBE=1`. Logs each new kind of Direct3D 11 copy
  (sizes, formats, flags, which pictures), counts per 5 s, the fence waits, every large picture request, and the real
  sizes of the upscaler bridge's own pictures. It is what found the cause.
- `tools/rung_simcheck.py`: now judges a LIVE eye (world drawn and a different view on a head turn, nothing
  pressed), then the pause panel. `--stay` leaves the game up. It no longer needs the Streamer quit.
- The mod's live counters and places used today are listed in the reader's notes kept in this session; the ones worth
  keeping: helper's drawn-into indexes at `[0x1136638C]+0x61F44` (six, -1 = none), direct-mode flag 0x11365D80,
  handle generation 0x11366248, fallback counters backend+0x2B70 / +0x2BA0, posted / shown 0x11397A90 / 0x11397A94.

## What is NOT established

- Why the plain path (Upscaler=Off) was also frozen on 2026-11-11: not looked at again; desk runs keep the upscaler on.
- The picture at 165% in the simulator is capped at 4096 wide by the simulator; whether the capped picture is
  geometrically right at the edges was not checked.
- Nothing here says anything about the real headset: there the pictures were always shareable.

## Worth telling the mod's author (Tefa decides; we do not fill other people's channels)

1. With Virtual Desktop's Streamer running and nobody in the headset, the empty `VirtualDesktop.BodyState` is trusted
   over the body solver: no body at all.
2. On a runtime whose swapchain pictures give no old-style shared handle, DLSS mode silently shows a frozen eye
   (copy-forward of the previous picture). A log line there, or falling back to the mod's own full-size output, would
   make it visible. FSR mode keeps a full-size output of its own `[inferred-static]`, not tried.

---

# The same morning: all eight rungs, live, and through the door to the outside

`tools/rung_simcheck.py --outside`, one run per rung (runs `2026-11-12 0943 ...` to `1001 ...`), the Streamer running,
Tefa's own settings. Every rung: up, body solved, save loaded (15 to 24 s), no crash log, closed politely, the save
folder put back exactly (the three autosave files the game wrote on the way are kept aside in `Saves.desk-made`).
`[verified-live 2026-11-12, n=8 rungs, one run each]`

| rung | add-ons | world drawn | follows the head, nothing pressed | pause panel | through the door | walks outside |
| --- | --- | --- | --- | --- | --- | --- |
| 1 vr base | 22 | YES 12.84 | YES 7.42 | YES 21.17 | YES 69.86 | YES 54.70 |
| 2 fixes | 46 | YES 12.88 | YES 7.42 | YES 21.26 | YES 69.83 | YES 54.69 |
| 3 world | 50 | YES 14.47 | YES 7.48 | YES 22.82 | YES 51.32 | YES 38.74 |
| 4 gameplay | 50 | YES 14.51 | YES 7.46 | YES 22.84 | YES 51.41 | YES 38.92 |
| 5 interface | 56 | YES 14.49 | YES 7.48 | YES 14.45 | YES 51.41 | YES 38.96 |
| 6 armor and people | 56 | YES 14.43 | YES 7.69 | YES 14.41 | YES 50.74 | YES 38.98 |
| 7 weapons | 56 | YES 14.42 | YES 7.70 | YES 14.43 | YES 50.75 | YES 39.07 |
| 8 animations and the rest | 58 | YES 14.67 | YES 7.67 | YES 15.58 | YES 50.80 | YES 38.74 |

- **How the door is used:** the save stands inside Springvale Elementary School beside its double door (on the left,
  90 degrees). Both pretend hands point at it for 2 s, then A is HELD on the right hand for 1 s (a tap only shows the
  prompt; a press that arrives together with the hand's move is aimed at nothing: that is how the first pass of all
  eight failed, a fault of the script, not of the rungs). The Capital Wasteland loads in about 10 s. The walk stick
  and the turn stick work. `[verified-live, n=9 door uses]`
- Looked at by eye: rung 1 (four directions outside, after walking) and rung 8 (inside, outside, after walking). The
  schoolyard, the ruined houses, the canopy, the player's arms; from rung 3 on the sky and ground are the world
  mods' own. Nothing missing, nothing pink. `[verified-live, n=2 rungs looked at]`
- **One flaw seen, cause not looked at:** a dark band down the left and the right edge of each eye picture in the
  simulator (about 7% and 10% of the width), inside and outside, every rung. `[measured]` Could be the simulator's
  4096 cap against the 4864-wide upscaled eye, or the mod's own lens-edge mask; not established, and it says nothing
  about the headset.
- One start in seventeen today died 5 s in (rung 5, first pass: an error in the C runtime, Windows event kept in
  `runs/2026-11-12 0919 ...`); the same rung passed twice afterwards. `[measured, n=1]`
- "Hang warnings 1" on rungs 1 and 2 of the outside pass: the mod's own watchdog during the door's load; no dump
  was looked at.
- Rung 8 alone still carries the mod's camera complaint about the skeleton; no harm visible standing or walking.
