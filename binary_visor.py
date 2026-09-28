"""Small cached glyphs projected onto a curved visor. No inference, no busy blink."""
import math,random,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops

class BinaryVisor:
    PERIOD=2.7
    SWEEP=1.85
    def __init__(self):
        self.cycle=-1;self.bits='';self.glyphs={}
        font=Path(os.environ.get('SystemRoot','C:/Windows'))/'Fonts'/'consola.ttf'
        self.font=ImageFont.truetype(str(font),48)
        self.mask=Image.new('L',(128,148))
        ImageDraw.Draw(self.mask).rounded_rectangle((38,30,91,57),radius=11,fill=255)

    def render(self,elapsed,offset=0):
        cycle=int(elapsed/self.PERIOD);position=elapsed%self.PERIOD
        if cycle!=self.cycle:
            self.cycle=cycle;self.bits=''.join(random.choice('01') for _ in range(10))
        frame=Image.new('RGBA',(128,148));draw=ImageDraw.Draw(frame)
        # Cover the two original eyes only; keep the visor's outline and highlights.
        for x in (51,77):draw.ellipse((x-7,31,x+7,55),fill='#151B23')
        if position<self.SWEEP:
            strip=Image.new('RGBA',frame.size)
            for index,bit in enumerate(self.bits):
                linear=-1.7+position/self.SWEEP*5.7-index*.30
                if abs(linear)>1:continue
                angle=linear*1.35
                x=64+27*math.sin(angle)
                scale=max(.16,math.cos(angle))
                width=max(2,round(9*scale));height=18
                key=(bit,width)
                if key not in self.glyphs:
                    glyph=Image.new('RGBA',(30,60))
                    ImageDraw.Draw(glyph).text((15,30),bit,font=self.font,anchor='mm',fill='#69DDFF')
                    self.glyphs[key]=glyph.resize((width,height),Image.Resampling.LANCZOS)
                strip.alpha_composite(self.glyphs[key],(round(x-width/2),34))
            strip.putalpha(ImageChops.multiply(strip.getchannel('A'),self.mask))
            glow=strip.filter(ImageFilter.GaussianBlur(1.2));glow.putalpha(glow.getchannel('A').point(lambda a:a//2))
            frame.alpha_composite(glow);frame.alpha_composite(strip)
        if offset:frame=frame.transform(frame.size,Image.Transform.AFFINE,(1,0,0,0,1,-offset),Image.Resampling.BICUBIC)
        return frame
