# /gr: the Stewie's Tweaks crash hook matches the `bEncumbranceIncludesGrabbedItems` switch

Answers the question in `engine-research/inbox/2026-11-14-gd-a-stewie-tweaks-crash-in-a-rung-4-sim-run.md`:
> "which Stewie's Tweaks setting (grabbed-weight) to switch off in Begin Again's INI for the VR rungs."

ModdingLinked's commented Stewie's Tweaks INI lists `bEncumbranceIncludesGrabbedItems` = "include grabbed item weight
when determining if player is overencumbered" `[reported]`; the crash hook is `IsOverencumberedAddGrabbedWeightHook`.
That the hook only runs with the switch on is `[inferred-static]` (name match; the Tweaks source is not public). No
public crash report names the hook.

Suggested change: read the switch's value in Begin Again's Stewie's Tweaks INI; if it is 1, set it to 0 for the VR
rungs in our own MO2 mod (Begin Again untouched) and re-run rung 4 in the simulator. Separately, FNVVR Reborn's notes
say to keep `bSmoothIronsightsCameraTransition`, `bScopeVisibilityDelay` and `bAlwaysShowWeaponAnimation` off in VR
`[reported]`. Topic: `external-research/topics/2026-11-14-stewie-tweaks-grabbed-weight-switch.md`.
