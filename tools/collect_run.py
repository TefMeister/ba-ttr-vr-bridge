#!/usr/bin/env python3
"""collect_run.py -- after every launch, keep every log the next launch would overwrite.

    python collect_run.py --mo2 <Begin Again folder> --game <Fallout New Vegas folder> --rung "rung-00 flat base"
                          --since "2026-11-09 21:30" [--out <repo>/runs]

Copies, into runs/<date time> <rung>/: every .log / .txt the game, xNVSE, its plugins, the crash logger, Root Builder,
MO2 and TTWVR wrote since --since (game folder, its Data/NVSE tree, MO2's logs and overwrite folder, Documents/My
Games/FalloutNV), plus the Windows Application error events for FalloutNV.exe since then. Files over 2 MB keep only
their last 2 MB. Prints one line per file and writes INDEX.md in the run folder.
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys

KEEP = (".log", ".txt")
MAX = 2 * 1024 * 1024


SEP = '[/' + re.escape(chr(92)) + ']+'
OTHER_HOME = re.compile('(?i)([A-Z]:' + SEP + 'Users' + SEP + ')[^/' + re.escape(chr(92)) + ' \t"|]+')


def is_binary(p):
    return os.path.splitext(p)[1].lower() in (".dmp", ".bin", ".fos", ".pdb", ".dll", ".exe", ".png", ".jpg", ".dds")


def scrubber():
    """Public repo: the home folder becomes ~, the login and the PC's name become <user> / <pc> (never published)."""
    home = os.path.expanduser("~")
    user = os.path.basename(home)
    pc = os.environ.get("COMPUTERNAME", "")
    pairs = []
    for h in {home, home.replace("\\", "/"), home.replace("\\", "\\\\")}:
        pairs.append((h, "~"))
    for v, rep in ((user, "<user>"), (pc, "<pc>")):
        if v and len(v) >= 3:
            pairs.append((v, rep))
    def scrub(b):
        t = b.decode("utf-8", errors="replace")
        for a, r in pairs:
            t = t.replace(a, r).replace(a.lower(), r).replace(a.upper(), r)
        # anyone else's home folder too (a plugin author's build path, say): the privacy guard refuses any of them
        t = OTHER_HOME.sub(lambda m: m.group(1) + '<user>', t)
        return t.encode("utf-8")
    return scrub


def candidates(roots, since):
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dp, _dn, fn in os.walk(r):
            depth = dp[len(r):].count(os.sep)
            if depth > 4:
                continue
            for x in fn:
                if not x.lower().endswith(KEEP):
                    continue
                p = os.path.join(dp, x)
                try:
                    if dt.datetime.fromtimestamp(os.path.getmtime(p)) >= since:
                        yield r, p
                except OSError:
                    pass


def win_errors(since):
    ps = ("Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=[datetime]'%s'} -ErrorAction SilentlyContinue | "
          "Where-Object { $_.Message -match 'FalloutNV|nvse|Fallout3' } | "
          "ForEach-Object { '---- ' + $_.TimeCreated + ' ' + $_.ProviderName + ' ' + $_.Id; $_.Message }") % since.strftime("%Y-%m-%d %H:%M:%S")
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout
    except Exception as e:
        return f"(could not read the Windows event log: {e})"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--game", required=True)
    ap.add_argument("--rung", required=True)
    ap.add_argument("--since", required=True, help='"YYYY-MM-DD HH:MM" local time, just before the launch')
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs"))
    a = ap.parse_args()
    since = dt.datetime.fromisoformat(a.since.strip())  # "YYYY-MM-DD HH:MM" or with seconds
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H%M")
    dst = os.path.join(a.out, f"{stamp} {a.rung}")
    os.makedirs(dst, exist_ok=True)
    mygames = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "FalloutNV")
    roots = [a.game, os.path.join(a.mo2, "logs"), os.path.join(a.mo2, "overwrite"), mygames]
    rows = []
    scrub = scrubber()
    for root, p in candidates(roots, since):
        label = {a.game: "game", mygames: "mygames"}.get(root, os.path.basename(root))
        rel = os.path.relpath(p, root)
        out = os.path.join(dst, label + "__" + rel.replace(os.sep, "__"))
        size = os.path.getsize(p)
        if size > MAX:
            with open(p, "rb") as f:
                f.seek(-MAX, os.SEEK_END)
                data = f.read()
            data = b"(only the last 2 MB kept)\n" + data
        else:
            with open(p, "rb") as f:
                data = f.read()
        with open(out, "wb") as f:
            f.write(data if is_binary(p) else scrub(data))
        rows.append((label, rel, size))
        print(f"kept {label}/{rel} ({size:,} bytes)")
    ev = win_errors(since)
    with open(os.path.join(dst, "windows-application-errors.txt"), "w", encoding="utf-8") as f:
        f.write(scrub((ev or "(none)\n").encode("utf-8")).decode("utf-8"))
    with open(os.path.join(dst, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(f"# {a.rung}, launched after {a.since}\n\n| where | file | bytes |\n| --- | --- | --- |\n")
        for l, r, s in rows:
            f.write(f"| {l} | `{r}` | {s:,} |\n")
        f.write(f"\nWindows error events for the game since then: {'yes, see windows-application-errors.txt' if ev.strip() else 'none'}\n")
    print(f"{len(rows)} log(s) kept in {dst}; Windows errors: {'YES' if ev.strip() else 'none'}")


if __name__ == "__main__":
    sys.exit(main())


def rescrub(folder):
    """Scrub an already-kept run folder in place (runs kept before the scrub was wired in)."""
    scrub = scrubber()
    for root, _, files in os.walk(folder):
        for n in files:
            p = os.path.join(root, n)
            if is_binary(p):
                continue
            with open(p, "rb") as f:
                b = f.read()
            c = scrub(b)
            if c != b:
                with open(p, "wb") as f:
                    f.write(c)
                print("scrubbed", os.path.relpath(p, folder))
