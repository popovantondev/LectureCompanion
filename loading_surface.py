"""Transparent, gently hovering startup mascot with real stage progress."""
import math,os,time,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from layered_sprite import LayeredSprite
from i18n import tr

class LoadingSurface(LayeredSprite):
    def __init__(self,root,source):
        self.portrait=source.convert('RGBA').copy();self.portrait.thumbnail((185,215),Image.Resampling.LANCZOS)
        self.started=time.monotonic();self.step=0;self.label=tr('Подготовка интерфейса…')
        font=Path(os.environ.get('SystemRoot','C:/Windows'))/'Fonts'/'segoeui.ttf'
        self.font=ImageFont.truetype(str(font),12);self.small=ImageFont.truetype(str(font),10)
        self.motion_frames={};self.caption_key=None;self.caption_frame=None
        # Quarter-pixel positions preserve smooth motion without repainting fonts
        # or calculating blur on every animation tick.
        self.motion_source=Image.new('RGBA',(280,242))
        self.motion_source.alpha_composite(self.portrait,((280-self.portrait.width)//2,8))
        for quarter in range(-24,25):self.motion_frame(quarter)
        super().__init__(root,source,size=(280,330))

    def motion_frame(self,quarter):
        if quarter not in self.motion_frames:
            bob=quarter/4
            frame=Image.new('RGBA',(280,242));shadow=Image.new('RGBA',frame.size)
            ImageDraw.Draw(shadow).ellipse((99-bob,224,181+bob,232),fill=(35,60,85,round(43+bob*2)))
            frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)))
            shifted=self.motion_source.transform(self.motion_source.size,Image.Transform.AFFINE,(1,0,0,0,1,-bob),Image.Resampling.BICUBIC)
            frame.alpha_composite(shifted);self.motion_frames[quarter]=frame
        return self.motion_frames[quarter]

    def paint(self,*args):
        elapsed=time.monotonic()-self.started
        key=(self.step,self.label,int(elapsed))
        if key!=self.caption_key:
            self.caption_frame=self.make_caption(elapsed);self.caption_key=key
        frame=self.caption_frame.copy()
        frame.alpha_composite(self.motion_frame(round(math.sin(elapsed*1.8)*24)))
        self.paint_frame(frame)

    def make_caption(self,elapsed):
        frame=Image.new('RGBA',(280,330))
        draw=ImageDraw.Draw(frame);draw.rounded_rectangle((42,250,238,256),radius=3,fill=(218,230,242,240))
        if self.step:draw.rounded_rectangle((42,250,42+196*self.step/4,256),radius=3,fill='#075DD1')
        lines=textwrap.wrap(self.label,width=37)[:2]
        for i,line in enumerate(lines):
            half=draw.textlength(line,font=self.font)/2+9;y=276+i*18
            draw.rounded_rectangle((140-half,y-9,140+half,y+9),radius=8,fill=(255,255,255,238))
            draw.text((140,y-1),line,font=self.font,anchor='mm',fill='#14253D')
        draw.rounded_rectangle((94,306,186,324),radius=8,fill=(255,255,255,220))
        draw.text((140,314),tr('Этап')+f' {min(4,self.step+1)} / 4 · {int(elapsed)} s',font=self.small,anchor='mm',fill='#526C80')
        return frame
