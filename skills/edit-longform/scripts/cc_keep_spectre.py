"""Keep every CapCut window on the Spectre = the LEFT-MOST monitor, found at run time (the layout changed mid-session
on 2026-10-23: the Spectre moved from -3840,5 to -3782,2144, and a hard-coded rect made the watcher fight Windows).
Polls every 15 ms; a visible CapCut top-level window wider than 600 px whose centre is on another monitor is restored,
moved there and maximized. A window that has needed 3 moves is left alone (no tug-of-war). usage: [seconds=600]"""
import ctypes, sys, time
import ctypes.wintypes as W
u = ctypes.windll.user32; k = ctypes.windll.kernel32
ctypes.windll.shcore.SetProcessDpiAwareness(2)
def spectre():
    mons = []
    def mcb(hm, hdc, lp, _):
        class MI(ctypes.Structure): _fields_ = [("cb", W.DWORD), ("rc", W.RECT), ("wk", W.RECT), ("f", W.DWORD)]
        mi = MI(); mi.cb = ctypes.sizeof(MI); u.GetMonitorInfoW(hm, ctypes.byref(mi)); r = mi.rc
        mons.append((r.left, r.top, r.right, r.bottom)); return True
    u.EnumDisplayMonitors(0, 0, ctypes.WINFUNCTYPE(ctypes.c_bool, W.HMONITOR, W.HDC, ctypes.POINTER(W.RECT), W.LPARAM)(mcb), 0)
    return min(mons, key=lambda m: m[0])
SPECTRE = spectre()
tries = {}
names = {}
def exe(pid):
    if pid not in names:
        h = k.OpenProcess(0x1000, False, pid); buf = ctypes.create_unicode_buffer(260); n = W.DWORD(260)
        names[pid] = buf.value.lower() if h and k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) else ""
        if h: k.CloseHandle(h)
    return names[pid]
moved = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, W.HWND, W.LPARAM)
def cb(h, _):
    if not u.IsWindowVisible(h) or u.GetParent(h):
        return True
    pid = W.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if not exe(pid.value).endswith("capcut.exe"):
        return True
    r = W.RECT(); u.GetWindowRect(h, ctypes.byref(r))
    if r.right - r.left < 600:
        return True
    cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
    if not (SPECTRE[0] <= cx < SPECTRE[2] and SPECTRE[1] - 40 <= cy < SPECTRE[3]):
        if u.IsIconic(h) or tries.get(h, 0) >= 3:
            return True
        tries[h] = tries.get(h, 0) + 1
        u.ShowWindow(h, 9)                                    # restore
        u.SetWindowPos(h, 0, SPECTRE[0] + 60, SPECTRE[1] + 60, 1700, 950, 0x0014)   # NOZORDER | NOACTIVATE
        u.ShowWindow(h, 3)                                    # maximize on the Spectre
        t = ctypes.create_unicode_buffer(200); u.GetWindowTextW(h, t, 200)
        print(f"{time.strftime('%H:%M:%S')} moved {t.value!r} from {(r.left, r.top, r.right, r.bottom)}", flush=True)
        moved.append(h)
    return True
end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 600)
print("watching; Spectre =", SPECTRE, flush=True)
last = time.time()
while time.time() < end:
    if time.time() - last > 1.0:             # the layout can change mid-session (2026-10-23, twice): re-read it
        sp = spectre(); last = time.time()
        if sp != SPECTRE:
            SPECTRE = sp; tries.clear(); print("layout changed; Spectre =", SPECTRE, flush=True)
    u.EnumWindows(cb, 0)
    time.sleep(0.015)
print("watch over", flush=True)
