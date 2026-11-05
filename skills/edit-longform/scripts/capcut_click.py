"""Physical-pixel click for CapCut: click.py [dbl] X Y. Refuses unless CapCut is the foreground window and (X, Y) is
inside it (2026-10-28: the Spectre moved, a stale coordinate fell off every monitor, Windows clamped the cursor to
(0, 20) and the click landed on the main screen)."""
import ctypes, sys, time, subprocess
from ctypes import wintypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
subprocess.run(["uv", "run", "python", "scripts/capcut_drive.py", "activate"], cwd=r"%USERPROFILE%\Code\capcut-cli", capture_output=True)
fg = u.GetForegroundWindow()
n = ctypes.create_unicode_buffer(256); u.GetWindowTextW(fg, n, 256)
if "CapCut" not in n.value:
    sys.exit(f"ABORT: foreground is {n.value!r}")
args = sys.argv[1:]; dbl = args[0] == "dbl"
x, y = int(args[-2]), int(args[-1])
# the foreground "CapCut" can be a hidden helper window, so the point is checked against CapCut's VISIBLE windows
vis = []
@ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
def _cb(h, l):
    t = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, t, 256)
    if "CapCut" in t.value and u.IsWindowVisible(h):
        rr = wintypes.RECT(); u.GetWindowRect(h, ctypes.byref(rr)); vis.append((rr.left, rr.top, rr.right, rr.bottom))
    return True
u.EnumWindows(_cb, 0)
if not any(a <= x < c and b <= y < d for a, b, c, d in vis):
    sys.exit(f"ABORT: ({x}, {y}) is outside every visible CapCut window {vis}; re-grab and recompute")
u.SetCursorPos(x, y); time.sleep(0.15)
pt = wintypes.POINT(); u.GetCursorPos(ctypes.byref(pt))
if (pt.x, pt.y) != (x, y):
    sys.exit(f"ABORT: the cursor landed at ({pt.x}, {pt.y}), not ({x}, {y})")
for _ in range(2 if dbl else 1):
    u.mouse_event(2, 0, 0, 0, 0); time.sleep(0.02); u.mouse_event(4, 0, 0, 0, 0); time.sleep(0.03)
pt = wintypes.POINT(); u.GetCursorPos(ctypes.byref(pt)); print("clicked", pt.x, pt.y)
