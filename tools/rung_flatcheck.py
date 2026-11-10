#!/usr/bin/env python3
"""rung_flatcheck.py -- a desk check of one FLAT rung profile: start the game through MO2 on that profile, wait, say
whether it is still up and what its logs say, save a small picture of its window, close it (the window's own close),
and keep the run's logs with collect_run.py.

    python rung_flatcheck.py --mo2 <Begin Again folder> --game <New Vegas folder> --rung "rung-02 fixes flat"
                             [--wait 80] [--shot <folder for the window picture>]

It says: up or gone, how many xNVSE plugins loaded / were disabled, whether a new crash log appeared. It does not
press anything: what the menu looks like (TTW's own warning boxes) is for the picture.
"""
import argparse
import ctypes
import datetime as dt
import glob
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def running(name):
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}"], capture_output=True, text=True).stdout
    return name.lower() in out.lower()


def exe_of(hwnd):
    """The program file name behind a window."""
    u, k = ctypes.windll.user32, ctypes.windll.kernel32
    pid = ctypes.c_ulong(0)
    u.GetWindowThreadProcessId(ctypes.c_void_p(hwnd), ctypes.byref(pid))
    h = k.OpenProcess(0x1000, False, pid.value)   # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    buf = ctypes.create_unicode_buffer(520)
    n = ctypes.c_ulong(520)
    ok = k.QueryFullProcessImageNameW(ctypes.c_void_p(h), 0, buf, ctypes.byref(n))
    k.CloseHandle(ctypes.c_void_p(h))
    return os.path.basename(buf.value) if ok else ""


def game_windows():
    """Every visible top-level window of FalloutNV.exe: [(hwnd, title)]. The game's own is titled "Fallout..."; any
    other is a box put up by the game or one of its add-ons."""
    u = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, _):
        if u.IsWindowVisible(hwnd) and exe_of(hwnd).lower() == "falloutnv.exe":
            n = u.GetWindowTextLengthW(hwnd)
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(hwnd, b, n + 1)
            found.append((hwnd, b.value))
        return True
    u.EnumWindows(cb, 0)
    return found


def game_window():
    for hwnd, title in game_windows():
        if title.startswith("Fallout"):
            return hwnd
    return None


def boxes():
    """Boxes the game is stopped on: [(title, text, hwnd of its OK button or None)]."""
    u = ctypes.windll.user32
    out = []
    for hwnd, title in game_windows():
        if title.startswith("Fallout") and "Error" not in title:
            continue
        texts, ok = [], [None]

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def cb(h, _):
            n = u.GetWindowTextLengthW(h)
            b = ctypes.create_unicode_buffer(n + 2)
            u.GetWindowTextW(h, b, n + 2)
            if b.value in ("OK", "Yes", "&Yes"):
                ok[0] = h
            elif b.value and b.value not in ("No", "&No", "Cancel"):
                texts.append(" ".join(b.value.split()))
            return True
        u.EnumChildWindows(ctypes.c_void_p(hwnd), cb, 0)
        out.append((title, " ".join(texts), ok[0]))
    return out


def grab(hwnd, out):
    """A small picture of that window's own contents (PrintWindow), saved as PNG. No focus change, no keys."""
    try:
        from PIL import Image
        import ctypes.wintypes as w
        u, g = ctypes.windll.user32, ctypes.windll.gdi32
        r = w.RECT()
        u.GetClientRect(ctypes.c_void_p(hwnd), ctypes.byref(r))
        W, H = r.right - r.left, r.bottom - r.top
        if W <= 0 or H <= 0:
            return False
        dc = u.GetDC(ctypes.c_void_p(hwnd))
        mdc = g.CreateCompatibleDC(ctypes.c_void_p(dc))
        bmp = g.CreateCompatibleBitmap(ctypes.c_void_p(dc), W, H)
        g.SelectObject(ctypes.c_void_p(mdc), ctypes.c_void_p(bmp))
        u.PrintWindow(ctypes.c_void_p(hwnd), ctypes.c_void_p(mdc), 3)
        class BMI(ctypes.Structure):
            _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16),
                        ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32), ("biSizeImage", ctypes.c_uint32),
                        ("a", ctypes.c_int32), ("b", ctypes.c_int32), ("c", ctypes.c_uint32), ("d", ctypes.c_uint32)]
        bi = BMI(ctypes.sizeof(BMI), W, -H, 1, 32, 0, 0, 0, 0, 0, 0)
        buf = ctypes.create_string_buffer(W * H * 4)
        g.GetDIBits(ctypes.c_void_p(mdc), ctypes.c_void_p(bmp), 0, H, buf, ctypes.byref(bi), 0)
        g.DeleteObject(ctypes.c_void_p(bmp)); g.DeleteDC(ctypes.c_void_p(mdc)); u.ReleaseDC(ctypes.c_void_p(hwnd), ctypes.c_void_p(dc))
        im = Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB")
        im.thumbnail((640, 640))
        im.save(out)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True); ap.add_argument("--game", required=True); ap.add_argument("--rung", required=True)
    ap.add_argument("--wait", type=float, default=80.0); ap.add_argument("--shot", default=None)
    a = ap.parse_args()
    if running("FalloutNV.exe") or running("ModOrganizer.exe"):
        sys.exit("the game or Mod Organizer is already running: close it first")
    since = dt.datetime.now()
    crash_dir = os.path.join(a.mo2, "overwrite", "Root", "Crash Logs")
    before = set(glob.glob(os.path.join(crash_dir, "*.log")))
    subprocess.Popen([os.path.join(a.mo2, "ModOrganizer.exe"), "-p", a.rung, "moshortcut://:Begin Again"], cwd=a.mo2)
    t0 = time.time()
    while time.time() - t0 < 150 and not running("FalloutNV.exe"):
        time.sleep(2)
    if not running("FalloutNV.exe"):
        print(f"{a.rung}: THE GAME NEVER STARTED (150 s)")
        return 2
    started = time.time()
    while time.time() - started < a.wait and running("FalloutNV.exe"):
        time.sleep(3)
    # boxes on the way (an add-on's complaint, TTW's missing-plugin question): read, noted, answered OK / Yes by
    # message so the start goes on, up to 6 of them
    seen_boxes = []
    for _ in range(6):
        bs = boxes()
        if not bs:
            break
        for title, text, ok in bs:
            seen_boxes.append(f"[{title}] {text}"[:300])
            if ok:
                ctypes.windll.user32.PostMessageW(ctypes.c_void_p(ok), 0x00F5, 0, 0)
        time.sleep(6)
    if seen_boxes:
        time.sleep(15)
    up = running("FalloutNV.exe")
    new_crashes = sorted(set(glob.glob(os.path.join(crash_dir, "*.log"))) - before)
    loaded = disabled = 0
    nvse = os.path.join(a.mo2, "overwrite", "Root", "nvse.log")
    try:
        text = open(nvse, encoding="latin-1").read()
        loaded = len(re.findall(r"loaded correctly", text)) // 2 or len(re.findall(r"loaded correctly", text))
        disabled = len(set(re.findall(r"plugin (\S+) .*disabled", text)))
    except OSError:
        pass
    shot = ""
    hwnd = game_window()
    if up and hwnd and a.shot:
        os.makedirs(a.shot, exist_ok=True)
        out = os.path.join(a.shot, re.sub(r"[^A-Za-z0-9]+", "-", a.rung) + ".png")
        if grab(hwnd, out):
            shot = out
    # closing: the window's own close first; this engine ignores it at its main menu (seen 2026-11-10), so then the
    # game's own console command, typed INTO THAT WINDOW by message (never as real keys: those go to whatever is in
    # front): ` then qqq then Enter
    if up and hwnd:
        u = ctypes.windll.user32
        u.PostMessageW(ctypes.c_void_p(hwnd), 0x0010, 0, 0)
        t1 = time.time()
        while time.time() - t1 < 12 and running("FalloutNV.exe"):
            time.sleep(2)
    if running("FalloutNV.exe"):
        # nothing typed anywhere: the last resort is asked of the operating system for THIS program only, and said so
        subprocess.run(["taskkill", "/IM", "FalloutNV.exe"], capture_output=True)   # a polite close request (no /F)
        t1 = time.time()
        while time.time() - t1 < 15 and running("FalloutNV.exe"):
            time.sleep(2)
    forced = False
    if running("FalloutNV.exe"):
        subprocess.run(["taskkill", "/F", "/IM", "FalloutNV.exe"], capture_output=True)
        forced = True
        time.sleep(3)
    closed = not running("FalloutNV.exe")
    t2 = time.time()
    while time.time() - t2 < 30 and running("ModOrganizer.exe"):
        time.sleep(2)
    subprocess.run([sys.executable, os.path.join(HERE, "collect_run.py"), "--mo2", a.mo2, "--game", a.game, "--rung", a.rung,
                    "--since", since.strftime("%Y-%m-%d %H:%M:%S")], capture_output=True)
    verdict = "UP after %d s" % a.wait if up else "GONE before %d s (crashed or quit)" % a.wait
    print(f"{a.rung}: {verdict}; xNVSE plugins loaded {loaded}, disabled {disabled}; new crash logs {len(new_crashes)}; "
          f"{('ended by the system (it ignored its window close)' if forced else 'closed by its window') if closed else 'DID NOT CLOSE'}" + (f"; picture {shot}" if shot else ""))
    for b in seen_boxes:
        print("    BOX: " + b)
    return 0 if (up and not new_crashes and disabled == 0 and not seen_boxes) else 1


if __name__ == "__main__":
    sys.exit(main())
