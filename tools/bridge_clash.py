"""bridge_clash.py -- one game at a time on this PC: the Lanes clash guard for our Fallout launch tools (2026-11-14).

Asked for on Tefa's behalf by the session watching this PC, after The Darkness's desk runs and Tefa's Fallout headset
runs nearly overlapped (VR Bench presses buttons into whatever game is up). rung_simcheck.py runs `clash.py check live`
and refuses on exit 1, then holds the lock with `clash.py take live ba-ttr-vr-bridge`, and gives it back once the game
is closed, only when it took the lock itself (a marker file), so it never frees a session's own /lm or /ms lock.
rung_repeat.sh takes it once for the whole series and tells each start so through BRIDGE_CLASH_TAKEN=1.

    import bridge_clash; bridge_clash.take_or_exit()   # before the launch
    import bridge_clash; bridge_clash.release()        # after the game is closed
    python bridge_clash.py take|release                # the same, for a shell script
"""
import os, subprocess, sys, tempfile

CLASH = os.path.expanduser("~/github-backups/_lanes-next-wt/plugins/lanes/tools/clash.py")
PROJECT = "ba-ttr-vr-bridge"
MARKER = os.path.join(tempfile.gettempdir(), "bridge_clash_taken.txt")
TAKEN_ENV = "BRIDGE_CLASH_TAKEN"   # set by a caller that already holds the lock for us


def take_or_exit():
    if os.environ.get(TAKEN_ENV) == "1":
        return
    if not os.path.isfile(CLASH):
        sys.exit("refused: the Lanes clash guard is not at " + CLASH + "; nothing launched")
    r = subprocess.run([sys.executable, CLASH, "check", "live", PROJECT], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout.strip() or r.stderr.strip(), flush=True)
        sys.exit("refused: another game holds this PC (clash.py check live); nothing launched")
    r = subprocess.run([sys.executable, CLASH, "take", "live", PROJECT], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout.strip() or r.stderr.strip(), flush=True)
        sys.exit("refused: could not take the one-game lock; nothing launched")
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def release():
    if os.environ.get(TAKEN_ENV) == "1" or not os.path.exists(MARKER):
        return
    subprocess.run([sys.executable, CLASH, "release", "live", PROJECT], capture_output=True, text=True)
    os.remove(MARKER)
    print("one-game lock: given back", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "take":
        take_or_exit()
        print("one-game lock: taken", flush=True)
    elif cmd == "release":
        release()
    else:
        sys.exit(__doc__)
