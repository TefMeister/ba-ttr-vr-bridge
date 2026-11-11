#!/usr/bin/env python3
"""ttwvr_gates.py -- read (never write) the switches TTWVR's stereo frame waits for, from the running game.

    python ttwvr_gates.py            one reading
    python ttwvr_gates.py --watch 10 a reading every second for 10 s (only lines that changed)

Why: on a desk run in the OpenXR Simulator the game draws the world but the VR mod's two eye pictures stay empty
(modding-notes/2026-11-11-why-no-3d-world-in-the-simulator.md). Its stereo frame only runs when its state is 4 and
four switches are on; this prints them, so one run says which one is off. Read-only: the process is opened for
reading alone. The places are those of TTWVR 1.0.0 build 6AF014A8 (KUPOkinz's work; found by reading the DLL on disk).
It checks a known piece of text first and refuses on any other build rather than print wrong numbers.
"""
import ctypes
import ctypes.wintypes as w
import struct
import subprocess
import sys
import time

PREFERRED = 0x10000000                      # the DLL's own base; everything below is relative to it
KNOWN_TEXT = (0x108F5CF0, b"the stereo frame drew the world")
VR = 0x1152CE78                             # the mod's VR object
CFG = 0x10E77408                            # the mod's settings
BYTES = [                                   # (name, where, offset, what it means when known)
    ("stereo switch A", "abs", 0x1122EDF7, "set by the world step once the player and scene are ready"),
    ("stereo switch B", "abs", 0x1122ECB8, ""),
    ("switch B helper", "abs", 0x1122ECB9, ""),
    ("vr +0xae8 (stereo allowed)", "vr", 0xAE8, "needs settings +0x7c, a game check, vr +0x148, and vr +0xb5c off"),
    ("vr +0x148", "vr", 0x148, ""), ("vr +0x146", "vr", 0x146, ""),
    ("vr +0xb5c", "vr", 0xB5C, "must be 0"), ("vr +0xb68", "vr", 0xB68, ""), ("vr +0xb75", "vr", 0xB75, ""),
    ("vr +0xc6e", "vr", 0xC6E, ""), ("vr +0x1a58", "vr", 0x1A58, ""),
    ("settings +0x7c", "cfg", 0x7C, ""), ("settings +0x7d", "cfg", 0x7D, ""), ("settings +0x7e", "cfg", 0x7E, ""),
    ("settings +0x8d (one draw for both eyes)", "cfg", 0x8D, ""),
    ("Full Body", "cfg", 0x23C, "1 = on"), ("Full Body parked", "cfg", 0x38, "1 = parked off (player scale under 0.6)"),
]
DWORDS = [("vr state +0xae4", "vr", 0xAE4, "4 = the stereo frame may run; 5, 1, 3 = menu / loading kinds"),
          ("vr first field", "vr", 0x0, "0 = the world step leaves at once")]


def attach():
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    ps = ctypes.WinDLL("psapi", use_last_error=True)
    k.OpenProcess.restype = w.HANDLE
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq FalloutNV.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    rows = [l for l in out.splitlines() if "FalloutNV" in l]
    if not rows:
        sys.exit("the game is not running")
    h = k.OpenProcess(0x0410, False, int(rows[0].split('","')[1]))      # query + read, nothing else
    mods, need, name = (w.HMODULE * 2048)(), w.DWORD(), ctypes.create_unicode_buffer(520)
    ps.EnumProcessModulesEx(w.HANDLE(h), mods, ctypes.sizeof(mods), ctypes.byref(need), 3)
    base = None
    for i in range(need.value // ctypes.sizeof(w.HMODULE)):
        if mods[i]:
            ps.GetModuleBaseNameW(w.HANDLE(h), w.HMODULE(mods[i]), name, 520)
            if name.value.lower() == "ttwvr.dll":
                base = mods[i]
    if base is None:
        sys.exit("TTWVR.dll is not loaded in the game")

    def rd(va, n):
        b, got = ctypes.create_string_buffer(n), ctypes.c_size_t()
        ok = k.ReadProcessMemory(w.HANDLE(h), ctypes.c_void_p(va - PREFERRED + base), b, n, ctypes.byref(got))
        return b.raw if ok else None
    if rd(KNOWN_TEXT[0], len(KNOWN_TEXT[1])) != KNOWN_TEXT[1]:
        sys.exit("this is not TTWVR 1.0.0 build 6AF014A8: the places are unknown for it, nothing read")
    return rd


def reading(rd):
    where = {"abs": 0, "vr": VR, "cfg": CFG}
    out = []
    for name, kind, off, note in DWORDS:
        b = rd(where[kind] + off, 4)
        out.append((name, struct.unpack("<I", b)[0] if b else None, note))
    for name, kind, off, note in BYTES:
        b = rd(where[kind] + off, 1)
        out.append((name, b[0] if b else None, note))
    return out


def main():
    rd = attach()
    watch = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--watch" else 0
    last, t0 = {}, time.time()
    while True:
        for name, val, note in reading(rd):
            if last.get(name) != val:
                print(f"{time.strftime('%H:%M:%S')}  {name:42s} {val}" + (f"   ({note})" if note and name not in last else ""))
                last[name] = val
        if time.time() - t0 >= watch:
            return 0
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
