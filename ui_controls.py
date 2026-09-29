"""Small, antialiased controls in the Lecture Companion navy and blue palette."""
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

BG = '#FFFFFF'
INK = '#14253D'


class CardOutline(tk.Canvas):
    """A consistent 1 px light outline, independent of Windows frame colours."""
    def __init__(self,parent,fill=BG,radius=18):
        super().__init__(parent,bg=fill,highlightthickness=0,bd=0)
        self.fill=fill;self.radius=radius;self.last_size=None;self.frames={}
        self.item=self.create_image(0,0,anchor='nw')
        self.place(x=0,y=0,relwidth=1,relheight=1)
        self.tk.call('lower',self._w)

    def resize(self,width,height):
        key=(round(width),round(height))
        if key==self.last_size:return
        if key in self.frames:
            self.last_size=key;self.picture=self.frames[key];self.itemconfigure(self.item,image=self.picture);return
        self.last_size=key;scale=3
        face=Image.new('RGB',(key[0]*scale,key[1]*scale),self.fill)
        draw=ImageDraw.Draw(face)
        draw.rounded_rectangle((scale/2,scale/2,key[0]*scale-scale/2-1,key[1]*scale-scale/2-1),radius=self.radius*scale,outline='#DBE4F0',width=scale)
        self.picture=ImageTk.PhotoImage(face.resize(key,Image.Resampling.LANCZOS),master=self)
        if len(self.frames)>=12:self.frames.pop(next(iter(self.frames)))
        self.frames[key]=self.picture
        self.itemconfigure(self.item,image=self.picture)


def icon(kind, size=36, hovered=False, selected=False, level=1):
    scale = 3
    im = Image.new('RGBA', (size*scale, size*scale), BG)
    d = ImageDraw.Draw(im)
    def box(b): return tuple(round(v*size*scale/36) for v in b)
    def line(points, fill=INK, width=1.5):
        d.line(box(points), fill=fill, width=round(width*size*scale/36), joint='curve')
    def ellipse(b, fill=None, outline=None, width=1):
        d.ellipse(box(b), fill=fill, outline=outline, width=max(1,round(width*size*scale/36)))
    circle = '#E6F0FF' if selected or hovered else '#F3F6FB'
    if kind == 'close': circle = '#F5E1E4' if hovered else '#EEF2F6'
    ellipse((1,1,35,35),circle)
    if kind == 'close':
        line((13,13,23,23), '#9C6671' if hovered else '#7D8A98')
        line((23,13,13,23), '#9C6671' if hovered else '#7D8A98')
    elif kind == 'image':
        d.rounded_rectangle(box((9,10,27,26)),radius=2*scale,outline=INK,width=scale)
        ellipse((20,13,23,16), '#075DD1')
        line((10,23,15,17,20,23,23,20,26,24))
    elif kind == 'rocket':
        d.polygon(box((15,20,9,23,10,16,16,13)),fill='#075DD1')
        d.polygon(box((17,22,14,28,22,26,24,19)),fill='#075DD1')
        d.polygon(box((13,20,16,12,24,7,29,7,29,12,24,20,17,23)),fill='#FFFFFF',outline=INK,width=scale)
        ellipse((21,11,25,15),'#075DD1')
        line((12,24,8,28),'#67CFF4',2)
        line((15,26,13,29),'#A5E8FF',1.5)
    elif kind == 'settings':
        for y, cx in ((11,14),(18,23),(25,17)):
            line((9,y,27,y),width=1)
            ellipse((cx-2.5,y-2.5,cx+2.5,y+2.5),BG,INK)
    elif kind == 'note':
        # Progressively larger notes, from crossed-out to loud.
        factor = .45+.55*level
        def n(points): return tuple(18+(v-18)*factor for v in points)
        line(n((17,23,17,10,25,8,25,20)),width=1.7)
        line(n((17,13,25,11)),width=1.4)
        ellipse(n((11,21,17,25)),INK)
        ellipse(n((19,18,25,22)),INK)
        if level == 0:
            line((9,8,28,28),BG,4)
            line((9,8,28,28),'#91A0AF',1.5)
    return im.resize((size,size),Image.Resampling.LANCZOS)


class IconButton(tk.Canvas):
    def __init__(self, parent, kind, command, size=36, label='', level=1):
        super().__init__(parent,width=size,height=size,bg=BG,highlightthickness=0,
                         takefocus=True,cursor='hand2')
        self.kind=kind; self.command=command; self.label=label; self.level=level
        self.selected=False; self.hovered=False; self.size=size; self.cache={}
        self.item=self.create_image(size//2,size//2)
        self.bind('<Enter>',lambda e:self.hover(True))
        self.bind('<Leave>',lambda e:self.hover(False))
        self.bind('<FocusIn>',lambda e:self.hover(True))
        self.bind('<FocusOut>',lambda e:self.hover(False))
        self.bind('<ButtonRelease-1>',lambda e:self.invoke())
        self.bind('<Return>',lambda e:(self.invoke(),'break')[1])
        self.bind('<space>',lambda e:(self.invoke(),'break')[1])
        self.paint()

    def invoke(self): self.command()
    def hover(self, value): self.hovered=value; self.paint()
    def paint(self):
        key=(self.hovered,self.selected,self.level)
        if key not in self.cache:
            self.cache[key]=ImageTk.PhotoImage(icon(self.kind,self.size,*key[:2],level=self.level),master=self)
        self.itemconfigure(self.item,image=self.cache[key])
