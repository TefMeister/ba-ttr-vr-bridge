#!/usr/bin/env python3
"""console_type.py -- type console lines into the running game, and ONLY into its own window.

    python console_type.py                      list FalloutNV.exe's windows
    python console_type.py "player.moveto SpringvaleElementaryMapMarker" "player.setangle z 121"

Each line: the console key, the text, Enter, the console key again. Refuses to type unless the game's own
"Fallout: New Vegas" window is in front: the OpenXR Simulator's preview window lives in the same program, and on
2026-11-13 keys meant for the console reached it and changed its view settings.
In a simulator run set the simulator's "input_polling" to "preview" first (settings.json, game closed) and back to
"app" after: otherwise the simulator also reads W/A/S/D/Q/E/I/J/K/L off the keyboard and the head moves.
"""
import ctypes, ctypes.wintypes as w, sys, time, subprocess
u = ctypes.WinDLL("user32", use_last_error=True)
pid = int([l for l in subprocess.run(["tasklist","/FI","IMAGENAME eq FalloutNV.exe","/FO","CSV","/NH"],capture_output=True,text=True).stdout.splitlines() if "FalloutNV" in l][0].split('","')[1])
wins = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, l):
    p = w.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid and u.IsWindowVisible(h):
        t = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, t, 256)
        c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
        wins.append((h, t.value, c.value))
    return True
u.EnumWindows(cb, 0)
for x in wins: print(x)
if len(sys.argv) < 2: sys.exit()
game = [x for x in wins if "simulator" not in x[1].lower() and "openxr" not in x[1].lower()][0]
print("using", game)
class KI(ctypes.Structure): _fields_=[("wVk",w.WORD),("wScan",w.WORD),("dwFlags",w.DWORD),("time",w.DWORD),("dwExtraInfo",ctypes.c_size_t)]
class IN(ctypes.Structure): _fields_=[("type",w.DWORD),("ki",KI),("pad",ctypes.c_byte*8)]
def key(sc, up=False):
    i = IN(1, KI(0, sc, 0x8 | (0x2 if up else 0), 0, 0)); u.SendInput(1, ctypes.byref(i), ctypes.sizeof(IN))
def tap(sc, shift=False):
    if shift: key(0x2A)
    key(sc); time.sleep(0.06); key(sc, True)
    if shift: key(0x2A, True)
    time.sleep(0.09)
SC = {c: s for s, c in enumerate("1234567890-=", 2)}
SC.update({c: s for c, s in zip("qwertyuiop[]", range(0x10, 0x1C))}); SC.update({c: s for c, s in zip("asdfghjkl;'", range(0x1E, 0x29))})
SC.update({c: s for c, s in zip("zxcvbnm,./", range(0x2C, 0x36))}); SC[" "] = 0x39
def typ(s):
    for ch in s:
        if ch.isupper(): tap(SC[ch.lower()], True)
        elif ch == '"': tap(0x28, True)
        elif ch == ':': tap(0x27, True)   # 2026-11-13: shift + ; (SetNumericINISetting "bUseWaterDepth:Water" 1)
        elif ch == '_': tap(0x0C, True)   # shift + -
        else: tap(SC[ch])
for _ in range(3):
    u.keybd_event(0x12, 0, 0, 0); u.keybd_event(0x12, 0, 2, 0)
    u.ShowWindow(game[0], 5); u.BringWindowToTop(game[0]); u.SetForegroundWindow(game[0]); time.sleep(0.8)
    if u.GetForegroundWindow() == game[0]: break
fg = u.GetForegroundWindow()
fg = u.GetForegroundWindow(); p = w.DWORD(); u.GetWindowThreadProcessId(fg, ctypes.byref(p))
if fg != game[0]: sys.exit("the game window itself is not in front; nothing typed")
for line in sys.argv[1:]:
    tap(0x29); time.sleep(0.6); typ(line); time.sleep(0.2); tap(0x1C); time.sleep(0.8); tap(0x29); time.sleep(1.5)
print("typed", len(sys.argv)-1)
