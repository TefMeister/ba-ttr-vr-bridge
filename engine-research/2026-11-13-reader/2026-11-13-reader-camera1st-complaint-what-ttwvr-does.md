# 2026-11-13 reader: the "Camera1st's parents" complaint: what TTWVR does, what a player would feel, what fixes it

From: the static reader (read-only; disassembled a scratch copy of `TTWVR.dll` build 6AF014A8; parsed copies of
the two skeletons). For: the modding lane, board row "THE CAMERA COMPLAINT ON RUNG 8".

## The check `[measured]` (function 0x1032ED60)

- Each frame (when the player and its 1st-person root exist) TTWVR finds the node **`Camera1st`** in the
  1st-person skeleton. It then compares the names of its parent, grandparent and great-grandparent, **exactly**
  (byte-for-byte compare):
  - `Camera1st`'s parent must be **`Bip01 Looking`**;
  - its parent must be **`Bip01 NonAccum`**;
  - its parent must be **`Bip01`**.
- If any one differs, the complaint is logged **once per session** and the frame goes the short way.
- The rest pose it holds `Camera1st` at is local (0, -3.741, 0) (a constant in the code).

## What changes when the chain is missing `[measured]` paths; meaning `[inferred]`

- **Chain present:**
  - TTWVR also reads `Bip01 NonAccum`'s animated position, with its downward part clamped to 0..-40 units (a
    crouch-sized drop) and tracked against a first reference;
  - it reads `Bip01 Looking`'s rotation;
  - it composes `Camera1st`'s local transform from them, so the camera sits at rest relative to `Bip01`. That
    cancels what the animations do to those two parents.
- **Chain missing:** only `Camera1st`'s own local transform is reset to rest. Whatever the animations do to its
  parents passes straight through to the camera. That means the `NonAccum` crouch/bob offsets and the `Looking`
  pitch, and in Enhanced Movement's skeleton also its three lean nodes.
- Both paths then write `Camera1st`'s local and world transforms the same way. Nothing else is switched off in this
  function (no crouch, height or body feature is disabled here).

**What a player would likely feel on rung 8a `[hypothesis]`**, assuming the VR view hangs off `Camera1st` (it is
the node TTWVR holds):
- the view **moves on its own** with the 1st-person animations: bob when walking or sprinting, sway, a dip or lift
  around crouch and stand;
- with Enhanced Movement, **a tilt or roll** from its camera-lean nodes (its sprint tilt is on in Begin Again);
- most likely only slight, but a roll is the kind of thing that makes people sick;
- standing still with no animation running: probably nothing.

Points to watch when Tefa wears 08a:
- sprint, then stop;
- crouch and stand;
- strafe while sprinting;
- does the horizon roll or the view bounce?

## The two skeletons' real chains `[measured]` (parsed NIF hierarchy, not just a name search)

- `NVCS Vanilla Weights` `_1stPerson/Skeleton.nif`:
  `Camera1st <- Bip01 Looking <- Bip01 NonAccum <- NAccController <- Bip01 <- Scene Root`.
  All names are present. **One extra node, `NAccController`, sits between `NonAccum` and `Bip01`**, so the third
  test fails.
- `Enhanced Movement` `skeletonEM.nif`: `Camera1st <- EMLeanCameraCOffset1P <- EMLeanCameraController1P <-
  EMLeanCameraPOffset1P <- Bip01 Looking <- Bip01 NonAccumFix <- Bip01 NonAccumFix2 <- NAccController <- Bip01`.
  There are three lean nodes above the camera, and `NonAccum` is renamed `...Fix`, so the first test already fails.
- The check runs on the **live** scene graph. Enhanced Movement swaps its skeleton in during play, so what counts is
  what is loaded at the moment `[inferred]`.

## What a bridge fix would look like `[inferred]`

- **A bridge skeleton** has to give, by exact name: `Bip01` → `Bip01 NonAccum` → `Bip01 Looking` → `Camera1st`
  (each the direct child of the one before).
  - For NVCS: re-parent `Bip01 NonAccum` straight under `Bip01` and drop or move `NAccController`. Its purpose for
    NVCS animations is unknown; it may be needed, so that is a risk.
  - For Enhanced Movement: remove its lean nodes and restore the `NonAccum` name. That takes away its camera lean
    and sprint tilt, which is probably wanted in VR anyway.
- **Or our TTWVR copy:** relax the check (walk up skipping unknown nodes, accept `Bip01 NonAccum*`) and cancel the
  extra nodes too. That keeps both mods' skeletons. It is the larger change and needs `MODEL: FABLE` for the
  maths.
- **The cheapest test first:** the headset look at 08a above. If nothing is felt, nothing needs building.

## `[Debug] sDebugLoadSave`: yes, it takes a save name `[measured]`

- It is a string setting.
- When non-empty, **once per session and at least 15 s after start-up**, TTWVR runs the console line
  **`load "<value>"`** through xNVSE's console interface. The value is a save file name, as typed after `load`.
- So `sDebugLoadSave=<save name>` under `[Debug]` would load a named save by itself. That it is read from
  `TTWVR.ini` is `[inferred]` (see the command-file note).
- The desk runs already have our own MO2 auto-load mod; this would be an alternative that needs no extra plugin.
  It must stay out of the played profiles' INI.
