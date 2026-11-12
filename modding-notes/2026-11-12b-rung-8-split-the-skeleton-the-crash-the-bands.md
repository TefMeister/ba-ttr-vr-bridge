# 2026-11-12 (afternoon): rung 8 split, the skeleton complaint's two mods, the rung-5 crash, the dark bands

Developer PC, Opus, nobody in the headset; every run in the OpenXR Simulator with the VR Bench hands.

## The rung-5 crash of 09:19 (one start in seventeen) `[measured]` from its logs

- Windows: FalloutNV.exe, `ucrtbase.dll` fail-fast (c0000409) after the crash logger caught an access violation.
- Crash logger (`runs/2026-11-12 0919 rung-05 interface sim/overwrite__Root__CrashLogger.log`): main thread, top frame
  `nvse_stewie_tweaks IsOverencumberedAddGrabbedWeightHook+0xE` (Stewie's Tweaks `main.h:4356`), eax = ecx = 0 (an empty
  object), the player as the actor; called from the game's encumbrance check, which was called from TTWVR's own frame
  code (`NVSEPlugin_Load+0xC8818` ...), during the load.
- The setting behind that hook: Begin Again's `nvse_stewie_tweaks.ini` has `bEncumbranceIncludesGrabbedItems = 1` (the
  item you carry by hand counts toward your weight). `[inferred]`: TTWVR asked about encumbrance before the grab data
  existed.
- Ready fix, NOT applied (one crash in seventeen; it changes play a little): a bridge settings file
  `NVSE/Plugins/Tweaks/INIs/zzBridgeFixes.ini` with `bEncumbranceIncludesGrabbedItems = 0`, in a bridge MO2 mod on in
  every rung. Apply if the same top frame comes back.

## Rung 8 split (`tools/ladder_groups.py`, `--only` added)

| rung | adds | mods / plugins | simulator, inside and outside |
| --- | --- | --- | --- |
| 08a skeleton and animation | SKELETON & ANIMATION | 615 / 198 | all YES; the camera complaint |
| 08b late loaders | LATE LOADERS | 620 / 201 | all YES; the camera complaint |
| 08c optional mods | OPTIONAL MODS | 621 / 202 | all YES; the camera complaint (= the old rung 8, mods and plugins identical) |

`[verified-live 2026-11-12, simulator, n=1 each]`. The old `rung-08 animations and the rest` profiles are untouched.

## The camera complaint ("Camera1st's parents are not Bip01 Looking / NonAccum / Bip01 in this skeleton")

Side rungs (not carried forward): 08a-x without `NVCS Vanilla Weights`: complaint stays. 08a-y without `Enhanced
Movement`: stays. 08a-z without both: GONE. `[verified-live 2026-11-12, simulator, n=1 each]`. The skeleton group's only
two first-person skeletons are NVCS's `_1stPerson/Skeleton.nif` and Enhanced Movement's `skeletonEM.nif` (it swaps that
in while playing); each alone is enough to make TTWVR find no Bip01 chain above Camera1st. What the complaint costs in the
headset is not known yet (the camera may sit off the head). Next: a bridge skeleton (either mod's skeleton with the chain
TTWVR expects), or the rungs without them; Tefa's look at 08a in the headset first.

## The dark bands at the edges of each eye (simulator only, so far)

- Measured on the kept stills: pure black (0), left 6.5-7.1 %, right 9.8-10.2 % of the eye's width, every rung.
- At Resolution 100% (TTWVR.ini, that one run, put back to 165% after): the SAME bands (6.9 % / 10.0 %). The simulator's
  4096 size cap is NOT the cause. `[verified-live 2026-11-12, n=1]`
- What the mod submits (the simulator's projection log, live): per eye 4096 x 3648, left eye angles left -1.0727 /
  right 0.9156 / up 0.7676 / down -0.9472 rad (right eye mirrored), while the simulator's views are left -0.942 / right
  0.698 / up 0.768 / down -0.947. So TTWVR draws and declares a WIDER side-to-side view (61.5 / 52.5 degrees) than the
  runtime gave it (54 / 40); up and down match. `[measured]`. Why, and how that turns into black edges in the preview,
  is not worked out (the mod's own projection: `MODEL: FABLE`). Whether the real headset shows anything: ask Tefa.

## Tool fix

`rung_simcheck.py` switches the VR Bench hands on itself: four runs said "pause panel shows NO" on rungs that answer,
because another session had switched VR Bench off (the pause press and the walk silently did nothing). Rung 7 control
then: pause YES.
