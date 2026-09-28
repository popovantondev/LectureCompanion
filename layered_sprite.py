"""Per-pixel transparent Windows mascot surface; original artwork stays unchanged."""
import ctypes as c
from ctypes import wintypes as w
from PIL import Image,ImageDraw,ImageFilter
import math
from binary_visor import BinaryVisor

class Info(c.Structure):
    _fields_=[('size',w.DWORD),('width',w.LONG),('height',w.LONG),('planes',w.WORD),('bits',w.WORD),('compression',w.DWORD),('image_size',w.DWORD),('xppm',w.LONG),('yppm',w.LONG),('used',w.DWORD),('important',w.DWORD)]
class Blend(c.Structure):
    _fields_=[('op',c.c_ubyte),('flags',c.c_ubyte),('alpha',c.c_ubyte),('format',c.c_ubyte)]

class LayeredSprite:
    def __init__(self,root,source,size=(128,148)):
        self.width,self.height=size
        self.root=root;self.source=source.convert('RGBA').copy();self.source.thumbnail((124,140),Image.Resampling.LANCZOS)
        self.base_frames={};self.visor=BinaryVisor()
        u,g=c.windll.user32,c.windll.gdi32;self.u=u;self.g=g
        u.GetParent.argtypes=[w.HWND];u.GetParent.restype=w.HWND
        u.GetWindowLongW.argtypes=[w.HWND,c.c_int];u.GetWindowLongW.restype=w.LONG
        u.SetWindowLongW.argtypes=[w.HWND,c.c_int,w.LONG];u.SetWindowLongW.restype=w.LONG
        g.CreateCompatibleDC.argtypes=[w.HDC];g.CreateCompatibleDC.restype=w.HDC
        g.CreateDIBSection.argtypes=[w.HDC,c.POINTER(Info),w.UINT,c.POINTER(c.c_void_p),w.HANDLE,w.DWORD];g.CreateDIBSection.restype=w.HBITMAP
        g.SelectObject.argtypes=[w.HDC,w.HANDLE];g.SelectObject.restype=w.HANDLE
        g.DeleteObject.argtypes=[w.HANDLE];g.DeleteDC.argtypes=[w.HDC]
        u.UpdateLayeredWindow.argtypes=[w.HWND,w.HDC,c.POINTER(w.POINT),c.POINTER(w.SIZE),w.HDC,c.POINTER(w.POINT),w.DWORD,c.POINTER(Blend),w.DWORD]
        root.wm_attributes('-transparentcolor','');root.update_idletasks()
        self.hwnd=u.GetParent(root.winfo_id()) or root.winfo_id()
        style=u.GetWindowLongW(self.hwnd,-20);u.SetWindowLongW(self.hwnd,-20,style & ~0x80000);u.SetWindowLongW(self.hwnd,-20,style|0x80000|0x80)
        self.dc=g.CreateCompatibleDC(None);self.bits=c.c_void_p();info=Info(40,self.width,-self.height,1,32,0,self.width*self.height*4,0,0,0,0)
        self.bitmap=g.CreateDIBSection(self.dc,c.byref(info),0,c.byref(self.bits),None,0)
        if not self.bitmap:raise OSError('Cannot create mascot surface')
        self.previous=g.SelectObject(self.dc,self.bitmap);self.paint()
        root.bind('<Destroy>',lambda e:self.close() if e.widget==root else None,add='+')

    def paint(self,offset=0,processing=False,phase=0,closed=False):
        if offset not in self.base_frames:
            frame=Image.new('RGBA',(128,148));shadow=Image.new('RGBA',frame.size)
            spread=abs(offset);ImageDraw.Draw(shadow).ellipse((35-spread,139,93+spread,145),fill=(45,65,90,round(45-spread*3)))
            frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
            body=Image.new('RGBA',frame.size)
            body.alpha_composite(self.source,((128-self.source.width)//2,69-self.source.height//2))
            if offset:body=body.transform(body.size,Image.Transform.AFFINE,(1,0,0,0,1,-offset),Image.Resampling.BICUBIC)
            frame.alpha_composite(body)
            self.base_frames[offset]=frame
        frame=self.base_frames[offset].copy()
        if processing:
            frame.alpha_composite(self.visor.render(phase,offset))
        elif closed:
            draw=ImageDraw.Draw(frame);y=43+offset
            for i,x in enumerate((51,77)):
                draw.ellipse((x-7,y-12,x+7,y+12),fill='#151B23')
                if closed:draw.line((x-4,y,x+4,y),fill='#8EE7FF',width=2)
                else:
                    pulse=2+2*(1+math.sin(phase+i*.7));draw.ellipse((x-3,y-pulse,x+3,y+pulse),fill='#73DAFF')
        self.paint_frame(frame)

    def paint_frame(self,frame):
        if frame.size!=(self.width,self.height):frame=frame.resize((self.width,self.height),Image.Resampling.LANCZOS)
        r,g,b,a=frame.convert('RGBa').split();raw=Image.merge('RGBA',(b,g,r,a)).tobytes();c.memmove(self.bits,raw,len(raw))
        dst=w.POINT(self.root.winfo_x(),self.root.winfo_y());src=w.POINT(0,0);size=w.SIZE(self.width,self.height);blend=Blend(0,0,255,1)
        # Preserve the actual native position. Tk can report the previous position
        # briefly after a drag; reapplying it here would make the mascot jump.
        if not self.u.UpdateLayeredWindow(self.hwnd,None,None,c.byref(size),self.dc,c.byref(src),0,c.byref(blend),2):
            raise OSError('Cannot display transparent mascot')

    def close(self):
        if self.dc:
            self.g.SelectObject(self.dc,self.previous);self.g.DeleteObject(self.bitmap);self.g.DeleteDC(self.dc);self.dc=None
