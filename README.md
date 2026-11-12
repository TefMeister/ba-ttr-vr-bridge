# Begin Again Tale of Two Realities VR Bridge (`ba-ttr-vr-bridge`)

Named by Tefa 2026-11-09.

Goal (Tefa, 2026-11-09): run the **Begin Again** Wabbajack modlist for Tale of Two Wastelands with **TTWVR / Tale of Two
Realities** by KUPOkinz, a full VR conversion of Fallout 3 + New Vegas as one xNVSE plugin. Tefa's words: "i fully
expect this to fail miserably today, but maybe not in a few months". Parked until TTWVR is in hand.

## How we work: middlemen only (Tefa 2026-11-09)

*"strictly we will only be the middlemen for making Begin Again work in the VR mod and we have to make it sustainable
somehow. we'll figure it out or fail spectacularily"*

**Changed 2026-11-12 (Tefa's decision):** the bridge is built for one pair of versions and stays on it:
**TTWVR 1.0.0** (the DLL of 2026-11-08) and **Begin Again V6.1.0**. No newer TTWVR is taken in. Under KUPOkinz's
permission (below), TTWVR may now be changed by us where that is what makes Begin Again work in VR. What a new Begin
Again release means for the bridge is decided when one comes.

- Begin Again's own files are never edited.
- Whatever we change, in the list or in TTWVR, lives in our own MO2 mods placed on top; the originals stay in place,
  so every change can be seen and taken out again.
- Every step is written as a recipe a script can repeat.
- A conflict report (which files TTWVR and the list both supply, and who wins) is kept current.
- We do not take our modding questions or faults to KUPOkinz or to the list's author.
- Credit: TTWVR is KUPOkinz's work; Begin Again is Spring Heel John's; TTW is the TTW team's. Their support channels are not
  ours to fill with our problems.

## Where it is going, and what we may do (Tefa 2026-11-11)

- **The goal: Begin Again in VR, 1:1.** The whole list as its author built it, playable in TTWVR.
- **Maybe, on the way, some of our own:** hand poses, how guns are held, and the like. Since 2026-11-12 these may
  also be changes to TTWVR itself (see above), always as our own mod on top of the untouched original.
- **KUPOkinz's permission** `[reported]` (Tefa, from KUPOkinz's public Discord thread; the message itself is not yet
  saved here): anyone may do anything with the mod as long as nobody posts it as their own work. So: every file,
  page and note that builds on TTWVR says it is KUPOkinz's work, first and plainly.
- **Versions (2026-11-12):** TTWVR is fixed at 1.0.0; Begin Again at V6.1.0 until its author releases a new one,
  and then it is decided afresh. (Before this date the plan was to follow both as they updated.)


## Where it stands (2026-11-09)

- Begin Again V6.1.0 installed by Wabbajack (CLI, Nexus Premium) to `C:\Modlists\Begin Again`, downloads on D. 874
  archives, no errors, 23 minutes.
- TTW 3.4 installing into the list's `[NoDelete] TTW 3.4` mod (started by Tefa through the installer's Browse field).
- Fallout 3's launcher crashes on the RTX 5080 (Windows error log: Fallout3Launcher.exe 0xc0000005); its INIs were made
  from `Fallout_default.ini` + `VeryHigh.ini` at 3440x1440. New Vegas's launcher worked.
- TTWVR 1.0.0 (`TTWVR.zip`, 325 MB, from the pinned message of KUPOkinz's Discord thread on the Flat2VR server) is
  downloaded, not installed. An MO2 archive (meta.ini): `NVSE/Plugins/TTWVR.dll` (2026-11-08), its own
  `ttwvr_dxvk_d3d9.dll`, `openvr_api.dll` (SteamVR), DLSS and FSR DLLs, a `TTWVR.ini` (165 %, DLSS Performance, full
  body, HUD off), and 1,040 files in all: ~520 resized armor meshes, weapon meshes, `meshes/characters/_male`, wound
  textures. Those meshes must win over Begin Again's armor, body and weapon replacers.

## What TTWVR asks for, against what Begin Again has

| TTWVR needs | Begin Again |
| --- | --- |
| xNVSE, JIP LN NVSE, lStewieAl's Tweaks | included |
| lStewieAl's Engine Optimizations, the 4GB patch | to check |
| "no additional mods" until it runs; mods touching the player model, Pip-Boy model or player animations "may break" it | many: 3rd Person Animation Fixpack, kNVSE weapon animations, Dri / P6 weapon replacers, Consistent Pip-Boy Icons ... |
| custom weapons only work when their NIFs follow TTWVR's node rules | the list replaces many weapon meshes |
| launched under Virtual Desktop (VDXR) with forward tracking data on, or SteamVR | MO2 launch only (Root Builder) |

The likely route: first TTWVR on the list's **Debug Mode** profile (TTW and its required mods only), then add Begin
Again's groups back one at a time, weapons and animations last.

## Files

- `NOTEBOOK.md`: the dated log of everything done and what came of it.
- `FAULTS.md`: the fault ledger, in the order faults must be sorted, and questions only a mod's author can answer.
- `tools/ladder.py`: builds each test rung as an MO2 profile and checks its masters before a launch.
- `tools/collect_run.py`: keeps every log a launch wrote (scrubbed), in `runs/`.
- `docs/rung-00-plan.md`: the first launch, what we expect and what each failure would mean.
- `external-research/README.md`: where the outside facts come from (links), and what we take from them.
- `tools/conflict_report.py`, `reports/`: which files TTWVR and the list both supply, and who wins.
