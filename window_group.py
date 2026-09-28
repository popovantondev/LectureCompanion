"""Move the companion's native windows together without touching their Z order."""
import ctypes as c
from ctypes import wintypes as w


class WindowGroup:
    def __init__(self):
        self.u = c.windll.user32
        self.g = c.windll.gdi32
        self.u.GetParent.argtypes = [w.HWND]
        self.u.GetParent.restype = w.HWND
        self.u.BeginDeferWindowPos.argtypes = [c.c_int]
        self.u.BeginDeferWindowPos.restype = w.HANDLE
        self.u.DeferWindowPos.argtypes = [w.HANDLE, w.HWND, w.HWND, c.c_int, c.c_int, c.c_int, c.c_int, w.UINT]
        self.u.DeferWindowPos.restype = w.HANDLE
        self.u.EndDeferWindowPos.argtypes = [w.HANDLE]
        self.u.SetWindowPos.argtypes = [w.HWND, w.HWND, c.c_int, c.c_int, c.c_int, c.c_int, w.UINT]
        self.u.SetWindowRgn.argtypes = [w.HWND, w.HRGN, w.BOOL]
        self.g.CreateRoundRectRgn.argtypes = [c.c_int]*6
        self.g.CreateRoundRectRgn.restype = w.HRGN
        self.g.DeleteObject.argtypes = [w.HANDLE]
        self.positions = {}
        self.regions = {}
        self.chrome_removed = set()
        self.move_batches = 0

    def handle(self, window):
        return self.u.GetParent(window.winfo_id()) or window.winfo_id()

    def remove_chrome(self,window):
        """Tk override-redirect still gets a Windows nonclient edge on some builds."""
        if window in self.chrome_removed:return
        hwnd=self.handle(window)
        self.u.GetWindowLongW.argtypes=[w.HWND,c.c_int];self.u.GetWindowLongW.restype=w.LONG
        self.u.SetWindowLongW.argtypes=[w.HWND,c.c_int,w.LONG];self.u.SetWindowLongW.restype=w.LONG
        style=self.u.GetWindowLongW(hwnd,-16)
        self.u.SetWindowLongW(hwnd,-16,style & ~(0x00800000|0x00400000|0x00040000))
        for attribute,value in [(2,1),(33,1),(34,0xfffffffe)]:
            option=w.DWORD(value)
            c.windll.dwmapi.DwmSetWindowAttribute(w.HWND(hwnd),attribute,c.byref(option),4)
        self.u.SetWindowPos(hwnd,None,0,0,0,0,0x1|0x2|0x4|0x10|0x20|0x200)
        self.chrome_removed.add(window)

    def move(self, placements):
        changed = [(win, tuple(map(round, rect))) for win, rect in placements
                   if self.positions.get(win) != tuple(map(round, rect))]
        if not changed:
            return
        for win,(x,y,width,height) in changed:
            previous=self.positions.get(win)
            if previous is None or previous[2:]!=(width,height) or win.state()=='withdrawn':
                # Keep Tk's requested size in sync. Otherwise a deferred Tk
                # geometry request can undo a native auto-grow one frame later.
                # Pure dragging never calls wm_geometry and never resizes.
                win.geometry(f'{width}x{height}+{x}+{y}')
        # NOZORDER | NOACTIVATE | NOOWNERZORDER. In particular, never lift here.
        flags = 0x4 | 0x10 | 0x200
        batch = self.u.BeginDeferWindowPos(len(changed))
        for win, (x, y, width, height) in changed:
            if batch:
                batch = self.u.DeferWindowPos(batch, self.handle(win), None, x, y, width, height, flags)
        if not batch or not self.u.EndDeferWindowPos(batch):
            for win, (x, y, width, height) in changed:
                self.u.SetWindowPos(self.handle(win), None, x, y, width, height, flags)
        self.positions.update(changed)
        self.move_batches += 1

    def show(self,window):
        # Mapping a Tk window restores its last wm_geometry, not necessarily its
        # last native drag position. Synchronize only at this visibility change.
        rect=self.positions.get(window)
        if rect:
            x,y,width,height=rect
            window.geometry(f'{width}x{height}+{x}+{y}')
        window.deiconify()

    def rounded(self, window, width, height, radius=22):
        self.remove_chrome(window)
        key = (round(width), round(height), radius)
        if self.regions.get(window) == key:
            return
        region = self.g.CreateRoundRectRgn(0, 0, key[0]+1, key[1]+1, radius*2, radius*2)
        if not self.u.SetWindowRgn(self.handle(window), region, True):
            self.g.DeleteObject(region)
        self.regions[window] = key

    def stack(self, windows):
        """Only after a visibility change, from back to front, without activation."""
        for win in windows:
            if win.state() != 'withdrawn':
                self.u.SetWindowPos(self.handle(win), w.HWND(-1), 0, 0, 0, 0, 0x1 | 0x2 | 0x10)


def deck_layout(x, y, card_height, input_height, screen_width, screen_height, width=470, input_width=620):
    """Pure placement: the input stays below the pet; the deck avoids both."""
    x = max(8, min(x, screen_width-136))
    y = max(8, min(y, screen_height-148-12-input_height-12))
    left = max(8, min(x+64-width//2, screen_width-width-8))
    cy = y+160
    above = y-card_height-14
    below = cy+input_height+18+72
    if above >= 80:
        fx, fy = left, above
    elif below+card_height <= screen_height-8:
        fx, fy = left, below
    else:
        # At the middle of a short screen, use the free side of the mascot.
        right_room = screen_width-(x+128)
        fx = x+148 if right_room >= width+20 else x-width-20
        fx = max(8, min(fx, screen_width-width-8))
        fy = max(80, min(y-card_height//2, screen_height-card_height-8))
        # Keep the side deck above the composer even if the input reaches sideways.
        if fy+card_height > cy-12:
            fy = max(80, cy-12-card_height)
    input_left=max(8,min(x+64-input_width//2,screen_width-input_width-8))
    return (x,y,128,148), (fx,fy,width,card_height), (input_left,cy,input_width,input_height)
