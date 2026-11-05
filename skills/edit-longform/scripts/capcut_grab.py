import ctypes, sys
from ctypes import wintypes
from PIL import ImageGrab
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
vx, vy = u.GetSystemMetrics(76), u.GetSystemMetrics(77)   # virtual screen origin
im = ImageGrab.grab(all_screens=True)
# CapCut window rect (largest visible window titled CapCut)
res = []
@ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
def cb(h, l):
    n = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, n, 256)
    if u.IsWindowVisible(h) and "CapCut" in n.value:
        r = wintypes.RECT(); u.GetWindowRect(h, ctypes.byref(r)); res.append((r.right - r.left) * (r.bottom - r.top) and (r.left, r.top, r.right, r.bottom))
    return True
u.EnumWindows(cb, 0)
l, t, r, b = max((x for x in res if x), key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))
crop = im.crop((l - vx, t - vy, r - vx, b - vy))
crop.resize((crop.width // 3, crop.height // 3)).save(sys.argv[1])
print("window", l, t, r, b, "saved at 1/3")
