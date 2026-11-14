#!/usr/bin/env python3
"""ladder_groups.py -- build the rest of the ladder: Begin Again's own groups back on top of the VR base, a few at a
time, weapons and animations last (KUPOkinz: mods touching the player model, the Pip-Boy or the player's animations
"may break" TTWVR).

Each rung is TWO MO2 profiles made from the list author's own order (nothing is reordered, mods are only switched on):
    "rung-NN <name>"        the groups so far + TTWVR on top (it must win every clash): for the headset
    "rung-NN <name> flat"   the same without TTWVR: a desk check that the list side loads at all
A mod whose plugin needs a master that is not on yet is left off for that rung and named in the report (it comes on
by itself at the rung where its masters do). Settings files come from the rung-01 profile.

    python ladder_groups.py plan  --mo2 <Begin Again folder>            the groups, the rungs, what would be deferred
    python ladder_groups.py make  --mo2 <Begin Again folder> [--force] [--only 08a,08b]  write the profiles (all, or the
                                                                       ones named) and check each one
"""
import argparse
import os
import shutil
import stat
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ladder as L   # noqa: E402

BASE = "Begin Again"
FILES_FROM = "rung-01 vr base"
TTWVR = "TTWVR 1.0.0"
# always on: the game itself and the tools every rung needs
FLOOR = ["PUT TALE OF TWO WASTELANDS MOD HERE", "UTILITIES"]
# cumulative, safest first; the three KUPOkinz warns about come last, one at a time
RUNGS = [
    ("02", "fixes", ["BUGFIXES & QOL"]),
    ("03", "world", ["WORLDSPACE EDITS", "LOD RESOURCES", "WORLDSPACE MESHES & TEXTURES", "SOUNDS & MUSIC",
                     "WEATHER & LIGHTING", "QUESTS & ADVENTURES"]),
    ("04", "gameplay", ["GAMEPLAY", "IMMERSION"]),
    ("05", "interface", ["USER INTERFACE"]),
    ("06", "armor and people", ["ARMOR", "ACTOR APPEARANCE"]),
    ("07", "weapons", ["WEAPONS"]),
    # 2026-11-12: rung 8 split before it is worn (the board's row): its three groups one at a time, so a fault in the
    # headset names its group. "rung-08 animations and the rest" (made 2026-11-10) stays as it is: it equals 08c.
    ("08a", "skeleton and animation", ["SKELETON & ANIMATION"]),
    ("08b", "late loaders", ["LATE LOADERS"]),
    ("08c", "optional mods", ["OPTIONAL MODS"]),
]
# mods brought down from a later group, on from this rung up (Tefa 2026-11-12: "switch the pack on from rung 3"):
# Begin Again's own baked far view (the dense horizon). Each is a 1 KB plugin, master FalloutNV.esm only, that loads its
# same-named archives; they sit in OPTIONAL MODS, which kept the horizon off until rung 8b.
EARLY = {"03": ["Begin Again Object LOD", "Begin Again Terrain LOD"]}
# side rungs: a rung's mods minus some, NOT carried into the rungs after it. 08a without the one mod TTWVR's log complains
# about on rung 8 (the first-person skeleton): does the complaint go?
SIDE = [
    ("08a-x", "skeleton and animation without NVCS weights", "08a", ["NVCS Vanilla Weights"]),
    # 2026-11-12: the complaint stayed without NVCS; the group's only other first-person skeleton is Enhanced Movement's
    # skeletonEM.nif (which it swaps in during play)
    ("08a-y", "skeleton and animation without Enhanced Movement", "08a", ["Enhanced Movement"]),
    ("08a-z", "skeleton and animation without both skeletons", "08a", ["NVCS Vanilla Weights", "Enhanced Movement"]),
]


def groups_of(mo2):
    """group name -> the mods the author has ON in it, from the base profile's modlist.txt (highest priority first;
    a separator closes the group written above it)."""
    lines = [l for l in L.read_lines(os.path.join(L.profile_dir(mo2, BASE), "modlist.txt")) if l and not l.startswith("#")]
    out, cur = {}, []
    for l in lines:
        flag, name = l[0], l[1:]
        if name.endswith("_separator"):
            out[name[:-len("_separator")]] = [m for f, m in cur if f == "+"]
            cur = []
        else:
            cur.append((flag, name))
    return out, lines


def resolve(mo2, want, base_lo):
    """Drop mods whose plugins miss a master, until nothing is missing. Returns (mods on, load order, deferred)."""
    mods_dir = os.path.join(mo2, "mods")
    on = list(want)
    deferred = []
    while True:
        have, owner = {}, {}
        for m in on:
            for p in L.mod_plugins(mods_dir, m):
                have[p.lower()] = os.path.join(mods_dir, m, p)
                owner[p.lower()] = m
        bad = {}
        for k, path in have.items():
            for ms in (L.plugin_masters(path) or []):
                if ms.lower() not in have:
                    bad.setdefault(owner[k], set()).add(ms)
        if not bad:
            lo = [p for p in base_lo if p.lower() in have]
            lo += sorted(os.path.basename(have[k]) for k in have if k not in {x.lower() for x in lo})
            return on, lo, deferred
        for m, miss in bad.items():
            deferred.append((m, sorted(miss)))
        on = [m for m in on if m not in bad]


# Off in every VR rung (Tefa 2026-11-13, option a): 360 Movement is a third-person movement mod; with TTWVR's own body
# skeleton winning over NVCS's it cannot find its "360Corr0" node and puts up a box, many times, which smears the VR view.
OFF_IN_VR_MODS = {"360 Movement", "3rd Person Animation Fixpack - 360 Movement patch"}
OFF_IN_VR_PLUGINS = {"360movement.esp", "360movement - diagonal movement patch.esp"}
# On in EVERY rung, VR and flat alike (so the twins still differ only by TTWVR), just under TTWVR: our own bridge mods
# (source in bridge-mods/). 2026-11-14: the rung-5 start crash is Stewie's Tweaks' grabbed-weight hook reading an empty
# object during the load; this mod turns that one setting off (modding-notes/2026-11-14-the-rung-5-crash-...).
BRIDGE_MODS = ["Bridge - Stewie grabbed weight off"]


def write_profile(mo2, name, on, lo, base_lines, with_vr, force):
    if with_vr:
        on = [m for m in on if m not in OFF_IN_VR_MODS]
        lo = [x for x in lo if x.lower() not in OFF_IN_VR_PLUGINS]
    dst = L.profile_dir(mo2, name)
    src = L.profile_dir(mo2, FILES_FROM)
    if os.path.exists(dst):
        if not force:
            sys.exit(f"profile already exists: {name} (use --force to rewrite OUR rung profiles)")
        if not os.path.basename(dst).startswith("rung-"):
            sys.exit("refusing to rewrite a profile that is not a rung")
        for x in os.listdir(dst):
            p = os.path.join(dst, x)
            if os.path.isfile(p):
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
                os.remove(p)
    else:
        os.makedirs(dst)
    for x in os.listdir(src):
        if x in ("modlist.txt", "plugins.txt", "loadorder.txt", "lockedorder.txt") or ".bak" in x:
            continue
        s = os.path.join(src, x)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(dst, x))
            os.chmod(os.path.join(dst, x), stat.S_IWRITE | stat.S_IREAD)
    want = set(on)
    new = [("+" if with_vr else "-") + TTWVR] + ["+" + m for m in BRIDGE_MODS]
    for l in base_lines:
        flag, nm = l[0], l[1:]
        if nm.endswith("_separator") or flag == "*":
            new.append(l)
        else:
            new.append(("+" if nm in want else "-") + nm)
    L.write_lines(os.path.join(dst, "modlist.txt"), new)
    L.write_lines(os.path.join(dst, "loadorder.txt"), lo)
    L.write_lines(os.path.join(dst, "plugins.txt"), lo)
    L.write_lines(os.path.join(dst, "lockedorder.txt"), [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("what", choices=("plan", "make"))
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rung numbers to make (e.g. 08a,08b,08c,08a-x); the others are only planned")
    a = ap.parse_args()
    groups, base_lines = groups_of(a.mo2)
    base_lo = [l for l in L.read_lines(os.path.join(L.profile_dir(a.mo2, BASE), "loadorder.txt")) if l and not l.startswith("#")]
    # the floor: the two always-on groups AND every mod the proven base profile has on, wherever the author filed it
    # (rung 2 first stopped on "NVTF.ini not found": that file is in "Begin Again Configs", which sits in a late group)
    so_far = []
    for g in FLOOR:
        so_far += groups.get(g, [])
    floor_lines = L.read_lines(os.path.join(L.profile_dir(a.mo2, FILES_FROM), "modlist.txt"))
    for l in floor_lines:
        if l.startswith("+") and not l.endswith("_separator") and l[1:] != TTWVR and l[1:] not in so_far:
            so_far.append(l[1:])
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    problems = 0
    after = {}   # rung number -> the mods wanted once it is on (for the side rungs)

    def one(num, label, want, what_added):
        nonlocal problems
        on, lo, deferred = resolve(a.mo2, want, base_lo)
        name = f"rung-{num} {label}"
        print(f"{name}: {what_added}: {len(on)} mods on, {len(lo)} plugins" + (f", {len(deferred)} left off for now" if deferred else ""))
        for m, miss in deferred:
            print(f"    left off: {m} (needs {', '.join(miss)})")
        if a.what == "make" and (not only or num in only):
            write_profile(a.mo2, name, on, lo, base_lines, True, a.force)
            write_profile(a.mo2, name + " flat", on, lo, base_lines, False, a.force)
            problems += L.check_profile(a.mo2, name)
            problems += L.check_profile(a.mo2, name + " flat")

    for num, label, gs in RUNGS:
        for g in gs:
            if g not in groups:
                print(f"  (no group named {g!r} in the list)")
            so_far += [m for m in groups.get(g, []) if m not in so_far]
        so_far += [m for m in EARLY.get(num, []) if m not in so_far]
        after[num] = list(so_far)
        one(num, label, so_far, "+ " + ", ".join(gs))
    for num, label, of, minus in SIDE:
        missing = [m for m in minus if m not in after.get(of, [])]
        if missing:
            print(f"  (side rung {num}: not on in rung {of}: {', '.join(missing)})")
        one(num, label, [m for m in after.get(of, []) if m not in minus], f"rung {of} minus {', '.join(minus)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
