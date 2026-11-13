#!/usr/bin/env python3
"""rung_simcheck.py -- a desk check of one VR rung with NOBODY in the headset: the OpenXR Simulator plays the headset
and the VR Bench layer plays the hands.

    python rung_simcheck.py --mo2 <Begin Again folder> --game <New Vegas folder> --rung "rung-02 fixes"
                            --sim <openxr_simulator-32.json> --vrbench <lanes tools/vrbench folder> [--wait 240]

What it does: makes "<rung> sim" (the rung's own VR profile + our mod "Bridge desk test - continue on start", which
loads the newest save from the start menu and keeps the game from pausing when its window is not in front), starts it
through MO2 with XR_RUNTIME_JSON pointing at the simulator for that one start, waits for the save to load, and then
looks at the picture the VR mod hands to the headset (the simulator's own screenshot, never the desktop):

  1. the world must be in the eye picture (anything brighter than nothing), with no button pressed;
  2. turns the pretend head: the eye picture must be a different one, again with nothing pressed (a LIVE picture);
  3. presses the pause button with the pretend hand: the mod's pause panel must show; un-pauses.

Why this works since 2026-11-12: TTWVR 1.0.0's upscaler helper draws each finished eye straight into the headset's
own picture, through the old kind of shared handle. The simulator's pictures are plain, so the eye stayed frozen
(one fresh still per pause change). Our desk mod's bridge_desk.dll (desk-shim/shareable.cpp) has those pictures made
shareable; with it the eye is live. Without it this check says "follows the head NO".

Then it closes the game politely (never by force) and keeps the logs and the two stills in the run's folder.

It refuses to start while Virtual Desktop's body memory exists (its Streamer is running): with it there and nobody
in the headset the VR mod has no body at all, and the run says nothing. Since 2026-11-12 our desk mod carries
bridge_desk.dll (desk-shim/), which also answers the VR mod's question about that memory with "not there" inside the game;
with it in place the Streamer may stay up. Without it: quit the Streamer first.

--stay leaves the game running after the checks (no close, no log collection), for a session that wants to look.

It says: started or not, the VR system the mod chose, save loaded or not, pause panel shows or not, world drawn or
not, world follows the head or not, add-ons loaded / disabled, new crash logs, hang warnings. The rung's own profile
is never touched, and MO2 is left on the profile it was on.
Before it: `vrbench.py start <FalloutNV.exe>`; after the last rung: `vrbench.py stop`.
"""
import argparse
import ctypes
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rung_flatcheck import running   # noqa: E402

DESK_MOD = "Bridge desk test - continue on start"
DESK_SHIM = "bridge_desk.dll"   # desk-shim/: makes TTWVR ignore Virtual Desktop's empty body memory on a desk run
SETTLE_S = 20           # after the save has loaded, before the first press
AFTER_PRESS_S = 3.5     # after a button, before the picture is taken
PANEL_CHANGED = 1.0     # mean grey-level change of the eye picture that counts as "the pause panel came up"
WORLD_DRAWN = 0.5       # mean grey level of the eye picture that counts as "the world is in it" (empty is exactly 0)
HEAD_CHANGED = 1.0      # mean change between the two stills that counts as "another view"
HEAD_YAW_DEG = 60
DOOR_YAW_DEG = 90       # rung 1's save stands beside the school's double door: it is on the left
DOOR_HOLD_S = 1.0       # the activate button (A) has to be HELD about a second; a tap only shows the prompt
AIM_FIRST_S = 2.0       # the hand points at the door this long before the button goes down
DOOR_LOAD_S = 15        # the way outside loads
THROUGH_DOOR = 20.0     # mean change of the eye picture that counts as "somewhere else now"
WALKED = 5.0            # mean change after 3 s of the walk stick that counts as "moved"
BODY_MEMORY = "VirtualDesktop.BodyState"
DESK_SAVE = "Springvale Elementary School"   # the rung-1 test save (beside the school's double door); see --save
CAMERA_COMPLAINT = "Camera1st's parents are not"
SIM_DATA = os.path.join(os.environ.get("LOCALAPPDATA", ""), "OpenXR-Simulator")


def body_memory_there():
    """True while Virtual Desktop's body-tracking memory exists (its Streamer is running). Read-only open."""
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.OpenFileMappingW.restype = ctypes.c_void_p
    h = k.OpenFileMappingW(4, False, BODY_MEMORY)
    if h:
        k.CloseHandle(ctypes.c_void_p(h))
    return bool(h)


def sim_picture(timeout=6.0):
    """The left eye as the simulator shows it, as a grey picture; None when the simulator gives none.
    The simulator's own request file, as its own tools use it: nothing of the desktop is ever photographed."""
    from PIL import Image
    cid = uuid.uuid4().hex
    req, tmp = os.path.join(SIM_DATA, "screenshot_request.json"), os.path.join(SIM_DATA, f"screenshot_request.{cid}.tmp")
    status, raw = os.path.join(SIM_DATA, f"screenshot_status.{cid}.json"), os.path.join(SIM_DATA, f"screenshot.{cid}.bmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"capture_id": cid, "eye": "left", "layer": "all", "after_sync": 0}, f)
        os.replace(tmp, req)
        t = time.time()
        while time.time() - t < timeout:
            if os.path.exists(status) and os.path.exists(raw):
                try:
                    with open(status, encoding="utf-8") as f:
                        st = json.load(f)
                    with Image.open(raw) as im:
                        im = im.convert("RGB")
                except (OSError, ValueError):
                    time.sleep(0.05)
                    continue
                eye = next((e for e in st.get("geometry", {}).get("eyes", []) if e.get("eye") == "left"), None)
                if eye:
                    x, y, w, h = (int(v) for v in eye["viewport"])
                    im = im.crop((max(0, x), max(0, y), min(im.width, x + w), min(im.height, y + h)))
                return im
            time.sleep(0.05)
        try:                                        # nobody took the request: do not leave it for a later session
            with open(req, encoding="utf-8") as f:
                if json.load(f).get("capture_id") == cid:
                    os.remove(req)
        except (OSError, ValueError):
            pass
        return None
    finally:
        for p in (tmp, status, raw):
            try:
                os.remove(p)
            except OSError:
                pass


def level(im):
    from PIL import ImageStat
    return None if im is None else round(ImageStat.Stat(im.convert("L")).mean[0], 2)


def diff(a, b):
    from PIL import ImageChops, ImageStat
    if a is None or b is None or a.size != b.size:
        return None
    return round(ImageStat.Stat(ImageChops.difference(a.convert("L"), b.convert("L"))).mean[0], 2)


def said(v, limit):
    if v is None:
        return "NO PICTURE"
    return f"YES ({v})" if v > limit else f"NO ({v})"


def mo2_profile(mo2, set_to=None):
    """Read, or put back, the profile MO2 opens on."""
    p = os.path.join(mo2, "ModOrganizer.ini")
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        text = f.read()
    m = re.search(r"^selected_profile=@ByteArray\((.*)\)\r?$", text, re.M)
    if set_to is None or not m or m.group(1) == set_to:
        return m.group(1) if m else None
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text[:m.start(1)] + set_to + text[m.end(1):])
    return set_to


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


def close_game():
    """A polite close, up to three times. Never by force. True when the game is still there afterwards."""
    for _ in range(3):
        if not running("FalloutNV.exe"):
            return False
        subprocess.run(["taskkill", "/IM", "FalloutNV.exe"], capture_output=True)
        t = time.time()
        while time.time() - t < 40 and running("FalloutNV.exe"):
            time.sleep(2)
    return running("FalloutNV.exe")


def put_saves_back(saves, copy, rung):
    """After a run that went through a door: whatever the game saved on the way is moved aside (never deleted) and
    every file is put back as it was, dates included, so 'Continue' loads the same save next time."""
    aside = os.path.join(os.path.dirname(saves), "Saves.desk-made", dt.datetime.now().strftime("%Y-%m-%d %H%M ") + rung)
    moved = 0
    for name in sorted(os.listdir(saves)):
        now, was = os.path.join(saves, name), os.path.join(copy, name)
        if not os.path.isfile(now):
            continue
        same = (os.path.isfile(was) and os.path.getsize(was) == os.path.getsize(now)
                and abs(os.path.getmtime(was) - os.path.getmtime(now)) < 2)
        if same:
            continue
        os.makedirs(aside, exist_ok=True)
        shutil.move(now, os.path.join(aside, name))
        moved += 1
        if os.path.isfile(was):
            shutil.copy2(was, now)
    shutil.rmtree(os.path.dirname(copy), ignore_errors=True)       # our own temporary copy
    return f"saves put back ({moved} file(s) the game wrote kept aside)" if moved else "saves untouched"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    for k in ("--mo2", "--game", "--rung", "--sim", "--vrbench"):
        ap.add_argument(k, required=True)
    ap.add_argument("--wait", type=float, default=240.0)
    ap.add_argument("--stay", action="store_true", help="leave the game running after the checks")
    ap.add_argument("--outside", action="store_true",
                    help="also go through the door beside the save's spot and walk a few steps outside; the save "
                         "folder is put back exactly afterwards (what the game saved on the way is kept aside)")
    ap.add_argument("--save", default=DESK_SAVE,
                    help="part of the name of the save to load (made newest for the run, its date put back after); "
                         "default: the rung-1 school save. 2026-11-13: without this the auto-load took Tefa's own newer "
                         "autosave, so rungs 4-8 were judged from another spot and rung 1 stopped at 'content no longer present'")
    a = ap.parse_args()
    if running("FalloutNV.exe") or running("ModOrganizer.exe"):
        sys.exit("the game or Mod Organizer is already running: close it first")
    shim = os.path.join(a.mo2, "mods", DESK_MOD, "NVSE", "Plugins", DESK_SHIM)
    if body_memory_there() and not os.path.isfile(shim):
        sys.exit("Virtual Desktop's body memory is there (its Streamer is running): with it the VR mod has no body "
                 "on a desk run. Quit the Virtual Desktop Streamer, then start this again.")
    # 2026-11-12: the pretend hands must be on for FalloutNV.exe, or the pause press and the walk outside silently do
    # nothing (five runs said "pause panel shows NO" on rungs that answer, after another session switched VR Bench off).
    # Switched on here every time; it stays on (the docstring's `vrbench.py stop` after the last rung still applies).
    vb = subprocess.run([sys.executable, os.path.join(a.vrbench, "vrbench.py"), "start", os.path.join(a.game, "FalloutNV.exe")],
                        capture_output=True, text=True)
    if vb.returncode != 0:
        sys.exit("VR Bench could not be switched on for FalloutNV.exe: " + (vb.stdout + vb.stderr).strip())
    sys.path.insert(0, a.vrbench)
    import vb_input as vi
    import vb_settings as vs
    import vb_sim

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
        time.sleep(AFTER_PRESS_S)

    def point_and_hold(yaw_deg, secs, **right):
        """Aim both hands that way FIRST, then hold the button: a press that arrives with the hand's move is aimed at
        nothing (all eight rungs failed the door that way on 2026-11-12)."""
        import math
        rad = math.radians(yaw_deg)
        fx, fz = -math.sin(rad), -math.cos(rad)     # yaw 0 looks along -z; a positive yaw turns left

        def put(buttons):
            inp = vi.Input().mode(poses="set", buttons="set")
            for h, kw, side in ((vs.HAND_LEFT, None, -0.15), (vs.HAND_RIGHT, buttons, 0.15)):
                pose = vi.pose_from_ypr((fx * 0.45 + fz * side, 1.35, fz * 0.45 + fx * side), yaw_deg, 0)
                inp.hand(h, grip=pose, aim=pose, **(kw or {}))
            vi.write(inp)

        put(None)
        time.sleep(AIM_FIRST_S)
        put(right)
        time.sleep(secs)
        put(None)
        time.sleep(0.5)
        hands()

    def walk_stick(secs):
        inp = vi.Input().mode(poses="set", buttons="set")
        for h, kw, x in ((vs.HAND_LEFT, {"stick": (0.0, 1.0)}, -0.2), (vs.HAND_RIGHT, None, 0.2)):
            pose = vi.pose_from_ypr((x, 1.2, -0.3), 0, 0)
            inp.hand(h, grip=pose, aim=pose, **(kw or {}))
        vi.write(inp)
        time.sleep(secs)
        hands()

    saves = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "FalloutNV", "Saves")
    saves_copy = None
    if not a.stay:
        saves_copy = os.path.join(tempfile.mkdtemp(prefix="rung_simcheck_saves_"), "Saves")
        shutil.copytree(saves, saves_copy)          # copy2 underneath: dates kept, "newest save" stays the same one
    picked = sorted((f for f in glob.glob(os.path.join(saves, "*.fos")) if a.save.lower() in os.path.basename(f).lower()),
                    key=os.path.getmtime)
    if not picked:
        sys.exit(f"no save whose name contains '{a.save}'")
    bumped = [(f, os.path.getmtime(f)) for f in (picked[-1], picked[-1][:-4] + ".nvse") if os.path.isfile(f)]
    for f, _ in bumped:
        os.utime(f, None)                               # newest for the auto-load; the old date goes back after
    profile_before = mo2_profile(a.mo2)
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
        for f, t in bumped:
            os.utime(f, (t, t))
        print(f"{a.rung}: THE GAME NEVER STARTED (150 s)")
        mo2_profile(a.mo2, profile_before)
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
    panel = drawn = follows = through = walked = None
    still_a = still_b = still_out = still_walk = still_pause = None
    if loaded_save and running("FalloutNV.exe"):
        time.sleep(SETTLE_S)
        still_a = sim_picture()                     # no pause change first: the eye must be live by itself
        drawn = level(still_a)
        vb_sim.head(0, 1.7, 0, HEAD_YAW_DEG, 0)
        time.sleep(2.5)
        still_b = sim_picture()                     # the turned head, again with no pause change
        follows = diff(still_a, still_b)
        vb_sim.head(0, 1.7, 0, 0, 0)
        time.sleep(2.5)
        back = sim_picture()
        tap(left={"y": True})                       # pause: the mod's panel
        still_pause = sim_picture()
        panel = diff(back, still_pause)
        tap(right={"b": True})                      # un-pause
        if a.outside:
            vb_sim.head(0, 1.7, 0, DOOR_YAW_DEG, 0)
            time.sleep(2.5)
            inside = sim_picture()
            point_and_hold(DOOR_YAW_DEG, DOOR_HOLD_S, a=True)
            time.sleep(DOOR_LOAD_S)
            still_out = sim_picture()
            through = diff(inside, still_out)
            walk_stick(3.0)
            time.sleep(1.0)
            still_walk = sim_picture()
            walked = diff(still_out, still_walk)
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
    body = "solved" if "the body is solved from the headset" in text else "NOT SOLVED"
    hangs = len(re.findall(r"\[hang\] the game's main loop has not turned", text))
    warns = sorted(set(m[:110] for m in re.findall(r"(?:WARN|ERROR)\s+(.*)", text)
                       if "[hang]" not in m and CAMERA_COMPLAINT not in m and "64-bit" not in m and "body memory is not there" not in m))
    ok_plugins = off_plugins = 0
    try:
        with open(nvse, encoding="latin-1") as f:
            t = f.read()
        ok_plugins, off_plugins = len(re.findall(r"loaded correctly", t)), len(set(re.findall(r"plugin (\S+) .*disabled", t)))
    except OSError:
        pass
    if a.stay and up:
        print(f"{a.rung} in the simulator: UP AND LEFT RUNNING; body {body}; save loaded "
              f"{'yes after ' + str(load_s) + ' s' if loaded_save else 'NO'}; pause panel shows {said(panel, PANEL_CHANGED)}; "
              f"world drawn {said(drawn, WORLD_DRAWN)}; world follows the head {said(follows, HEAD_CHANGED)}. "
              f"MO2 was on '{profile_before}': put it back after the close.")
        return 0
    still_there = close_game()                      # last: the polite close also stops the simulator's session
    t2 = time.time()
    while time.time() - t2 < 30 and running("ModOrganizer.exe"):
        time.sleep(2)
    if not running("ModOrganizer.exe"):
        mo2_profile(a.mo2, profile_before)
    new_crashes = sorted(set(glob.glob(os.path.join(crash_dir, "*.log"))) - before)
    saves_note = ""
    if not still_there:
        for f, t in bumped:
            if os.path.isfile(f):
                os.utime(f, (t, t))
    if saves_copy and not still_there:
        saves_note = "; " + put_saves_back(saves, saves_copy, a.rung)
    print(f"{a.rung} in the simulator: {'UP' if up else 'GONE'}; VR system {backend} ({runtime}); body {body}; save loaded "
          f"{'yes after ' + str(load_s) + ' s' if loaded_save else 'NO'}; pause panel shows {said(panel, PANEL_CHANGED)}; "
          f"world drawn {said(drawn, WORLD_DRAWN)}; world follows the head {said(follows, HEAD_CHANGED)}; "
          + (f"through the door {said(through, THROUGH_DOOR)}; walks outside {said(walked, WALKED)}; " if a.outside else "") +
          f"add-ons loaded {ok_plugins}, disabled {off_plugins}; new crash logs {len(new_crashes)}; hang warnings {hangs}; "
          f"camera complaint {'YES' if CAMERA_COMPLAINT in text else 'no'}; "
          f"closed {'NO - THE GAME IS STILL RUNNING, close it by hand' if still_there else 'politely'}{saves_note}")
    for w in warns[:8]:
        print("    mod log:", w)
    kept = subprocess.run([sys.executable, os.path.join(HERE, "collect_run.py"), "--mo2", a.mo2, "--game", a.game,
                           "--rung", a.rung + " sim", "--since", since.strftime("%Y-%m-%d %H:%M")],
                          capture_output=True, text=True).stdout
    m = re.search(r"log\(s\) kept in (.+?); Windows errors", kept)
    if m and os.path.isdir(m.group(1)):
        for name, im in (("eye head straight.jpg", still_a), (f"eye head turned {HEAD_YAW_DEG}.jpg", still_b),
                         ("eye pause panel.jpg", still_pause),
                         ("eye outside.jpg", still_out), ("eye outside after walking.jpg", still_walk)):
            if im is not None:
                im.thumbnail((640, 640))
                im.save(os.path.join(m.group(1), name), quality=80)
    return 0 if up and loaded_save and not new_crashes and (drawn or 0) > WORLD_DRAWN else 1


if __name__ == "__main__":
    sys.exit(main())
