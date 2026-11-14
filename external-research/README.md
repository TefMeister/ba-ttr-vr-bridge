# Where the outside facts come from

This folder is the project's public research, curated only by the `/gr` research session; everyone else reads it
and hands verdicts or leads over as new files in [`inbox/`](inbox/). The front door is [INDEX.md](INDEX.md), every
source is in [CREDITS.md](CREDITS.md), write-ups live in [`topics/`](topics/).

We only link to these; the words belong to their authors.

| What | Who | Where |
| --- | --- | --- |
| **TTWVR / Tale of Two Realities** (the VR conversion, one xNVSE plugin) | KUPOkinz | The pinned message of KUPOkinz's thread on the [Flat2VR Discord](https://discord.com/channels/747967102895390741/1560413111423344730) (download, controls, install steps) |
| **Begin Again** (the Wabbajack modlist for TTW) | its author, on Nexus | Wabbajack gallery, machine name `Beginagain/beginagain`; the install guide on its Nexus page |
| **Tale of Two Wastelands** | the TTW team | [taleoftwowastelands.com](https://taleoftwowastelands.com) |
| **The Best of Times** (the TTW setup guide TTWVR's install steps point to) | moddinglinked | [thebestoftimes.moddinglinked.com](https://thebestoftimes.moddinglinked.com/ttw.html) |

## What we take from them, in our words

- TTWVR wants: xNVSE, JIP LN NVSE, lStewieAl's Tweaks and Engine Fixes, lStewieAl's Engine Optimizations, the 4GB
  patch, TTW set up by The Best of Times guide **without** its optional performance section, and at first **no other
  mods**: mods touching the player model, the Pip-Boy model or player animations may break it.
- It is started from MO2 with Virtual Desktop (VDXR, forward tracking data on) or SteamVR already running; height and
  arms are calibrated in game by holding both arms straight out and both triggers.
- Weapons: TTWVR reads conventions from each weapon's NIF (a `ProjectileNode` at the muzzle, a lens shape named
  `ScopeLens`, reloadable parts as separate `##` nodes named as the reload animation animates them, the grip at the
  mesh origin). A replacement weapon that does not follow them misses the VR handling.
- Begin Again: install TTW 3.4 into the empty `[NoDelete] TTW 3.4` mod; always start through MO2; its "Debug Mode"
  profile is TTW and the mods TTW needs only.
