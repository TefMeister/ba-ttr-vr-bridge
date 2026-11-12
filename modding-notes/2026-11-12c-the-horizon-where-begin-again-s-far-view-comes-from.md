# The horizon: where Begin Again's far view comes from, and what TTWVR does to it (2026-11-12 late, /pd, no game)

Tefa asked: in Begin Again (flat) everything on the horizon is visible; can we have that in VR?
**The game was not launched, and nothing here has been run.** Everything below is read from the
profiles, the mods folder and TTWVR.dll (build 6AF014A8) on disk.

## The answer in one line

Begin Again's horizon is **22 LOD mods plus its own generated LOD (3.8 GB)**, and the ladder only
switches the generated part on at **rung 8b**. Rungs 1 and 2 have none of it; rungs 3 to 8a have the
22 mods but not the generated part. So nothing worn or desk-checked below 8b can show Begin Again's
horizon, VR or flat. `[measured 2026-11-12]` (profile files compared)

## What was compared

| profile | the 22 LOD mods (`modlist.txt`) | LOD plugins active (`plugins.txt`) |
| --- | --- | --- |
| Begin Again | on | 8, incl. `Begin Again Terrain LOD.esp`, `Begin Again Object LOD.esp` |
| rung-01 vr base | 0 | 0 |
| rung-02 fixes | 2 | 0 |
| rung-03 world .. rung-08a | 22 (the two Begin Again LOD folders still **off**) | 6, without the two Begin Again ones |
| rung-08b late loaders, 08c | on | 8, same as Begin Again |

`Begin Again Object LOD` (2.9 GB, three BSAs) and `Begin Again Terrain LOD` (867 MB, one BSA) are
each a 1 KB plugin whose only master is `FalloutNV.esm`; the plugin is there to load the same-named
archives. Off = their archives are not loaded at all. They sit under Begin Again's
`OPTIONAL MODS` separator, which is why the ladder put them in rung 8. `[measured]`
Because their only master is `FalloutNV.esm`, nothing stops them being switched on in any lower
rung. `[inferred-static]` (masters read from the TES4 header)

## The settings files are not the cause

- Every rung's `falloutprefs.ini` is the same file (`ladder.py --inis vanilla` copies it from
  Documents), not Begin Again's own 146-line one. For the far view the differences are small:
  `fBlockLoadDistance` 125000 vs 130000, `fBlockLoadDistanceLow` 50000 vs 30000; both profiles'
  `falloutcustom.ini` say 130000 / 30000. `[measured]`
- The `[LOD] bDisplayLODBuildings=0` line followed later by `=1` looked like a suspect, but Begin
  Again's own `fallout.ini` has the same pair (it is the stock file's), and flat Begin Again shows the
  horizon with it. `[measured]` Dropped.

## What TTWVR does to the far view

1. **It writes its own graphics preset into the game** (a table in `.rdata` near 0x10907E80: game
   setting address, value, label). The far-view entries: object / actor / item fade 15, grass fade
   11200, `fTreeLoadDistance` 40000, `fBlockLoadDistanceLow` 50000, `fSplitDistanceMult` 1.5. These
   match or beat Begin Again's own values (15, 15, 15, 11200, 40000, 30000, 1.5).
   **It does not touch `fBlockLoadDistance`** (the farthest LOD ring). So the preset does not shorten
   the horizon. `[inferred-static]` (table read; whether every entry is applied at run time not seen)
2. **It has built-in culling switches, all on:** `[Cull] bOcclusionCull, bGridSleep, bSidesNoGrid,
   bFogCull, bAllCells` = 1 (defaults table at 0x10743E40). `bFogCull` is the one that could matter:
   if it drops whatever stands inside the fog, a far LOD skyline in clear weather should be
   untouched, but a hazy weather could thin it. Not read further. `[inferred-static]` for the
   defaults; what each one does `[hypothesis]`.
3. **These switches cannot be changed from `TTWVR.ini`.** The loader (0x10091FC0) only maps 13
   keys to `[VR]` in the file (Resolution, Upscaler, Upscaler Level, Sharpness, Full Body, VR Scenes,
   Turning, UI Scale, UI Opacity, Experimental Gore, HUD, Spectator View, Voice); everything else comes
   from the built-in table. Changing `bFogCull` would mean a one-byte data patch of our own copy of
   TTWVR.dll (allowed since Tefa's decision of 2026-11-12). `[inferred-static]`
4. Begin Again also ships `FogCulling.dll` (an NVSE plugin, loaded in all 54 kept runs). Flat Begin
   Again shows the horizon with it, so on its own it is not the cause. `[measured]` (logs)

## What is NOT established

- Whether VR (rung 8b/8c) shows the same horizon as flat. Nobody has looked yet.
- Whether a 32-bit game with TTWVR in VR has the memory for 3.8 GB of LOD archives on top (TTWVR
  logs "the game's address space is nearly full" when it runs short; watch for it in the log).

## The test that decides it (FLAT desk run, or Tefa in the headset)

Rung **8c** (= the whole list) flat and sim, same save, outside the school door, the view turned to
the far skyline (the Washington Monument direction). Two stills, side by side:

- Same skyline in both: the horizon works in VR; nothing to build, it simply arrives at rung 8b.
- VR clearly shorter or thinner: TTWVR's own culling. Next step `bFogCull` off in our copy of the
  DLL (a `MODEL: FABLE` read of what it does first).
- VR fine but the game stalls or the log says the address space is nearly full: memory, a separate job.

If Tefa wants the horizon sooner on the ladder: switch the two Begin Again LOD folders and their
plugins on from rung 3 (their only master is `FalloutNV.esm`). Not done: it changes rungs that are
already desk-checked, and it is Tefa's call.
