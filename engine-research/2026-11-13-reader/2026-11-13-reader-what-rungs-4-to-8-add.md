# 2026-11-13 reader: what rungs 4 to 8c add, and what to watch for in the headset

From: the static reader beside the live session (read-only, no game, no MO2 touched). For: the modding lane.

Method: enabled lines (`+name`) of each rung's `modlist.txt` diffed against the rung below; plugins.txt the same; each
added mod's folder scanned for xNVSE DLLs, INIs, `_1stperson` files, menus, skeletons; file clashes against
`TTWVR 1.0.0` (TTWVR sits on top and wins every one); the TTWVR log of each rung's 2026-11-12 simulator run
(`runs/2026-11-12 09xx/14xx ...`) read for the mod's own "does not verify (another mod's patch?)" lines.

## Things true for every rung

- **The rung profiles' own INIs are byte-identical from rung 3 to 8c** (fallout.ini, falloutprefs.ini,
  falloutcustom.ini, initweaks.ini, settings.ini) `[measured]`. Nothing camera-related changes between rungs from the
  profile side. They set `fDefaultWorldFOV=75`, `fDefault1stPersonFOV=65`, `fPipboy1stPersonFOV=50` (falloutcustom.ini)
  and the vanilla font list; rung 3 was worn clean with exactly these.
- Begin Again's Stewie's Tweaks INI (`Begin Again Configs`, on from rung 1) already has `bSmoothCamera = 1`,
  `bSmoothIronsightsCameraTransition = 1` (225 ms), `bEncumbranceIncludesGrabbedItems = 1`. So the rung-8a mod
  "Smooth True Iron Sights Camera" only adds a menu entry; the behaviour was already on `[inferred-static]`.
- **TTWVR's self-checks all pass on every rung in the simulator:** none of its "does not verify (another mod's
  patch?)" lines (HUD placement, HUD visibility, local-map render, conversation list sizing, PlayAnimGroup for manual
  reload, save-load InitItem) appears in any rung's log; the only new line anywhere is rung 8's camera/skeleton one
  `[measured, simulator, n=1 per rung]`.
- No rung from 4 on drops a mod; rung 8a/8b/8c add plugins `360Movement*.esp`, `Diagonal movement.esp`,
  `Enhanced Movement.esp`, `Auto Activate Invisible Doors.esm` / `Begin Again Conflict reolution patch.esp` /
  `AimAssist.esp`.
- Tefa's TTWVR menu has **HUD=Off** (`TTWVR.ini`), so most rung-5 HUD mods will only show where TTWVR draws game UI
  (pause panel, Pip-Boy, menus).

## Rung 4 gameplay: +63 mods, +35 plugins, no xNVSE DLL, no `_1stperson` file

Mostly rules, quests, loot and economy (RAD, Less Tedious TTW, JAM, Follower Formula, WRS, ammo crafting ...).
Watch:
1. **B42 True Leaning (contextual):** tilts the camera (18 degrees, CamLeanAmount 0.33) when aiming next to cover.
   In VR that is a roll of the whole view you did not make: aim a gun beside a door frame or wall `[inferred-static]`.
2. **Animated Moments:** plays short camera animations at set events (vault exit, nuke, flash-bang, explosion
   reaction). The Vault 101 exit is one of them: watch for the view being yanked when leaving the vault
   `[inferred-static]`.
3. B42 Melee Bash / SMAC (melee bash and parry): new melee animation hooks, may not fire from a VR swing
   `[inferred-static]`.
4. Cookable Grenades / Quick Disarm: button-hold mechanics on keys TTWVR may already use `[inferred-static]`.

## Rung 5 interface: +81 mods, +7 plugins; DLLs: `yUI.dll`, `HDPipboy.dll` (High Resolution Screens), `HighResLocalMaps.dll`, `nvse_console_autocomplete.dll`, `EnhancedConsoleAutocomplete.dll`, `race_menu_presets.dll`

The rung that most touches what TTWVR draws. Watch:
1. **Squished menu text should be gone here** (`Vanilla Fonts Revisited` + `Vanilla UI Plus` arrive) `[inferred-static]`.
2. **Enhanced FOV:** Begin Again sets 1st-person FOV 85, viewmodel FOV 65, iron-sight size 0.5 (`EFOV_Config.ini`);
   TTWVR hooks the same camera-FOV setter ("Hook SetCameraFOV" in the DLL). Look at your hands and gun: wrong size,
   swimming, or a zoom when aiming = this mod `[inferred-static]`.
3. **Pip-Boy:** `Vanilla UI Plus` rewrites the Stats/Items/Data menus (TTWVR injects its STATS/ITEMS/DATA tab row into
   their `GLOW_BRANCH`, which VUI+ keeps) plus Pip-Boy UI Tweaks, Holo Panel, Instant Pip-Boy (replaces the
   1st-person Pip-Boy raise animation), High Resolution Screens (a DLL that enlarges the Pip-Boy screen). Check the
   wrist Pip-Boy opens, the tab row is there and not overlapping, the local map draws `[inferred-static]`.
4. **Screen overlays painted on the view:** Sneak Vignette (0.8 alpha when sneaking), Drowning Visuals, Modern Night
   Vision (blur + overlay), PSRO's peripheral depth blur and scope overlays (TTWVR draws its own scope). Crouch, go
   under water, look through a scope: a flat dark frame stuck to your face = one of these `[inferred-static]`.
5. MAPMO replaces the main and pause menus (the pause panel already looks different from rung 5 in the simulator
   stills); Fallout 76 loading menu; WASD Menu Controls (menu keys) `[measured]` for the still change, rest
   `[inferred-static]`.
6. The rung-5 crash of 2026-11-12 (Stewie's grabbed-weight hook, 1 in 17 starts) was on this rung; fix ready, not
   applied `[measured]`.

## Rung 6 armor and people: +84 mods, +14 plugins, no DLL

Mostly textures and NPC/armour meshes; 196 files clash with TTWVR and TTWVR wins them all. Watch:
1. **Vanilla Style Pip-Boy 3000** and **Pip-Boy Glove replacer** ship the exact Pip-Boy arm and left-glove meshes
   TTWVR ships: TTWVR's win, so no change expected; any change to your left arm/Pip-Boy here means the order slipped
   `[inferred-static]`.
2. **Mechanical Power Armor Gloves / Power Armor Reshape / PipBoyOn Node Fixes** replace power-armour hand and body
   meshes TTWVR does not all cover: in power armour, check the hands and where the Pip-Boy sits `[inferred-static]`.
3. Otherwise: looks of people and creatures only; nothing expected in the headset.

## Rung 7 weapons: +87 mods, +7 plugins, no DLL; ~40 mods carry 1st-person weapon meshes and animations

Watch:
1. **Weapons TTWVR did not author:** replacers use new mesh names (e.g. Classic 10mm Pistols `P610mmPistols/...`,
   Gun and Friends' `10mmpistolre/...`). TTWVR pins scope lenses and grips by its own tables ("no lens table: only
   weapons whose mesh names its lens", "hands will hold the relaxed pose"). Check the 10mm: is the grip right, does
   the hand close on it, does the magazine and rack still work? `[hypothesis]` that tables are per mesh.
2. **Scoped guns** (AR Series, AWO Varmint, Plasma Defenders with `B42Optics` configs; LAER): scope picture and
   lens position `[inferred-static]`.
3. Iron-sight configs (`ISControl`, `HPControl` folders in ~15 mods + Begin Again Weapon Configs): sight position
   for flat aiming; may offset the gun in the hand when aiming `[inferred-static]`.
4. Power Fists / EVE / Dog-tag fist: TTWVR's own meshes win those files `[measured]`.

## Rung 8a skeleton and animation: +38 mods, +5 plugins; DLLs `AimTransitionPatch.dll`, `ThirdPersonAimFix.dll`

The one most likely to break hands and view. Watch:
1. **Camera / skeleton:** `NVCS Vanilla Weights` (`_1stPerson/Skeleton.nif`) and `Enhanced Movement`
   (`skeletonEM.nif`) each trigger TTWVR's "Camera1st's parents are not Bip01..." `[verified-live, simulator]`. In the
   headset: does the view sit on your head, or float/lag when you crouch, sprint or lean? (NVCS's 3rd-person
   skeleton loses to TTWVR's.)
2. **Weapon sway and recoil not from your hands:** B42 Weapon Inertia (gun lags behind turns), B42 Recoil
   (`RadialBlur=1`, `DoubleVision=1`: a screen blur and double image on firing). TTWVR has its own recoil and
   camera-shake switches. Fire a few shots, turn fast with a gun out `[inferred-static]`.
3. **Enhanced Movement / Enhanced Locomotion / Diagonal movement / 360 Movement:** 1st-person sprint animations,
   tilting while sprinting, camera bob (`iReduceCameraBobbing = 0`), body leaning up to 50 degrees. Sprint and strafe
   while looking down at your body `[inferred-static]`.
4. **NVAO Guns/Melee (~1,900 1st-person animations), Quick Scope Anims, Vanilla Weapon Scale Fix, kNVSE Fixpack:**
   reload, equip and aim animations; TTWVR's manual reload hooks PlayAnimGroup (still verifies here `[measured]`).
   Reload the 10mm by hand once `[inferred-static]`.
5. B42 Inject / B42 Interact / B42 Loot: animated stimpak use, item pick-up and inspect animations that may play
   on the 1st-person body you are standing in `[inferred-static]`.

## Rung 8b late loaders: +2 mods, +1 plugin

`Begin Again Conflict Resolution Patch` (plugin) and a Pip-Boy icons patch. Plus Begin Again's generated far view
(on since 2026-11-12 from rung 3). Nothing VR-specific expected; first launch may load longer `[inferred-static]`.

## Rung 8c optional mods: +1 mod, +1 plugin

**Soft-Lock Aim-Assist** (`AimAssist.esp`, VerticalThreshold 66, HorizontalThreshold 55, TrackTime 0.3): pulls the
aim toward targets. With aiming from the controller, watch for the shot or the view drifting toward enemies
`[inferred-static]`. Off-switch candidate if anything feels "sticky".

## DXVK log: where it goes

- Begin Again's own `DXVK` mod (Root Builder: `root/d3d9.dll` + `dxvk.conf`) is **off** (`-DXVK`) in every rung
  profile `[measured]`; there is no `dxvk.conf` in the game folder.
- TTWVR loads its own copy (`NVSE/Plugins/TTWVR/ttwvr_dxvk_d3d9.dll`) and sets `DXVK_LOG_LEVEL` (the string next to
  it is `error`), `DXVK_LOG_PATH`, `DXVK_CONFIG` (inline settings such as sampler LOD bias, memory defrag off,
  `hideNvidiaGpu = False`) and `DXVK_DEBUG` itself `[inferred-static]` (DLL strings).
- Its messages say the log is **`FalloutNV_d3d9.log` beside `TTWVR.log`**, i.e. `~/Documents/My Games/FalloutNV/`
  `[inferred-static]`.
- No `FalloutNV_d3d9.log` (or any `*d3d9*.log`) exists today in that folder, the game folder or MO2's overwrite
  `[measured 2026-11-13]`: with the level at `error`, DXVK writes the file only when something goes wrong `[inferred]`.
  `collect_run.py` already walks that folder (its `mygames` root) and keeps every new `.log` there, so it will keep
  `mygames__FalloutNV_d3d9.log` by itself the first time one is written: the board row may need no code, only a
  note `[inferred-static]`.
