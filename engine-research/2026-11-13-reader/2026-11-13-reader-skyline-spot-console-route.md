# 2026-11-13 reader: one outdoor spot facing the D.C. skyline, by console only (for the horizon decider)

From: the static reader (read-only; parsed copies of the plugin records, no game, no MO2, no profile touched).
For: the modding lane, board row "THE HORIZON".

## The spot `[measured]` (records parsed out of TTW's `Fallout3.esm`, in the `[NoDelete] TTW 3.4` mod)

- TTW 3.4 keeps Fallout 3's own editor IDs, with no prefix. They sit in `Fallout3.esm` (the converted master), and
  some are repeated in `TaleOfTwoWastelands.esm`. The world is `Wasteland` (form `0607EA1F` in this load order).
- **Best spot: Springvale Elementary's map marker**, right outside the school the saves already start in:
  - `SpringvaleElementaryMapMarker`, REFR `0600321F`, in the Wasteland's persistent cell;
  - position x -1671.6, y -4337.4, z 11814.9.
  - Command: `player.moveto SpringvaleElementaryMapMarker`.
- Alternatives:
  - `SpringvaleSchoolDoorExteriorto01REF` (`060183CF`, the outside of the school door; x -1555.0, y -4825.3,
    z 11776, facing 180°). Moving onto a door can leave you inside its frame; the marker is cleaner.
  - Cells for `coc` (exterior, editor IDs present): `SpringvaleSchoolExterior` (grid -1,-2), `Springvale` (-2,-4),
    `Vault101Exterior` (-4,-4), `MegatonMainGate` (-1,-5), `SuperDuperMartExterior` (4,-5).
  - `coc` lands at the cell's centre or its marker, so it is less exact than `moveto` `[inferred]`.
  - Second spot if Springvale's view is blocked: `SuperDuperMartMapMarkerREF` (`060030C4`, x 20125.0, y -17747.3,
    z 11025.8).

## Which way to face `[measured]` positions; heading worked out `[inferred]`

- The Washington Monument is a `WashMonument` STAT placed in `DCworld01` at x 55622.5, y -38927.9, z 12096.
  `WashingtonMonumentExterior` is also a Wasteland cell at grid (15,-10), so the same coordinates hold in the
  Wasteland `[inferred]`. The Capitol dome pieces are at about x 88600-94400, y -39072.
- Heading from the Springvale marker: dx +57294, dy -34591. In Bethesda's convention (0 = north, +Y; clockwise; 90 =
  east) that is **`player.setangle z 121`** (east-south-east). From the Super-Duper Mart marker it also comes out at
  about **121**. The Capitol lies almost on the same line, a little further out (about 112° from Springvale).
- Keep the view level with `player.setangle x 0`.
- Distance about 66,900 units (about 0.95 km): far-view (LOD) range, which is what is being tested.
- Whether terrain hides it at ground level from Springvale has not been checked. The flat still settles that; if it
  is blocked, use the Super-Duper Mart marker, same 121.

## Does `setangle` turn the VR view? `[inferred-static]`, needs one check

- TTWVR hooks the engine's own `SetAngleZ` and `SetAngleX` ("Hook SetAngleZ failed ... shots will NOT follow the
  barrel"). It has smooth/snap turning (`bSnapTurn`, `fSnapTurnDegrees`). No recenter command shows in its strings.
- So the VR view is the body's heading plus the headset's yaw. A console `setangle z` probably moves the body
  heading, and the view with it, but TTWVR may overwrite it the next frame from its own turn state `[hypothesis]`.
- Check it once in the simulator:
  - head pose straight (yaw 0);
  - `player.setangle z 121`, then `player.getangle z` and a still;
  - compare with the flat still.
- If it did not turn, set the simulator's head yaw to make up the difference, or use snap turns.

## The console in both modes

- **Flat:** the vanilla console key (grave/tilde, scan code 0x29). Begin Again's Stewie's Tweaks has
  `iConsoleKey = 0` (= keep the default) and `bDontAllowConsoleTillLoadingIsDone = 1` (not until the save has loaded).
  Improved Console, JIP LN and Stewie's are on from rung 1 (checked on rungs 3 and 8c) `[measured]` for the INI and
  mods; that the key is the default is `[inferred]`.
- **VR / simulator:** the same key works while the game window has keyboard focus `[inferred]`. TTWVR also has two
  routes of its own `[inferred-static]` (DLL strings, not tried):
  - **a VR keyboard** that runs console commands ("[keyboard] no console to run '%s' on");
  - **a command file `NVVR-cmd.txt`**, whose verbs include `console <command>`, `dumpfront` / `dumpback`
    (`NVVR-cmd-front.bmp` / `-back.bmp`, eye pictures saved to disk), `status`, `localmap`, `worldmap`, `show`,
    `cull`, `probe`, `focus`.

  Which folder it reads the file from is not established (probably beside `TTWVR.log` in
  `~/Documents/My Games/FalloutNV/`, or the game folder). That would give a no-keyboard, no-focus route for the sim
  run, and a stereo still with no screenshot tool. The `cull` verb here sits among menu-node verbs (`show`, `root`);
  it is probably not world culling, so do not read it as the `bFogCull` switch `[inferred]`.
- **Hiding the HUD:** `tm` (ToggleMenus) and `tfc` (ToggleFlyCam) are vanilla engine commands, so they exist here
  `[inferred]`.
  - Flat: `tm` for a clean still.
  - VR: Tefa's TTWVR menu already has `HUD=Off`. `tm` there may also hide TTWVR's panels.
  - Avoid `tfc` in VR: it detaches the game camera that TTWVR drives `[inferred]`.

## The route, as typed (same in both runs)

```
player.moveto SpringvaleElementaryMapMarker
player.setangle x 0
player.setangle z 121
tm
```
Wait for the far view to load (a few seconds), take the still, then `tm` again to bring the HUD back.
