#!/usr/bin/env python3
"""rung_simcheck.py -- a desk check of one VR rung with NOBODY in the headset: the OpenXR Simulator plays the headset
and the VR Bench layer plays the hands.

    python rung_simcheck.py --mo2 <Begin Again folder> --game <New Vegas folder> --rung "rung-02 fixes"
                            --sim <openxr_simulator-32.json> --vrbench <lanes tools/vrbench folder> [--wait 240]

What it does: makes "<rung> sim" (the rung's own VR profile + our mod "Bridge desk test - continue on start", which
loads the newest save from the start menu and keeps the game from pausing when its window is not in front), starts it
through MO2 with XR_RUNTIME_JSON pointing at the simulator for that one start, waits for the save to load, presses the
pause button with the pretend hand and says whether the picture changed, turns the pretend head and says whether the
picture changed, closes the game (a polite close, forced only when it does not answer) and keeps the logs.

It says: started or not, the VR system the mod chose, save loaded or not, pause menu answers or not, world follows the
head or not, add-ons loaded / disabled, new crash logs, hang warnings. The rung's own profile is never touched.
Before it: `vrbench.py start <FalloutNV.exe>`; after the last rung: `vrbench.py stop`.
"""
import argparse
import datetime as dt
import glob
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rung_flatcheck import running   # noqa: E402

DESK_MOD = "Bridge desk test - continue on start"
SETTLE_S = 20          # after the save has loaded, before the first press
PAUSE_CHANGED = 3.0    # mean grey-level change of the desktop that counts as "the pause menu came up"
HEAD_CHANGED = 1.0     # ... as "the world moved with the head"
HEAD_YAW_DEG = 60


def make_profile(mo2, rung):
    src, dst = os.path.join(mo2, "profiles", rung), os.path.join(mo2, "profiles", rung + " sim")
    if not os.path.isdir(src):
        sys.exit(f"no such profile: {rung}")
    if not os.path.isdir(os.path.join(mo2, "mods", DESK_MOD)):
        sys.exit(f"the mod '{DESK_MOD}' is not in the list's mods folder")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    p = os.path.join(dst, "modlist.txt")
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    lines.insert(1, "+" + DESK_MOD)             # the top of the file wins every clash
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return rung + " sim"


def diff(a, b):
    from PIL import ImageChops
    h = ImageChops.difference(a, b).histogram()
    return round(sum(i * c for i, c in enumerate(h)) / sum(h), 2)


def said(v, limit):
    if v is None:
        return "not tried"
    return f"YES ({v})" if v > limit else f"NO ({v})"


def close_game():
    """a polite close twice, then by force; True when force was needed"""
    for force in (False, False, True):
        if not running("FalloutNV.exe"):
            return False
        subprocess.run(["taskkill"] + (["/F"] if force else []) + ["/IM", "FalloutNV.exe"], capture_output=True)
        t = time.time()
        while time.time() - t < 40 and running("FalloutNV.exe"):
            time.sleep(2)
        if force:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    for k in ("--mo2", "--game", "--rung", "--sim", "--vrbench"):
        ap.add_argument(k, required=True)
    ap.add_argument("--wait", type=float, default=240.0)
    a = ap.parse_args()
    if running("FalloutNV.exe") or running("ModOrganizer.exe"):
        sys.exit("the game or Mod Organizer is already running: close it first")
    sys.path.insert(0, a.vrbench)
    import vb_input as vi
    import vb_settings as vs
    import vb_sim
    from PIL import ImageGrab

    def hands(left=None, right=None):
        inp = vi.Input().mode(poses="set", buttons="set")
        for h, kw, x in ((vs.HAND_LEFT, left, -0.2), (vs.HAND_RIGHT, right, 0.2)):
            pose = vi.pose_from_ypr((x, 1.4, -0.4), 0, 0)
            inp.hand(h, grip=pose, aim=pose, **(kw or {}))
        vi.write(inp)

    def tap(**kw):
        hands(**kw)
        time.sleep(0.3)
        hands()

    def shot():
        return ImageGrab.grab().convert("L")

    sim_rung = make_profile(a.mo2, a.rung)
    since = dt.datetime.now()
    crash_dir = os.path.join(a.mo2, "overwrite", "Root", "Crash Logs")
    before = set(glob.glob(os.path.join(crash_dir, "*.log")))
    nvse = os.path.join(a.game, "nvse.log")
    vrlog = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "FalloutNV", "TTWVR.log")
    hands()
    vb_sim.head(0, 1.7, 0, 0, 0)
    subprocess.Popen([os.path.join(a.mo2, "ModOrganizer.exe"), "-p", sim_rung, "moshortcut://:Begin Again"],
                     cwd=a.mo2, env=dict(os.environ, XR_RUNTIME_JSON=a.sim))
    t0 = time.time()
    while time.time() - t0 < 150 and not running("FalloutNV.exe"):
        time.sleep(2)
    if not running("FalloutNV.exe"):
        print(f"{a.rung}: THE GAME NEVER STARTED (150 s)")
        return 2
    loaded_save = False
    while time.time() - t0 < a.wait and running("FalloutNV.exe"):
        try:
            if os.path.getmtime(nvse) > since.timestamp():
                with open(nvse, encoding="latin-1") as f:
                    loaded_save = "DoLoadGameHook" in f.read()
        except OSError:
            pass
        if loaded_save:
            break
        time.sleep(3)
    load_s = round(time.time() - t0)
    pause = head = None
    if loaded_save and running("FalloutNV.exe"):
        time.sleep(SETTLE_S)
        p0 = shot()
        tap(left={"y": True})
        time.sleep(3)
        pause = diff(p0, shot())
        tap(right={"b": True})
        time.sleep(3)
        p2 = shot()
        vb_sim.head(0, 1.7, 0, HEAD_YAW_DEG, 0)
        time.sleep(2.5)
        head = diff(p2, shot())
        vb_sim.head(0, 1.7, 0, 0, 0)
    up = running("FalloutNV.exe")
    text = ""
    try:
        with open(vrlog, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        pass
    backend = (re.findall(r"VR backend: (\S+)", text) or ["none"])[-1]
    runtime = (re.findall(r"OpenXR: runtime '([^']+)'", text) or ["?"])[-1]
    hangs = len(re.findall(r"\[hang\] the game's main loop has not turned", text))
    warns = sorted(set(m[:110] for m in re.findall(r"(?:WARN|ERROR)\s+(.*)", text) if "[hang]" not in m and "64-bit" not in m))
    ok_plugins = off_plugins = 0
    try:
        with open(nvse, encoding="latin-1") as f:
            t = f.read()
        ok_plugins, off_plugins = len(re.findall(r"loaded correctly", t)), len(set(re.findall(r"plugin (\S+) .*disabled", t)))
    except OSError:
        pass
    forced = close_game()
    t2 = time.time()
    while time.time() - t2 < 30 and running("ModOrganizer.exe"):
        time.sleep(2)
    new_crashes = sorted(set(glob.glob(os.path.join(crash_dir, "*.log"))) - before)
    print(f"{a.rung} in the simulator: {'UP' if up else 'GONE'}; VR system {backend} ({runtime}); save loaded "
          f"{'yes after ' + str(load_s) + ' s' if loaded_save else 'NO'}; pause menu answers {said(pause, PAUSE_CHANGED)}; "
          f"world follows the head {said(head, HEAD_CHANGED)}; add-ons loaded {ok_plugins}, disabled {off_plugins}; "
          f"new crash logs {len(new_crashes)}; hang warnings {hangs}; closed {'BY FORCE' if forced else 'politely'}")
    for w in warns[:8]:
        print("    mod log:", w)
    subprocess.run([sys.executable, os.path.join(HERE, "collect_run.py"), "--mo2", a.mo2, "--game", a.game,
                    "--rung", a.rung + " sim", "--since", since.strftime("%Y-%m-%d %H:%M")], capture_output=True)
    return 0 if up and loaded_save and not new_crashes else 1


if __name__ == "__main__":
    sys.exit(main())
