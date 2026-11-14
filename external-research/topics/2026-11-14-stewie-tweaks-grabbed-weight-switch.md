# The Stewie's Tweaks crash in `IsOverencumberedAddGrabbedWeightHook`: the INI switch that turns that hook's feature on

**Status:** 🆕 new · **Priority:** medium. Gold Digger found one real crash in the rung-4 simulator run of
2026-11-13 15:41: an access violation at the top of `nvse_stewie_tweaks`, in `IsOverencumberedAddGrabbedWeightHook`
(`engine-research/inbox/2026-11-14-gd-a-stewie-tweaks-crash-in-a-rung-4-sim-run.md`).

## What is public

- No public page names that hook or a crash in it: two web searches and a GitHub search found nothing
  `[reported, negative from n=3 searches]`. lStewieAl's Tweaks has no public source repository among its author's
  GitHub repositories `[measured 2026-11-14, API]`, so the hook's code cannot be read online.
- **The setting it belongs to:** the commented Stewie's Tweaks INI published by ModdingLinked (the Viva New Vegas
  guide's maintainers) lists `bEncumbranceIncludesGrabbedItems` with the comment "include grabbed item weight when
  determining if player is overencumbered", default 0 in their INI `[reported 2026-11-14, read in the repository
  viewer]`. The hook's name and the switch's wording match; that the hook only runs when this switch is 1 is
  `[inferred-static]` (name match, no source).
- Nearby grab switches in the same INI: `bJumpingDoesntDropGrabbedItem`, `bNoGrabOwnedItems`,
  `bGrabbingItemsIsCrime`.

## What it means for us

- With TTWVR the hands grab world objects, so "the weight of the grabbed item" can be asked for while the game's
  own grab (the one this tweak was written for) holds nothing valid; that would fit a crash at +0xE of a short
  hook `[hypothesis]`.
- First check (no game needed): the value of `bEncumbranceIncludesGrabbedItems` in Begin Again's Stewie's Tweaks
  INI for the VR rungs. If it is 1, a VR-only override to 0 in our own MO2 mod (Begin Again untouched) removes the
  hook's work entirely; it is a small gameplay rule nobody would miss in VR. If it is already 0, the hook runs
  regardless and this lead is weaker.
- FNVVR Reborn's notes also name three Stewie's Tweaks settings to keep off in VR (camera and weapon view); see the
  topic of the same date.

## Sources

- ModdingLinked, Stewie-Tweaks-INIs (the commented Viva New Vegas INI): https://github.com/ModdingLinked/Stewie-Tweaks-INIs
- lStewieAl, lStewieAl's Tweaks and Engine Fixes (Nexus Mods, New Vegas mod 66347): https://www.nexusmods.com/newvegas/mods/66347
- lStewieAl's GitHub (no Tweaks source listed): https://github.com/lStewieAl
