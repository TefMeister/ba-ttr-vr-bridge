# 2026-11-13 reader: TTWVR's per-weapon data against the rung-7 replacers of the first guns

From: the static reader beside the live session (read-only; nothing in the game, MO2 or the profiles touched). For: the
modding lane. Follows `2026-11-13-reader-what-rungs-4-to-8-add.md`, rung-7 point 1.

## How TTWVR 1.0.0 knows a gun `[measured]` (unpacked a copy of its data file; the DLL's strings)

- All per-weapon data sits in `NVSE/Plugins/TTWVR/TTWVR.dat`: a plain pack (`TVPK`, 17 files, stored uncompressed
  as name / offset / size). Inside: `handling.txt` (1,880 rows), `grips-pose.txt`, `grips.bin` (24.5 MB),
  `mag-grip.bin` (18 MB), `pistol-zones.txt`, `scopes.txt`, `reload-anim.txt`, `twohand-grip.txt`, plus melee,
  throw and seat tables. Each says it was generated "from the game's own meshes / .kf animations by tools/<x>.py.
  Regenerate it rather than hand-editing it". The tools are not shipped.
- **The key is the weapon's EDITOR ID** (plus the weapon-mod mask 0..7 where the mesh changes with mods, e.g.
  `weap10mmpistol@3`). `scopes.txt` gives the reason: the game names a held weapon's model root
  `Weapon <EditorID> (<FormID>)`, so the plugin reads the ID off the node. **Not the mesh path.**
- **The parts are found by NODE NAMES inside the mesh**, as `handling.txt` names them per weapon: `mag ##Clip`,
  `handle ##Slide` (the part you rack or cock), plus `ProjectileNode` for where shots leave ("no '%s' in this weapon
  mesh; firing from ... ahead of the grip").
- **The NUMBERS were measured on the vanilla meshes and animations:** the gun's size box, where the magazine and
  handle sit and which way the magazine leaves the gun (`handling.txt`); the pistol grip, slide and magazine boxes
  (`pistol-zones.txt`); the scope lens centre, radius and zoom in model-root space (`scopes.txt`); and the
  support-hand grab surface as triangles (`grips.bin`). The hand pose and the weapon's place in the hand come from
  the vanilla `.kf` (`grips-pose.txt`).
- **Two-handed:** the support hand grabs where the `grips.bin` surface says ("no exact weapon surface table:
  support grabbing is disabled"). Pistols get a two-hand grip from the vanilla `1hpaimis.kf` (`twohand-grip.txt`).
  There is also a live reading of the drawn model's surface ("[grip] live weapon surface ... read off the drawn
  model"); I could not tell from strings how far it replaces the table `[inferred-static]`.

**So what happens after a replacer** (a rung-7 script `SetWeaponModel <EditorID> <mask> "<new.nif>"` +
`SetWeapon1stPersonModel`, editor ID unchanged):
- The editor-ID key still matches, so TTWVR does not fall back. It applies the vanilla numbers to a different-shaped
  gun.
- Each named part is found only if the new mesh has a node of that name.

## Per gun (which mesh wins at rung 7; does the data still fit)

Node names: from a byte search of each replacer `.nif` `[measured]`. Who wins: from the scripts and Begin Again's
`GunAndFriends.ini` (in `Begin Again Weapon Configs`, which sits above Gun and Friends) `[measured]`. Which script runs
last when two touch the same gun: `[inferred]`.

| gun (editor ID) | rung-7 mesh | TTWVR's nodes in it | verdict |
| --- | --- | --- | --- |
| 10mm pistol `weap10mmpistol` | Classic 10mm Pistols `P610mmPistols\10mmP.nif` (Gun and Friends' 10mm is off: `b10mmPistol = 0`) | `##Clip`, `##Slide`, `ProjectileNode` present | parts found; boxes, grab surface and magazine path are the vanilla 10mm's → **partial** |
| 10mm SMG `weap10mmsubmachinegun` | Gun and Friends `10mmSMGre\10mmSMGRE.nif` (`b10mmSMG = 1`); TTWVR's own reshaped `10mmsubmachinegun.nif` is no longer used at all | `##SMGClip` yes, **`##SMGBoltL` missing** (no bolt or handle node of any name) | **miss** on cocking; rest stale numbers |
| hunting rifle `weaphuntingrifle` | Gun and Friends `HRRedux\HR308.nif` (`bhuntingrifle = 1`; `zzz` script likely runs after WAP's `tigerx87` swap) | `##HRClip`, `##HRBolt` in both candidates | parts found, numbers stale; **scope** (`@2/3/6/7`, `HR308Scope.nif`) has no lens node, so the lens is pinned at the vanilla scope's centre → likely off `[inferred]` |
| varmint rifle `weapnvvarmintrifle` | AWO `weapons\awo\...\Varmint\Varmint.nif` | `##VRClip`, `##VRBolt` | partial; scope variant `Varmint+scope.nif` has nodes `Scope` / `Lenses`, not TTWVR's, so the lens is again at vanilla numbers `[inferred]` |
| combat shotgun `weapshotguncombat` | Another Millenia `AnotherMilR\CShotgun\Combat.nif` (Gun and Friends' is off) | `##CSDrum`, `##CSLever` | partial |
| service rifle `weapnvservicerifle` / marksman `weapnvmarksmancarbine` | AR Series `conzo\AR15\ServiceRifle.nif` / `MarksmanCarbine.nif` | `##Clip`, `##ChargingHandle` | partial; the marksman has a `ScopeLens:0` node, but TTWVR's `@0/@1` table row (root-space numbers) probably wins over it `[inferred]` |
| assault rifle (R91) `weapassaultrifle` | Gun and Friends `g3re\g3assaultrifle.nif` (`bAssaultRifle = 1`) | `##G3Clip`, `##G3Lever` | partial |
| laser pistol `weaplaserpistol` | EVE Lite overwrites the vanilla path `Weapons\1HandPistol\LaserPistol.nif` (TTWVR ships none) | `##LPSmallEnergyCell` | partial (same key, new shape) |

"Partial" means:
- the magazine and handle are found by name `[measured]`;
- the boxes, the grab surface, the magazine exit and seating, and the scope lens are the vanilla gun's `[inferred]`.

How wrong depends on how far the new shape is from vanilla. In the headset that would show as:
- a hand that closes on air or inside the gun;
- the support hand not taking the foregrip;
- a magazine that will not seat or drop cleanly;
- a scope picture offset from the tube.

The vanilla hand pose (`grips-pose.txt` is read from vanilla `.kf`) can also disagree with rung 7's new animations
(Dri 10mm anim set via AnimGroupOverride, more at 8a with NVAO) `[inferred]`.

The 10mm (the gun Tefa has been describing for TTWVR's reload) is a "partial", not a "miss".

## What a bridge fix would look like `[inferred-static]`

- **Cheapest: keep TTWVR's guns.** Our MO2 mod above the list turns the swaps off for the guns that misbehave:
  - set `b10mmSMG`, `bhuntingrifle` and `bAssaultRifle` to `0` in a higher-priority `config/Xamie/GunAndFriends.ini`;
  - for the other replacers, an empty `gr_*.txt` of the same name (Classic 10mm, AWO Varmint, Another Millenia,
    AR Series), or switch that mod off.

  The vanilla meshes then come back, and TTWVR's data fits them exactly.
- **Proper: give TTWVR data for the new meshes.** Our MO2 mod ships a rebuilt `TTWVR.dat`. The pack format is
  trivial (no compression), and Tefa allows changing TTWVR as our own mod. The changed rows, under the same editor ID
  and mask keys, are re-measured from the replacer meshes: `handling`, `pistol-zones`, `scopes`, and `grips.bin` and
  `mag-grip.bin` (binary, format not yet read). We would need our own copy of the generator tools.
- For the SMG, also add a `##SMGBoltL` node to a copy of `10mmSMGRE.nif`, or point its handle row at a part that
  exists.
- One headset look at each "partial" gun decides which route each gun needs.
