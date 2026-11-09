#!/usr/bin/env python3
"""conflict_report.py -- which files TTWVR and the Begin Again modlist both supply, and who wins.

Run after every update of either (Tefa 2026-11-09: "we have to make it sustainable somehow"). Read-only: it opens the
TTWVR archive's listing, the MO2 instance's mods folder, the profile's modlist.txt and the BSAs of the enabled mods. It
writes one Markdown report and changes nothing.

    python conflict_report.py --ttwvr <TTWVR.zip> --mo2 <Begin Again folder> [--profile "Begin Again"] [--out report.md]

How a file wins in Fallout New Vegas under MO2:
  - two LOOSE files at the same path: the mod lower in MO2's left pane (higher priority) wins. modlist.txt lists the
    highest priority FIRST.
  - a loose file always beats the same path inside a BSA, whatever the order.
So TTWVR, installed loose, beats every BSA copy; against other loose copies it wins only if placed below them.

Also listed: the enabled mods that touch what KUPOkinz warns about ("Any mods touching the player model, pip boy model,
and/or player animations may break" TTWVR).
"""
import argparse
import os
import struct
import sys
import zipfile
from collections import defaultdict

# what touches the player model, the Pip-Boy or player animations (path prefixes, lower case, forward slashes)
RISKY = {
    "player skeleton / body": ("meshes/characters/_male/",),
    "first-person animations": ("meshes/characters/_1stperson/",),
    "Pip-Boy model": ("meshes/pipboy3000/", "meshes/characters/_1stperson/pipboy"),
    "Pip-Boy menus": ("menus/main/", "interface/pipboy", "textures/interface/pipboy"),
    "kNVSE animations": ("meshes/animgroupoverride/", "meshes/_animgroupoverride/"),
    "weapon meshes": ("meshes/weapons/",),
}


def norm(p):
    return p.replace("\\", "/").strip("/").lower()


def zip_files(path):
    with zipfile.ZipFile(path) as z:
        out = []
        for n in z.namelist():
            if n.endswith("/"):
                continue
            p = norm(n)
            if p in ("meta.ini",):
                continue
            out.append(p)
        return out


def bsa_files(path):
    """File paths inside a Fallout 3 / New Vegas BSA (version 104), lower case. [] if unreadable."""
    try:
        with open(path, "rb") as f:
            hdr = f.read(36)
            if len(hdr) < 36 or hdr[:4] != b"BSA\x00":
                return []
            (_, ver, off, flags, nfolders, nfiles, _fnlen, total_name_len, _ft) = struct.unpack("<4sIIIIIIII", hdr)
            if ver not in (103, 104, 105):
                return []
            f.seek(off)
            rec = 24 if ver == 105 else 16
            counts = []
            for _ in range(nfolders):
                r = f.read(rec)
                counts.append(struct.unpack("<I", r[8:12])[0])
            has_dir_names = flags & 0x1
            has_file_names = flags & 0x2
            folders = []
            for c in counts:
                name = ""
                if has_dir_names:
                    ln = f.read(1)[0]
                    name = f.read(ln).rstrip(b"\x00").decode("latin-1")
                f.read(16 * c)  # file records
                folders.append((name, c))
            if not has_file_names:
                return []
            names = f.read(total_name_len).split(b"\x00")
            out, i = [], 0
            for folder, c in folders:
                for _ in range(c):
                    if i < len(names):
                        out.append(norm(folder + "/" + names[i].decode("latin-1")))
                    i += 1
            return out
    except (OSError, struct.error, IndexError):
        return []


def read_profile(mo2, profile):
    """Enabled mods, highest priority first (modlist.txt order); separators skipped."""
    path = os.path.join(mo2, "profiles", profile, "modlist.txt")
    order = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue
            on, name = line[0], line[1:]
            if name.endswith("_separator"):
                continue
            order.append((name, on == "+"))
    return order


def mod_files(mods_dir, name):
    loose, bsas = [], []
    root = os.path.join(mods_dir, name)
    for dp, _dn, fn in os.walk(root):
        for x in fn:
            full = os.path.join(dp, x)
            rel = norm(os.path.relpath(full, root))
            if rel in ("meta.ini",) or rel.startswith("fomod/"):
                continue
            if rel.endswith(".bsa") and "/" not in rel:
                bsas.append(full)
            else:
                loose.append(rel)
    return loose, bsas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ttwvr", required=True)
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--profile", default="Begin Again")
    ap.add_argument("--out", default="conflict-report.md")
    a = ap.parse_args()

    tv = zip_files(a.ttwvr)
    tvset = set(tv)
    mods_dir = os.path.join(a.mo2, "mods")
    order = read_profile(a.mo2, a.profile)
    enabled = [n for n, on in order if on]

    loose_hits = defaultdict(list)   # path -> [mod, ...] (priority order, highest first)
    bsa_hits = defaultdict(list)     # path -> [mod (bsa), ...]
    risky = defaultdict(set)         # area -> mods
    for name in enabled:
        if not os.path.isdir(os.path.join(mods_dir, name)):
            continue
        loose, bsas = mod_files(mods_dir, name)
        allp = list(loose)
        for p in loose:
            if p in tvset:
                loose_hits[p].append(name)
        for b in bsas:
            inside = bsa_files(b)
            allp += inside
            for p in inside:
                if p in tvset:
                    bsa_hits[p].append(f"{name} ({os.path.basename(b)})")
        for area, prefixes in RISKY.items():
            if any(p.startswith(pre) for p in allp for pre in prefixes):
                risky[area].add(name)

    by_area = defaultdict(int)
    for p in tv:
        by_area["/".join(p.split("/")[:2])] += 1

    L = []
    L.append(f"# Conflict report: TTWVR against {a.profile}\n")
    L.append(f"TTWVR archive: `{os.path.basename(a.ttwvr)}`, {len(tv)} files. Profile: {len(enabled)} enabled mods.\n")
    L.append("Loose against loose: the mod higher in this list wins (MO2 priority). Loose against BSA: loose wins.\n")
    L.append(f"## Same loose file in TTWVR and the list: {len(loose_hits)} paths\n")
    L.append("TTWVR must sit below these mods in MO2's left pane, or their copy replaces the VR one.\n")
    per_mod = defaultdict(list)
    for p, ms in loose_hits.items():
        for m in ms:
            per_mod[m].append(p)
    for m in sorted(per_mod, key=lambda x: -len(per_mod[x])):
        ex = ", ".join(f"`{x}`" for x in sorted(per_mod[m])[:3])
        L.append(f"- **{m}**: {len(per_mod[m])} file(s), e.g. {ex}")
    L.append(f"\n## TTWVR loose files that replace a copy inside the list's BSAs: {len(bsa_hits)} paths\n")
    L.append("TTWVR wins these automatically; the list's version (often a retexture or remodel) is lost for those items.\n")
    per_bsa = defaultdict(int)
    for p, ms in bsa_hits.items():
        for m in ms:
            per_bsa[m] += 1
    for m in sorted(per_bsa, key=lambda x: -per_bsa[x]):
        L.append(f"- {m}: {per_bsa[m]}")
    L.append("\n## Enabled mods in the areas KUPOkinz warns about\n")
    for area in RISKY:
        ms = sorted(risky.get(area, ()))
        L.append(f"- **{area}** ({len(ms)}): " + (", ".join(ms) if ms else "none"))
    L.append("\n## TTWVR's files by area\n")
    for k in sorted(by_area, key=lambda x: -by_area[x])[:25]:
        L.append(f"- `{k}`: {by_area[k]}")
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"{a.out}: {len(loose_hits)} loose clashes, {len(bsa_hits)} BSA overrides, "
          f"{sum(len(v) for v in risky.values())} risky-area mod entries")


if __name__ == "__main__":
    sys.exit(main())
