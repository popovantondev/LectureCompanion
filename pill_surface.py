"""Antialiased pearl input shell. Animation changes pixels, not native window size."""
import tkinter as tk
import time
from collections import OrderedDict
from PIL import Image,ImageDraw,ImageFilter
from layered_sprite import LayeredSprite


class PillSurface(LayeredSprite):
    PAD=12
    def __init__(self,owner,width=620,max_height=196):
        self.window=tk.Toplevel(owner);self.window.overrideredirect(True)
        self.window.attributes('-topmost',True);self.window.withdraw()
        self.full_width=width;self.max_height=max_height
        self.frame_cache=OrderedDict();self.mask_cache={};self.current_key=None
        self.render_ms=[]
        self.window.geometry(f'{width+24}x{max_height+24}+0+0')
        super().__init__(self.window,Image.new('RGBA',(1,1)),size=(width+24,max_height+24))
        # Precompute the opening frames once. No blur or resizing on hover.
        self.opening=[]
        for index in range(16):
            fraction=1-(1-index/15)**3
            self.opening.append(self.frame(round(44+(width-44)*fraction),round(44+12*fraction)))

    def mask(self,width,height):
        radius=min(28,height//2)
        key=(width,height,radius)
        if key not in self.mask_cache:
            scale=3
            mask=Image.new('L',(width*scale,height*scale))
            ImageDraw.Draw(mask).rounded_rectangle((0,0,width*scale-1,height*scale-1),radius=radius*scale,fill=255)
            self.mask_cache[key]=mask.resize((width,height),Image.Resampling.LANCZOS)
            if len(self.mask_cache)>40:self.mask_cache.pop(next(iter(self.mask_cache)))
        return self.mask_cache[key]

    def frame(self,width,height):
        key=(width,height)
        if key in self.frame_cache:
            self.frame_cache.move_to_end(key);return self.frame_cache[key]
        mask=self.mask(width,height)
        frame=Image.new('RGBA',(self.full_width+24,self.max_height+24))
        x=self.PAD+(self.full_width-width)//2;y=self.PAD
        shadow_mask=Image.new('L',frame.size);shadow_mask.paste(mask,(x,y+3))
        shadow=Image.new('RGBA',frame.size,(32,55,82,0))
        shadow.putalpha(shadow_mask.filter(ImageFilter.GaussianBlur(5)).point(lambda a:a*32//255))
        frame.alpha_composite(shadow)
        scale=3;face=Image.new('RGBA',(width*scale,height*scale))
        ImageDraw.Draw(face).rounded_rectangle((0,0,width*scale-1,height*scale-1),radius=min(28,height//2)*scale,fill='#FAFBFD',outline='#DCE3EB',width=scale)
        face=face.resize((width,height),Image.Resampling.LANCZOS)
        frame.alpha_composite(face,(x,y));self.frame_cache[key]=frame
        if len(self.frame_cache)>40:self.frame_cache.popitem(last=False)
        return frame

    def paint(self,*args):
        # Called by LayeredSprite during native surface construction.
        self.paint_frame(self.frame(self.full_width,56))

    def show_shape(self,height,fraction=1):
        if fraction<1 and height==56:
            index=min(14,round((1-(1-fraction)**(1/3))*15))
            key=('opening',index)
            frame=self.opening[index]
        elif fraction<1:
            key=(round(44+(self.full_width-44)*fraction),round(44+(height-44)*fraction))
            frame=self.frame(*key)
        else:
            key=('full',height);frame=self.frame(self.full_width,height)
        if key==self.current_key:return
        before=time.perf_counter();self.paint_frame(frame)
        self.render_ms.append((time.perf_counter()-before)*1000)
        if len(self.render_ms)>120:self.render_ms.pop(0)
        self.current_key=key
