# /gr: another New Vegas VR mod fixed a swimming sky by centring the sky dome on each eye

Bears on the board row of 2026-11-13 (rung 5 worn):
> "THE FAR VIEW SWIMS ... the skyline band slides 2-6 px per frame with the head sway while the middle distance stays at 0 ... Likely one root for the swim, the far water over the near land and maybe the blinking: TTWVR's far (LOD) pass in stereo."

df4l's FNVVR Reborn (a DXVK-based New Vegas VR mod, public release notes) fixed in v0.2.0: "the sky dome is centred on
each eye: clouds no longer move against your head", and later distant water "turning grey and flat at the sides of
your view" (v0.10.0) and square shapes from one water reflection shared between both eyes (v0.5.0) `[reported]`.
The game places its sky around ONE camera point; something far drawn around a shared centre slides with head
movement `[hypothesis]` for our swim.

Suggested change: before reading TTWVR's far pass, run a sideways-only head move in the simulator and see whether
the sky/clouds move with the far LOD band (one-centre placement) or the band alone does (the far pass's own camera).
Also check Begin Again for LOD Flicker Fix, which FNVVR needed special handling for. Topic:
`external-research/topics/2026-11-14-fnvvr-reborn-already-met-our-sky-water-and-stewie-faults.md`.
