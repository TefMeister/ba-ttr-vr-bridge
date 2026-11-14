# FNVVR Reborn: a second New Vegas VR mod, whose public release notes already name our far-view, water and Stewie's Tweaks faults

**Status:** 🆕 new · **Priority:** high. Three open rows on the board (2026-11-13) are stereo faults of the drawing in
TTWVR: the far view "swims" against the near world with head sway, the far water is drawn as a flat green or olive
sheet over nearer land, and things blink. TTWVR's own notes are on Discord only. A second, independent New Vegas VR
mod publishes detailed release notes on GitHub, and several of its fixes describe the same symptoms.

## What it is

**FNVVR Reborn** by **df4l**: a VR mod for Fallout: New Vegas built into a fork of DXVK (a 32-bit `d3d9.dll`), so it
works at the Direct3D 9 call level rather than as an xNVSE plugin like TTWVR. OpenVR (SteamVR) only so far; an OpenXR
backend is listed as "not done yet". Seventeen public pre-releases since 2026-10-07, the newest v0.17.0 on
2026-11-13, tested by its author on Linux/Proton with a Quest 2 `[reported 2026-11-14]`. It is not built on TTW and
says nothing about Begin Again. We do not use it; this is a reference for what New Vegas does in stereo.

Read online on 2026-11-14 through the repository's release viewer and API (all 17 release notes). Nothing was
downloaded. All `[reported]` unless marked.

## What its release notes say, in our words

- **The sky (v0.2.0):** "the sky dome is centred on each eye", after which the clouds stopped moving against the
  head and stopped looking like a low ceiling; the sun glare likewise made to face each eye instead of rolling with
  the head. Read: the game places its sky (and sun) around ONE camera point; drawn twice for two eyes without moving
  that centre, the sky sits at a finite distance and slides with head movement.
- **Distant water (v0.10.0):** "no longer turns grey and flat at the sides of your view".
- **Water reflections (v0.5.0):** square shapes on the water, and cut or square shadows in the right eye, came from
  one picture being shared between the two eyes (the water reflection, the shadow maps); fixed by giving each eye
  its own reflection and drawing the shadow maps once per frame for both.
- **Settings it forces in VR (v0.12.0):** the Viva New Vegas guide's values, starting with NO full-scene water
  reflections; actor shadows later turned off too (v0.16.0) for cost.
- **Leaves (v0.16.0):** tree and bush leaves "no longer turn and roll with your head" (the game turns them to face
  the camera).
- **lStewieAl's Tweaks (every release since at least v0.14.0, "Known issues"):** keep
  `bSmoothIronsightsCameraTransition`, `bScopeVisibilityDelay` and `bAlwaysShowWeaponAnimation` OFF in VR.
- **Other mods it was checked with (v0.13.0):** xNVSE, JIP LN, JohnnyGuitar, kNVSE, lStewieAl's Tweaks, NVTF, ShowOff,
  yUI, CrashLogger, UI Organizer, ITR, hNVSE, ROOGNVSE, Shader Loader, Alpha Rendering Tweaks, HighResWaterDepth and
  more; **LOD Flicker Fix** needed special handling (v0.14.0): menus with a 3D scene, scope lenses and the console
  terminal were drawn black or square with it until fixed. NVAC is not supported.
- **JohnnyGuitar's script-drawn camera overlays** do not work in VR (hidden or drawn flat), and HUD parts added through
  UI Organizer stay at their flat-screen place.

## What it means for us

- **The far view swims (Tefa, rung 5):** the skyline band slid 2-6 px a frame with head sway while the middle
  distance held still. The same family as FNVVR's sky before v0.2.0: something far drawn around one shared camera
  point instead of each eye's own `[hypothesis]`. What separates it: in the simulator, move the pretend head
  sideways only (no turn) and watch the sky/clouds against the far LOD buildings against the near ground; if the
  sky and the far band move WITH the head and the near world does not, it is a one-centre placement (sky dome,
  or the far LOD drawn in a separate pass with its own camera), not a depth or resolution fault.
- **The water:** FNVVR met water turning grey and flat at the sides of the view and square shapes from a reflection
  shared between the eyes. Ours is a flat green / olive sheet drawn OVER nearer land. Not the same symptom; but it
  confirms that New Vegas water needs per-eye care in stereo and that turning full-scene reflections off is the
  accepted VR setting `[reported]`. Our own console test (`tws` hides the sheet) already points at the water's
  depth test rather than its colour.
- **Begin Again's Stewie's Tweaks INI:** check the three settings FNVVR says to keep off; they act on the camera and
  the weapon view, and the camera complaint on rung 8 is open. Whether TTWVR needs them off too is unknown
  `[hypothesis]`.
- **Begin Again carries LOD Flicker Fix?** If so, FNVVR's experience (3D menus, scope lenses, terminals drawn wrong
  with it) makes it a suspect for the blinking `[hypothesis]`; check the modlist first.
- Under the board's decision of 2026-11-12, none of this is raised with TTWVR's author; it only guides our own reading
  of TTWVR's drawing.

## Sources

- df4l, FNVVR Reborn (repository and release notes v0.1.0 to v0.17.0): https://github.com/df4l/FNVVR and
  https://github.com/df4l/FNVVR/releases
