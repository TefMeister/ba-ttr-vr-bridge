#!/usr/bin/env python3
"""save_needs.py -- will this save open with the game's "This save relies on content that is no longer present" box?

Tefa, 2026-11-13 (a picture of that box): "is there a way you can check for those, they do keep popping up".
The box comes when a save was made with mods that the profile now starting does not have on (a save from a higher rung
loaded on a lower one, or from the full Begin Again). Every New Vegas save names the mods it was made with, so this
is known BEFORE the game starts: no game, no window, nothing touched (the save is only read).

    python save_needs.py --mo2 <Begin Again folder> --rung "rung-03 world" [--save "Save 4"]
        one save (default: the newest) against one profile: "opens clean" or the mods the box would name
    python save_needs.py --mo2 <Begin Again folder> --save "Save 4" --all
        the same save against every rung profile: the lowest rung it opens clean on
Exit 0 = opens clean, 2 = the box would come, 1 = could not tell (the reason is printed).

How it reads the save: a one-byte count, then each mod's name with its length, separated by "|", starting at
FalloutNV.esm (layout measured on Tefa's saves 2026-11-13; --list prints what was read). The profile's mods on are the lines of its plugins.txt with a
game's own files (New Vegas and its DLC) are always there.
"""
import argparse, os, re, struct, sys

GAME_OWN = {n.lower() for n in (
    "FalloutNV.esm", "DeadMoney.esm", "HonestHearts.esm", "OldWorldBlues.esm", "LonesomeRoad.esm",
    "GunRunnersArsenal.esm", "CaravanPack.esm", "ClassicPack.esm", "MercenaryPack.esm", "TribalPack.esm")}
NAME = re.compile(rb"[\x20-\x7e]{1,250}?\.(?:esm|esp)", re.IGNORECASE)


def saves_dir():
    return os.path.join(os.path.expanduser("~"), "Documents", "My Games", "FalloutNV", "Saves")


def pick_save(part):
    d = saves_dir()
    fos = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(".fos")]
    if part:
        fos = [f for f in fos if part.lower() in os.path.basename(f).lower()]
    if not fos:
        raise SystemExit("no save found%s in the saves folder" % (" matching '%s'" % part if part else ""))
    return max(fos, key=os.path.getmtime)


def save_plugins(path):
    """The save's mods, in its order. Measured 2026-11-13 on Tefa's saves: a one-byte count, then per mod "|", its
    length (uint16 little-endian), "|", the name: ... a7 | 0d 00 | FalloutNV.esm | 0d 00 | DeadMoney.esm | ...
    New Vegas's own master is always first, so the list is found from it."""
    data = open(path, "rb").read()
    i = data.find(b"|FalloutNV.esm|")
    if i < 4:
        return []
    count = data[i - 4]
    out, pos = [], i - 2   # pos at the first length
    for _ in range(count):
        if pos + 3 > len(data): break
        n = struct.unpack_from("<H", data, pos)[0]
        name = data[pos + 3:pos + 3 + n]
        if data[pos + 2:pos + 3] != b"|" or not NAME.fullmatch(name):
            break
        out.append(name.decode("latin-1"))
        pos += 3 + n + 1   # length, "|", name, "|"
    return out


def profile_on(mo2, rung):
    p = os.path.join(mo2, "profiles", rung, "plugins.txt")
    if not os.path.isfile(p):
        raise SystemExit("no plugins.txt for profile '%s'" % rung)
    on = set(GAME_OWN)
    for line in open(p, encoding="utf-8", errors="replace"):
        # New Vegas's plugins.txt (as MO2 writes it, seen 2026-11-13): one ACTIVE mod per line, no "*" marks (those are the
        # newer games' format); off mods are simply absent. A leading "*" is still accepted.
        line = line.strip().lstrip("*").strip()
        if line and not line.startswith("#"):
            on.add(line.lower())
    return on


def missing(plugins, on):
    return [n for n in plugins if n.lower() not in on]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--rung")
    ap.add_argument("--save", default="", help="part of the save's name (default: the newest save)")
    ap.add_argument("--all", action="store_true", help="every rung profile (VR ones, not the sim / flat twins)")
    ap.add_argument("--list", action="store_true", help="print the save's whole mod list too")
    a = ap.parse_args()
    save = pick_save(a.save)
    plugins = save_plugins(save)
    if not plugins:
        print("could not read a mod list from %s" % os.path.basename(save)); return 1
    print("save: %s (%d mods)" % (os.path.basename(save), len(plugins)))
    if a.list:
        for n in plugins: print("   " + n)
    if a.all:
        prof = sorted(d for d in os.listdir(os.path.join(a.mo2, "profiles"))
                      if d.startswith("rung-") and not d.endswith((" sim", " flat")))
        first = None
        for r in prof:
            m = missing(plugins, profile_on(a.mo2, r))
            print("  %-36s %s" % (r, "opens clean" if not m else "BOX: %d missing (%s%s)" % (len(m), ", ".join(m[:4]), ", ..." if len(m) > 4 else "")))
            if not m and first is None: first = r
        print("lowest rung it opens clean on: %s" % (first or "none of them"))
        return 0
    if not a.rung:
        print("say --rung or --all"); return 1
    m = missing(plugins, profile_on(a.mo2, a.rung))
    if not m:
        print("%s: opens clean (no 'content no longer present' box)" % a.rung); return 0
    print("%s: the 'content no longer present' box WILL come; %d mod(s) the save has that the profile has off:" % (a.rung, len(m)))
    for n in m: print("   " + n)
    return 2


if __name__ == "__main__":
    sys.exit(main())
