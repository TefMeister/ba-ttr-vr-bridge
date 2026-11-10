# Rungs 2 to 8: Begin Again's own groups back on top of the VR base

**Question each rung answers:** with this much of Begin Again switched back on, does Tale of Two Realities (TTWVR) still
play? The first rung where something breaks names the group to look inside.

Built by `tools/ladder_groups.py` from the list author's own order: nothing is reordered, mods are only switched on.
Each rung is two MO2 profiles:

- `rung-NN <name>`: the groups so far + TTWVR at the very top (it must win every file clash). **For the headset.**
- `rung-NN <name> flat`: the same without TTWVR. A desk check that the list side loads at all (`tools/rung_flatcheck.py`).

The floor of every rung is rung 1's own mod set (the list author's Debug Mode profile), wherever the author filed those
mods: the first try left "Begin Again Configs" off because it sits in a late group, and the game stopped on
"NVTF.ini not found".

| Rung | Adds (the author's groups) | Mods on | Plugins | Why here |
| --- | --- | --- | --- | --- |
| 02 fixes | BUGFIXES & QOL | 83 | 35 | engine fixes: nothing a player sees |
| 03 world | WORLDSPACE EDITS, LOD RESOURCES, WORLDSPACE MESHES & TEXTURES, SOUNDS & MUSIC, WEATHER & LIGHTING, QUESTS & ADVENTURES | 260 | 130 | the world, not the player |
| 04 gameplay | GAMEPLAY, IMMERSION | 320 | 165 | rules and scripts |
| 05 interface | USER INTERFACE | 401 | 172 | menus, HUD, Pip-Boy screens: the first group KUPOkinz's warning touches |
| 06 armor and people | ARMOR, ACTOR APPEARANCE | 485 | 186 | 476 of the 498 file clashes with TTWVR are armor meshes (TTWVR wins them) |
| 07 weapons | WEAPONS | 572 | 193 | weapon meshes TTWVR resizes; 39 mods replace them |
| 08 animations and the rest | SKELETON & ANIMATION, LATE LOADERS, OPTIONAL MODS | 615 | 202 | the player's skeleton and animations: the likeliest to break VR; = the whole list |

No mod had to be left off at any rung for a missing master `[measured 2026-11-10]`.

## Before a launch

`python tools/ladder.py check --mo2 "C:/Modlists/Begin Again" --name "<the rung>"`. Since 2026-11-10 the check also
says, before the game has to: an xNVSE add-on that is on while its settings file sits in a mod that is off, and the
three add-ons TTW 3.4 itself asks for (`ttw_nvse.dll`, ShowOff, JohnnyGuitar). It would have caught all four of the
first evening's failed starts.

## What we expect in the headset `[inferred]`

Rungs 2 to 4 play as rung 1 did. Rung 5 may change the Pip-Boy or the menus TTWVR draws in VR. Rungs 6 and 7 should
look like rung 1 where TTWVR's own meshes win, with Begin Again's looks elsewhere. Rung 8 is the one expected to break
hands, body or weapon handling; if it does, its three groups are split and tried one at a time.

## A desk check with the VR mod on, nobody in the headset (2026-11-10)

`tools/rung_simcheck.py` starts a rung in the OpenXR Simulator (TTWVR accepts it as a headset), loads the newest save
by itself, presses pause with a pretend hand and closes the game. All eight rungs start, load and answer; only rung 8
adds a complaint to the mod's log (the first-person skeleton, from `NVCS Vanilla Weights`). The simulator does not get
the 3D world from the mod (menus only), so this check cannot say what a rung looks like: the headset ladder above
still decides. Detail: `NOTEBOOK.md`, 2026-11-10.
