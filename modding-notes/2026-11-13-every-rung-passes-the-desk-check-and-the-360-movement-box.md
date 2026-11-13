# 2026-11-13: every rung passes the desk check; the 360 Movement box; what each rung adds

Developer PC, /lm, Opus, Tefa away (watching the screen part of the time). OpenXR Simulator + VR Bench hands, nobody
in the headset.

## 1. The desk check had been loading the wrong save

`rung_simcheck.py` lets Stewie's Tweaks auto-load the NEWEST save. Since Tefa's rung-3 headset run (2026-11-13 00:1x)
the newest is Tefa's own `Autosave - 3` (outdoors, made with rung 3's far-view plugins). So the first pass of today
judged rungs 4-8c from that spot (pause press and walk both "NO"; the door step activated a vault door into a level-up
screen), and rung 1 stopped at "This save relies on content that is no longer present" (Tefa's screenshot)
`[verified-live 2026-11-13, n=8]`. **Fixed:** new `--save` (default: the rung-1 Springvale Elementary School save);
it is made newest for the run and its date is put back afterwards; the save folder is now copied and put back on
every run, not only with `--outside`. The pause panel is kept as `eye pause panel.jpg`, and the mod's camera
complaint is printed as its own yes / no.

## 2. Results on the school save (with the far-view pack on from rung 3)

| Rung | Start + load | World / head | Pause | Door + walk | Crash logs | Camera complaint |
| --- | --- | --- | --- | --- | --- | --- |
| 01 vr base | yes, 15 s | yes / yes | yes | yes / yes | 0 | no |
| 04 gameplay | yes, 18 s | yes / yes | yes | yes / yes | 0 | no |
| 05 interface | 1st try: crashed at start (ucrtbase 0xc0000409, as on 2026-11-12); 2nd: yes, 22 s | yes / yes | yes | yes / yes | 0 | no |
| 06 armor and people | yes, 20 s | yes / yes | yes | yes / yes | 0 | no |
| 07 weapons | yes, 24 s | yes / yes | yes | yes / yes | 0 | no |
| 08a / 08b / 08c | yes, 24 s | yes / yes | yes | yes / yes | 0 | YES |

`[verified-live 2026-11-13, n=1 each; rung 5 n=2 with one start crash]`. No stall from the 3.8 GB far-view pack on any
rung. Rung 5's pause panel is the full TTW pause menu (MAPMO), larger and clearer than rung 4's: nothing wrong
`[measured, still]`.

The rung-5 start crash left Steam's `x64launcher.exe` (the overlay starter) running with no window; Mod Organizer
waits for it and the next run never starts. It can only be ended with `/F` (harmless: its game is gone). Not yet
handled by the tool.

## 3. ⭐ The 360 Movement box (rungs 8a-8c), found by Tefa on the screen

"NV Compatibility Skeleton v12+ is required for 360 Movement!" pops up, many times, just before the game closes, and
also inside the VR view `[reported by Tefa; seen in the eye stills]`. The desk check never saw it: it judges picture
changes and logs, not boxes.

Cause `[measured]`: 360 Movement's start-up script tests `ModelHasBlock Player "360Corr0"` (only while
`IsPC1stPerson == 0`). The `360Corr0` node is in NVCS Vanilla Weights' third-person `_Male/Skeleton.nif`; TTWVR 1.0.0
ships its own `_male/skeleton.nif` and sits at the top of MO2's order, so TTWVR's skeleton wins and the node is gone.
TTWVR's skeleton also lacks NVCS's `B42Quiver`, `Bip01 Weapon2`, `Bip01 WeaponBow`, the `* Grab` nodes and others
that rung-8 mods (B42 Interact / Inject / Quiver, holstered side arms) may look for `[measured: node-name strings]`.
So rung 8's skeleton story has two halves: the first-person chain (the camera complaint) and this third-person one.

While a box is up the eye pictures smear and stay smeared, even with the head still `[measured, n=1]`; probably the
box puts the game in menu mode and the picture stops keeping up with the head `[hypothesis]`.

Options for Tefa (not done): (a) 360 Movement off in the VR profiles: it is a third-person movement mod
`[inferred]`; (b) NVCS's third-person skeleton above TTWVR's: risks whatever TTWVR's body needs `[hypothesis]`;
(c) a bridge skeleton: TTWVR's plus NVCS's extra nodes, our own MO2 mod. Read first what TTWVR's skeleton adds.

## 4. The horizon, first try (rung 8c, simulator only)

Route: `player.moveto SpringvaleElementaryMapMarker` typed into the console worked; `player.setangle z 121` did not
visibly turn the VR view `[n=1]`. The 360 Movement box then smeared every picture, so no skyline judgement.
**Keyboard into a simulator run:** the simulator reads W/A/S/D/Q/E/I/J/K/L and its own view keys from the keyboard
while the game's window is in front (`input_polling: app`), so typing moved the pretend head and changed the
preview (fixed back; settings backed up `settings.json.bak-2026-11-13-after-typing-slip`). With `input_polling:
preview` for the run it is clean. The tool is `tools/console_type.py`. TTWVR's command file `NVVR-cmd.txt` was NOT read
by the game (written twice, never taken) `[measured, n=2]`, though the DLL has the code for it. Next try: rung 7 (no box),
or 8c after the box is dealt with; dismiss any box with A first.

## 5. The reader's five notes (static, `engine-research/2026-11-13-reader/`)

- What each rung adds and what to watch in the headset (rung 4: True Leaning tilts the view, Animated Moments camera
  shots; rung 5: fonts fixed, FOV mod, Pip-Boy menus, screen overlays; rung 7: about 40 first-person weapon
  replacers; rung 8a: weapon inertia, B42 Recoil radial blur and double vision (a screen effect: goes off in VR),
  camera bob and lean; 8c: aim assist).
- TTWVR's gun data (`TTWVR.dat`) is keyed by editor ID, so rung 7's replacers are still found, but every grip,
  magazine and lens number was measured on the vanilla meshes: most guns "partial"; the 10mm SMG's bolt node is
  missing (no cocking).
- The camera complaint: TTWVR then stops cancelling the animations on the camera's parent nodes, so the view
  probably bobs / tilts with walk, sprint, crouch and Enhanced Movement's lean. The exact chains of both skeletons.
- TTWVR's command file and `[Debug] sDebugLoadSave` (loads a named save) `[inferred-static]`.
- The DXVK log: written only on errors, beside `TTWVR.log`; `collect_run.py` already keeps it when it appears (no code
  needed).

## 6. Rung 4 worn (Tefa, Quest 3 through Virtual Desktop, 16:35-16:45)

360 Movement was switched off in all 14 VR rung-8 profiles first (Tefa: option a; flat twins keep it; `ladder_groups.py`
keeps it off on a rebuild; `ladder.py check` clean on 8a / 8b / 8c). Rung 4 started through Virtual Desktop's OpenXR
runtime at 72 Hz, the VR Bench hands switched off before. Logs kept: `runs/2026-11-13 1652 rung-04 gameplay headset/`.

Tefa `[reported]`:
1. **The ammo holster spot moved to the right** of Tefa.
2. **Water is cut in two, two colours:** brown-olive near, dark green farther out, with a hard edge (screenshot).
3. **The waterline seems to start at the rock Tefa stands on**, while the water is really far lower (seen in the
   distance): the water surface looks drawn over the ground in front of it.
4. **Smearing, a bit worse with both eyes open; things blink in and out of existence even standing still** (three
   Quest clips, `D:\Claude videos to edit\Quest videos\VirtualDesktop.Android-20261113-16{3634,4141,4405}-0.mp4`).

Read from the clips `[measured]`: no repeated frames and no every-other-frame sharp/soft see-saw (1.4-3.4 %), so not
Virtual Desktop filling in frames; a once-every-5-frames bigger step in the moving clip is the 60 fps recording of a
72 Hz display, not the game. One-frame shimmer sits at fixed places on thin grass, shrubs and wreck edges, also with
the head still. The clips are one eye, so "worse with both eyes" (a difference between the eyes) cannot be seen in
them. `[hypothesis]`: the shimmer is the upscaler (Tefa's VR menu: DLSS Performance at 165 %) on thin foliage; the
two-eye smear is something different between the eyes.

Not established: whether the water and the holster are rung 4's or were there from rung 1 (rung 4 adds gameplay mods
only, none touching water or rendering `[inferred-static, reader]`).
