"""Lightweight native card-stack skin. Animations run only on interaction."""
import tkinter as tk
import threading
import time
import queue
import winsound
import ctypes
import math
import random
from pathlib import Path
from robot_sound import play,settings,save_settings
import i18n,os
from i18n import tr
from ui_controls import IconButton,CardOutline
from window_group import WindowGroup,deck_layout
from pill_surface import PillSurface

class QuestionBox(tk.Text):
    def get(self,*args):return super().get(*(args or ('1.0','end-1c')))
    def delete(self,first,last=None):return super().delete('1.0' if first==0 else first,last)

BG='#FAFBFD'; INK='#192534'; MUTED='#778493'; GOLD='#D9EEFB'; LINE='#DCE3EB'

def run(Base, api):
 class StyledPet(Base):
    def __init__(self):
        self.skin_ready=False; self.entries=[]; self.offset=0; self.last_status=''; self.animation=None
        self.hover_offset=0;self.hover_target=0;self.hover_job=None;self.processing=False;self.eye_job=None;self.eye_phase=0
        self.composer_animation=None;self.composer_full_height=56;self.composer_fraction=0;self.composer_width=620
        self.layout_job=None;self.drag_job=None;self.dragging=False;self.deck_shift=0
        self.popup=None;self.popup_hide_job=None;self.resize_job=None
        self.language=os.environ.get('LECTURE_UI_LANGUAGE',settings()['language']);i18n.set_language(self.language)
        self.sound_times={};self.language_pending=False;self.static_bindings=[];self.thinking_started=0;self.last_telemetry={}
        super().__init__()
        preferences=settings();self.volume=tk.DoubleVar(value=preferences['volume']);self.sound.set(preferences['sound'])
        self.canvas.delete('all')
        sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        self.root.geometry(f'128x148+{min(self.initial_xy[0],sw-128)}+{min(self.initial_xy[1],sh-188)}');self.canvas.configure(width=128,height=148)
        self.draw_robot()
        self.window_group=WindowGroup();self.pet_xy=self.initial_xy
        self.back_windows=[self.previous,tk.Toplevel(self.root),tk.Toplevel(self.root)]
        for win in self.back_windows[1:]:
            win.overrideredirect(True);win.attributes('-topmost',True);win.withdraw()
        for win in (self.bubble,*self.back_windows,self.composer):
            for child in win.winfo_children():child.destroy()
            win.configure(bg=LINE)
            win.update_idletasks()
            self.window_group.remove_chrome(win)
        self.composer.configure(padx=0,pady=0)
        self.bubble.configure(bg=BG)
        self.card_outlines=[CardOutline(self.bubble)]
        panel=tk.Frame(self.bubble,bg=BG);panel.pack(padx=22,pady=16,fill='both',expand=True)
        head=tk.Frame(panel,bg=BG);head.pack(fill='x')
        title=tk.Label(head,text='LECTURE  /  Компаньон',bg=BG,fg=INK,font=('Segoe UI',10,'bold'));title.pack(side='left')
        self.close_button=IconButton(head,'close',self.hide_answers,size=28,label='Скрыть ответы');self.close_button.pack(side='right')
        self.sound_button=IconButton(head,'note',self.show_sound_settings,size=28,label='Громкость');self.sound_button.pack(side='right',padx=(0,6))
        self.sound_button.level=self.volume.get()/100 if self.sound.get() else 0;self.sound_button.paint()
        self.settings_button=IconButton(head,'settings',self.show_mode_settings,size=28,label='Скорость ответа');self.settings_button.pack(side='right',padx=(0,6))
        for widget in (head,title):self.make_window_draggable(self.bubble,widget)
        tk.Frame(panel,bg='#6ABDE8',height=2,width=32).pack(anchor='w',pady=(10,14))
        self.meta=tk.Label(panel,text='Готов слушать',bg=BG,fg=MUTED,font=('Segoe UI',9),anchor='w');self.meta.pack(fill='x')
        self.prompt_label=tk.Label(panel,text='',bg=BG,fg=INK,font=('Segoe UI',10,'bold'),wraplength=390,justify='left');self.prompt_label.pack(fill='x',pady=(8,0))
        self.answer=tk.Label(panel,text='Новые итоги появятся здесь.',bg=BG,fg=INK,font=('Segoe UI',11),wraplength=390,justify='left',anchor='w');self.answer.pack(fill='x',pady=(8,16))
        nav=tk.Frame(panel,bg=BG);nav.pack(fill='x')
        self.button(nav,'←',lambda:self.navigate(1),quiet=True).pack(side='left')
        self.counter=tk.Label(nav,text='История',bg=BG,fg=MUTED,font=('Segoe UI',9));self.counter.pack(side='left',padx=10)
        self.button(nav,'→',lambda:self.navigate(-1),quiet=True).pack(side='left')
        self.button(nav,'К свежему',lambda:self.navigate(-999),quiet=True).pack(side='right')
        tk.Frame(panel,bg=LINE,height=1).pack(fill='x',pady=(12,10))
        self.stage=tk.Label(panel,text='Подключение…',bg=BG,fg='#507D79',font=('Segoe UI',9,'bold'),anchor='w',wraplength=390,justify='left');self.stage.pack(fill='x')
        self.details=tk.Label(panel,text='',bg=BG,fg=MUTED,font=('Segoe UI',8),anchor='w',wraplength=390,justify='left');self.details.pack(fill='x',pady=(4,0))
        self.text=tk.Label(panel,text='',bg=BG,fg=MUTED,font=('Segoe UI',9),wraplength=390,justify='left');self.text.pack(fill='x',pady=(4,0))
        self.back_labels=[]
        for depth,win in enumerate(self.back_windows,1):
            win.attributes('-alpha',(.88,.72,.57)[depth-1])
            face=('#DDE2E8','#D2D8E0','#C6CED8')[depth-1];win.configure(bg=face)
            self.card_outlines.append(CardOutline(win,fill=face))
            self.card_outlines[-1].bind('<Button-1>',lambda e,d=depth:self.navigate(d))
            self.card_outlines[-1].bind('<MouseWheel>',lambda e:self.navigate(1 if e.delta>0 else -1))
            label=tk.Label(win,text='Предыдущий итог',bg=face,fg='#536276',font=('Segoe UI',9),anchor='w',bd=0)
            label.place(x=16,y=3,height=20,relwidth=1,width=-32);self.back_labels.append(label)
            label.bind('<Button-1>',lambda e,d=depth:self.navigate(d))
        self.preview=self.back_labels[0]
        # Only the inset controls belong to Tk. The rounded face and shadow are
        # a per-pixel surface underneath, without a competing Windows border.
        self.composer.configure(bg='#010203')
        self.composer.wm_attributes('-transparentcolor','#010203')
        self.pill=PillSurface(self.root,self.composer_width)
        self.window_group.remove_chrome(self.pill.window)
        self.pill.window.bind('<Enter>',self.reveal_question)
        self.pill.window.bind('<Leave>',self.defer_hide_question)
        self.pill.window.bind('<Button-1>',lambda e:self.question.focus_set())
        composer=tk.Frame(self.composer,bg=BG);self.composer_panel=composer
        composer.place(x=16,y=9,width=self.composer_width-32,height=38)
        row=tk.Frame(composer,bg=BG);row.pack(fill='both',expand=True)
        controls=tk.Frame(row,bg=BG);controls.pack(side='right',anchor='n',padx=(8,0))
        self.slide_label=tk.Label(controls,text='Анализ скриншота',bg=BG,fg='#6B7F91',font=('Segoe UI',9),cursor='hand2',padx=4)
        self.slide_label.pack(side='left',padx=(0,3),pady=8)
        self.slide_label.bind('<Button-1>',lambda e:self.analyze_presentation())
        self.slide_button=IconButton(controls,'image',lambda:self.analyze_presentation(),label='Разобрать свежий слайд')
        self.slide_button.pack(side='left',padx=(0,6))
        self.send_button=IconButton(controls,'rocket',lambda:self.ask(),label='Отправить · Ctrl+Enter')
        self.send_button.selected=True;self.send_button.paint();self.send_button.pack(side='left')
        self.question=QuestionBox(row,width=30,height=1,font=('Segoe UI',11),bg=BG,fg=INK,relief='flat',bd=0,highlightthickness=0,insertbackground=INK,wrap='word',padx=0,pady=7,undo=True)
        self.question.pack(side='left',fill='both',expand=True)
        self.placeholder=tk.Label(composer,text='Спроси о лекции…',bg=BG,fg='#97A4B2',font=('Segoe UI',10),cursor='xterm',bd=0)
        self.placeholder.place(x=0,rely=.5,anchor='w');self.placeholder.bind('<Button-1>',lambda e:self.question.focus_set())
        self.question.bind('<<Modified>>',self.question_changed)
        self.question.bind('<Configure>',self.question_changed)
        self.question.bind('<FocusIn>',self.question_changed)
        self.question.bind('<FocusOut>',self.question_changed)
        self.question.bind('<Control-Return>',lambda e:(self.ask(),'break')[1])
        self.mode=tk.StringVar(value='balanced');self.mode_buttons={}
        self.composer.bind('<Enter>',self.reveal_question,add='+');self.composer.bind('<Leave>',self.defer_hide_question,add='+')
        for widget in (self.bubble,panel,self.answer,*self.back_labels):widget.bind('<MouseWheel>',lambda e:self.navigate(1 if e.delta>0 else -1))
        self.root.bind('<Left>',lambda e:self.navigate(1));self.root.bind('<Right>',lambda e:self.navigate(-1))
        self.root.bind('<Escape>',lambda e:self.hide_answers())
        self.canvas.bind('<Enter>',self.hover_enter);self.canvas.bind('<Leave>',self.hover_leave)
        self.skin_ready=True
        self.translate_static(self.root)
        self.composer.withdraw();self.root.update_idletasks();self.place_bubble()
        self.root.deiconify();self.window_group.show(self.bubble);self.root.update_idletasks();self.restack()
        self.root.bind('<Configure>',self.root_configured,add='+')
        self.root.bind_all('<ButtonPress-1>',self.outside_popup,add='+')
        self.root.after(random.randint(5000,9000),self.idle_blink)

    def sound_effect(self,kind,interval=.7):
        now=time.monotonic()
        if self.sound.get() and now-self.sound_times.get(kind,-100)>interval:
            self.sound_times[kind]=now;play(kind,self.volume.get()/100)

    def translate_static(self,parent):
        for widget in parent.winfo_children():
            try:
                value=widget.cget('text')
                if value in i18n.CATALOG:
                    self.static_bindings.append((widget,value));widget.configure(text=tr(value))
            except tk.TclError:pass
            self.translate_static(widget)

    def set_language(self,language):
        if self.language_pending or language==self.language:return
        self.language_pending=True
        def work():
            try:api('/api/language',True,{'language':language});self.events.put(('language',language))
            except Exception as exc:self.events.put(('language_error',str(exc)[:100]))
        threading.Thread(target=work,daemon=True).start()

    def apply_language(self,language):
        previous=self.language;self.language=language;i18n.set_language(language)
        save_settings(self.sound.get(),self.volume.get(),language)
        self.close_popup()
        for widget,key in self.static_bindings:
            if widget.winfo_exists() and widget.cget('text')==tr(key,previous):widget.configure(text=tr(key))
        self.render_card();self.telemetry(self.last_telemetry);self.show(tr('Язык изменён. Новые ответы будут на этом языке.'))

    def button(self,parent,text,command,quiet=False):
        button=tk.Button(parent,text=tr(text),command=command,bg=BG if quiet else GOLD,fg=INK,activebackground='#C6E4F6',activeforeground=INK,relief='flat',bd=0,padx=10,pady=6,font=('Segoe UI',9,'bold'),cursor='hand2',takefocus=True)
        if text in i18n.CATALOG:self.static_bindings.append((button,text))
        return button

    def set_mode(self,mode):
        def work():
            try:api('/api/response-mode',True,{'mode':mode});self.events.put(('notice',tr('Режим: ')+tr({'fast':'быстро','balanced':'обычно','deep':'вдумчиво'}[mode])))
            except Exception as exc:self.events.put(('notice','Не удалось изменить режим: '+str(exc)[:90]))
        threading.Thread(target=work,daemon=True).start()

    def draw_robot(self):
        c=self.canvas
        sprite=Path(__file__).with_name('assets')/'companion.png'
        if sprite.exists():
            from PIL import Image,ImageTk
            from layered_sprite import LayeredSprite
            with Image.open(sprite) as source:
                source=source.convert('RGBA');source.thumbnail((124,140),Image.Resampling.LANCZOS)
                self.robot_image=ImageTk.PhotoImage(source)
                c.pack_forget();self.renderer=LayeredSprite(self.root,source)
            for event,handler in [('<ButtonPress-1>',self.press),('<B1-Motion>',self.drag),('<ButtonRelease-1>',self.release),('<Button-3>',self.menu),('<Enter>',self.hover_enter),('<Leave>',self.hover_leave)]:self.root.bind(event,handler)
            self.shadow=c.create_oval(34,138,94,145,fill='#B6C0CD',outline='')
            c.create_oval(42,140,86,144,fill='#9BA9BA',outline='',tags='shadow_inner')
            c.create_image(64,69,image=self.robot_image,tags='robot')
            self.lamp=c.create_oval(57,140,71,145,fill='#76C6EF',outline='')
            return
        c.create_oval(19,86,78,94,fill='#ABB5B8',outline='')
        c.create_oval(25,55,73,92,fill='#CED8D8',outline='#8C9BA2')
        c.create_oval(27,52,70,87,fill='#FAF9EF',outline='')
        c.create_oval(15,55,31,85,fill='#E6E9E3',outline='#A0AFB3')
        c.create_oval(68,55,82,85,fill='#D8E1DC',outline='#A0AFB3')
        c.create_oval(8,8,88,65,fill='#A2B5BA',outline='#68808C')
        c.create_oval(10,6,86,61,fill='#FFFDF3',outline='')
        c.create_oval(15,16,82,55,fill='#102E38',outline='#395761',width=2)
        c.create_oval(21,18,74,32,fill='#203F48',outline='')
        for x in (33,63):
            c.create_oval(x-11,24,x+10,48,fill='#081D26',outline='#80E8DF',width=2)
            c.create_oval(x-8,27,x+7,45,fill='#102831',outline='#389C9D')
            c.create_oval(x-6,28,x-1,34,fill='#FFFDF3',outline='')
        c.create_line(43,51,51,51,fill='#ADF4E6',width=2)
        c.create_oval(22,11,48,16,fill='#FFFFFF',outline='')
        self.lamp=c.create_oval(43,67,53,77,fill='#80D5C1',outline='#476D6C',width=2)
        c.create_line(35,86,63,86,fill='#B0BCB8',width=2)

    def show(self,message):
        if not self.skin_ready:return
        message=tr(message)
        self.text.configure(text=message)
        changed=self.bubble.state()=='withdrawn'
        if changed:self.window_group.show(self.bubble)
        self.queue_layout()
        if changed:self.root.after_idle(self.restack)

    def hide_answers(self):
        self.cancel_composer_animation()
        self.composer_fraction=0
        self.bubble.withdraw();self.composer.withdraw()
        if hasattr(self,'pill'):self.pill.window.withdraw()
        for win in getattr(self,'back_windows',[self.previous]):win.withdraw()
        self.close_popup()

    def make_window_draggable(self,window,handle):
        # A card header drags the entire group, never detaches a single card.
        handle.bind('<ButtonPress-1>',self.press)
        handle.bind('<B1-Motion>',self.drag)
        handle.bind('<ButtonRelease-1>',lambda e:self.release(e,header=True))
        handle.configure(cursor='fleur')

    def press(self,event):
        if not self.skin_ready:return super().press(event)
        self.anchor=(event.x_root,event.y_root,*self.pet_xy);self.moved=False
        self.dragging=True;self.close_popup()
        if self.animation:self.root.after_cancel(self.animation);self.animation=None
        self.deck_shift=0

    def drag(self,event):
        if not self.skin_ready:return super().drag(event)
        ax,ay,x,y=self.anchor;dx,dy=event.x_root-ax,event.y_root-ay
        if abs(dx)+abs(dy)>4:self.moved=True
        if self.moved:
            self.sound_effect('drag',.65)
            self.drag_target=(x+dx,y+dy)
            if self.drag_job is None:self.drag_job=self.root.after(16,self.flush_drag)

    def flush_drag(self):
        self.drag_job=None
        if hasattr(self,'drag_target'):
            self.pet_xy=self.drag_target
            del self.drag_target
            self.place_bubble()

    def release(self,event,header=False):
        if not self.skin_ready:return super().release(event)
        if self.drag_job:self.root.after_cancel(self.drag_job);self.drag_job=None
        self.flush_drag();self.dragging=False
        if self.moved:
            self.root.update_idletasks()
            super().release(event)
        elif not header:self.request()

    def root_configured(self,event):
        if event.widget!=self.root or not self.skin_ready or self.dragging:return
        expected=self.window_group.positions.get(self.root)
        if expected and (event.x,event.y)!=expected[:2]:
            # Ignore queued stale configure events; only use the actual native position.
            from ctypes import wintypes
            rect=wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(self.window_group.handle(self.root),ctypes.byref(rect))
            if (rect.left,rect.top)!=expected[:2]:
                self.pet_xy=(rect.left,rect.top);self.queue_layout()

    def close_popup(self):
        if self.popup_hide_job:self.root.after_cancel(self.popup_hide_job);self.popup_hide_job=None
        if self.popup is not None:
            self.window_group.regions.pop(self.popup,None)
            self.window_group.positions.pop(self.popup,None)
            self.window_group.chrome_removed.discard(self.popup)
            self.popup.destroy();self.popup=None
        self.mode_buttons={}
        self.static_bindings=[(w,k) for w,k in self.static_bindings if w.winfo_exists()]

    def outside_popup(self,event):
        if not self.popup:return
        if event.widget.winfo_toplevel()==self.popup:return
        if event.widget in (self.sound_button,self.settings_button):return
        self.close_popup()

    def popup_window(self,anchor,width,height,position=None):
        self.close_popup()
        window=tk.Toplevel(self.root);window.withdraw();window.overrideredirect(True);window.attributes('-topmost',True)
        window.configure(bg=BG);self.popup=window
        sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        x=max(8,min(anchor.winfo_rootx()+anchor.winfo_width()//2-width//2,sw-width-8))
        y=anchor.winfo_rooty()+anchor.winfo_height()+8
        if y+height>sh-12:y=anchor.winfo_rooty()-height-8
        if position:x=max(8,min(position[0],sw-width-8));y=max(8,min(position[1],sh-height-48))
        window.geometry(f'{width}x{height}+{x}+{max(8,y)}');window.update_idletasks()
        self.window_group.rounded(window,width,height,20)
        window.bind('<Escape>',lambda e:self.close_popup())
        def leave(event=None):
            if self.popup_hide_job:self.root.after_cancel(self.popup_hide_job)
            def check():
                self.popup_hide_job=None
                if not self.popup:return
                px,py=self.root.winfo_pointerxy()
                for w in (self.popup,anchor):
                    if w.winfo_rootx()<=px<w.winfo_rootx()+w.winfo_width() and w.winfo_rooty()<=py<w.winfo_rooty()+w.winfo_height():return
                self.close_popup()
            self.popup_hide_job=self.root.after(850,check)
        window.bind('<Leave>',leave)
        border=CardOutline(window);border.resize(width,height)
        def ready():
            if self.popup!=window:return
            self.translate_static(window);window.update_idletasks();window.deiconify();self.raise_popup()
        self.root.after_idle(ready)
        return window

    def raise_popup(self):
        if self.popup and self.popup.winfo_exists():self.window_group.stack([self.popup])

    def show_sound_settings(self):
        window=self.popup_window(self.sound_button,292,142)
        header=tk.Frame(window,bg=BG);header.pack(fill='x',padx=18,pady=(13,4))
        tk.Label(header,text='Звук помощника',bg=BG,fg=INK,font=('Segoe UI',10,'bold')).pack(side='left')
        value=tk.Label(header,bg=BG,fg=MUTED,font=('Segoe UI',9));value.pack(side='right')
        row=tk.Frame(window,bg=BG);row.pack(pady=2)
        buttons=[]
        track=tk.Canvas(window,width=252,height=24,bg=BG,highlightthickness=0,cursor='hand2')
        def refresh():
            volume=round(self.volume.get()) if self.sound.get() else 0
            value.configure(text=str(volume)+'%' if volume else tr('Без звука'))
            nearest=0 if volume==0 else min(range(1,4),key=lambda i:abs(volume-(100*i/3)))
            for i,button in enumerate(buttons):button.selected=i==nearest;button.paint()
            track.delete('all')
            track.create_line(8,12,244,12,fill='#E4EAF1',width=5,capstyle='round')
            end=8+236*volume/100
            if volume:track.create_line(8,12,end,12,fill='#79C7EB',width=5,capstyle='round')
            track.create_oval(end-5,7,end+5,17,fill='#FAFEFF',outline='#81BEDC',width=2)
            self.sound_button.level=volume/100;self.sound_button.cache.clear();self.sound_button.paint()
        def choose(volume,persist=True):
            self.volume.set(max(0,min(100,round(volume))));self.sound.set(self.volume.get()>0)
            if persist:save_settings(self.sound.get(),self.volume.get())
            refresh()
        def preview(volume):
            choose(volume)
            play('answer',self.volume.get()/100,preview=True)
        for i in range(4):
            button=IconButton(row,'note',lambda n=i:preview(round(n*100/3)),size=42,level=i/3,label=('Без звука' if i==0 else str(round(i*100/3))+'%'))
            button.pack(side='left',padx=9);buttons.append(button)
        track.pack(pady=(4,0))
        track.bind('<Button-1>',lambda e:choose((e.x-8)/236*100,False))
        track.bind('<B1-Motion>',lambda e:choose((e.x-8)/236*100,False))
        def released(event):
            preview(self.volume.get())
        track.bind('<ButtonRelease-1>',released)
        refresh();self.volume_choose=choose;self.volume_buttons=buttons;self.volume_track=track

    def show_mode_settings(self):
        window=self.popup_window(self.settings_button,314,136)
        tk.Label(window,text='Скорость ответа',bg=BG,fg=INK,font=('Segoe UI',10,'bold')).pack(anchor='w',padx=18,pady=(13,10))
        row=tk.Frame(window,bg=BG);row.pack()
        for mode,label in [('fast','Быстро'),('balanced','Обычно'),('deep','Вдумчиво')]:
            button=self.button(row,label,lambda m=mode:self.set_mode(m),quiet=True);button.pack(side='left',padx=2)
            button.configure(bg=GOLD if mode==self.mode.get() else BG);self.mode_buttons[mode]=button
        tk.Label(window,text='Вдумчивый режим — только для твоих вопросов.\nВсе три режима работают локально.',bg=BG,fg=MUTED,font=('Segoe UI',8),justify='left').pack(padx=18,pady=8,anchor='w')

    def question_changed(self,event=None):
        if not self.skin_ready:return
        if self.question.edit_modified():self.question.edit_modified(False)
        if self.resize_job is None:self.resize_job=self.root.after_idle(self.resize_question)

    def resize_question(self):
        self.resize_job=None
        if not self.question.winfo_exists():return
        empty=not self.question.get()
        if empty and self.root.focus_get()!=self.question:self.placeholder.place(x=0,rely=.5,anchor='w')
        else:self.placeholder.place_forget()
        try:lines=int(self.question.count('1.0','end-1c','displaylines')[0])+1
        except (TypeError,tk.TclError):lines=1
        lines=max(1,min(8,lines))
        height=56+(lines-1)*20
        if height!=self.composer_full_height:
            self.question.configure(height=lines);self.composer_full_height=height
            self.place_bubble()
        self.question.see('insert')

    def cancel_composer_animation(self):
        if self.composer_animation:self.root.after_cancel(self.composer_animation);self.composer_animation=None

    def reveal_question(self,event=None):
        if not getattr(self,'skin_ready',False):return super().reveal_question(event)
        if self.hide_question_job:self.root.after_cancel(self.hide_question_job);self.hide_question_job=None
        if self.popup or self.dragging or self.composer_animation is not None or self.composer.state()!='withdrawn':return
        self.composer_fraction=0;self.composer_panel.place_forget()
        self.place_bubble();self.pill.show_shape(self.composer_full_height,0);self.window_group.show(self.pill.window)
        self.window_group.stack([self.pill.window]);self.sound_effect('reveal',1)
        started=time.monotonic()
        def animate():
            t=min(1,(time.monotonic()-started)/.24)
            self.composer_fraction=1-(1-t)**3
            # The native window stays still: only cached pixels change.
            self.pill.show_shape(self.composer_full_height,self.composer_fraction)
            if t<1:self.composer_animation=self.root.after(16,animate)
            else:
                self.composer_animation=None
                self.composer_fraction=1;self.place_bubble()
                self.composer_panel.place(x=16,y=9,width=self.composer_width-32,height=self.composer_full_height-18)
                self.composer.update_idletasks();self.window_group.show(self.composer)
                self.window_group.stack([self.composer]);self.raise_popup()
                self.composer_panel.place(x=16,y=9,width=self.composer_width-32,height=self.composer_full_height-18)
                self.question_changed()
        animate()

    def hide_question(self):
        self.hide_question_job=None
        if self.dragging or self.popup:return
        px,py=self.root.winfo_pointerxy()
        for widget in (self.root,self.composer):
            if widget.winfo_viewable() and widget.winfo_rootx()-8<=px<=widget.winfo_rootx()+widget.winfo_width()+8 and widget.winfo_rooty()-12<=py<=widget.winfo_rooty()+widget.winfo_height()+12:return
        if self.root.focus_get()==self.question:
            self.defer_hide_question();return
        self.cancel_composer_animation();self.composer.withdraw();self.pill.window.withdraw();self.composer_fraction=0

    def hover_enter(self,event=None):
        self.reveal_question(event);self.hover_target=-5;self.animate_hover()

    def hover_leave(self,event=None):
        self.defer_hide_question(event);self.hover_target=0;self.animate_hover()

    def animate_hover(self):
        if self.hover_job:self.root.after_cancel(self.hover_job)
        self.hover_job=None
        if self.hover_offset==self.hover_target:return
        origin=self.hover_offset;target=self.hover_target;started=time.monotonic()
        def step():
            before=time.monotonic();t=min(1,(before-started)/.16)
            value=round((origin+(target-origin)*(1-(1-t)**3))*4)/4
            if value!=self.hover_offset:
                self.hover_offset=value;self.canvas.coords('robot',64,69+value);self.draw_eyes()
            if t<1:self.hover_job=self.root.after(max(1,16-round((time.monotonic()-before)*1000)),step)
            else:self.hover_job=None
        step()

    def draw_eyes(self,closed=False):
        if hasattr(self,'renderer'):
            self.renderer.paint(self.hover_offset,self.processing,self.eye_phase,closed and not self.processing);return
        self.canvas.delete('eyes')
        if not hasattr(self,'robot_image') or not (closed or self.processing):return
        # Tiny vector eyelids/indicators are an animation layer over the unchanged sprite.
        y=43+self.hover_offset
        for index,x in enumerate((51,77)):
            self.canvas.create_oval(x-7,y-12,x+7,y+12,fill='#151B23',outline='',tags='eyes')
            if closed:self.canvas.create_line(x-4,y,x+4,y,fill='#8EE7FF',width=2,tags='eyes')
            else:
                pulse=2+2*(1+math.sin(self.eye_phase+index*.7))
                self.canvas.create_oval(x-3,y-pulse,x+3,y+pulse,fill='#73DAFF',outline='',tags='eyes')

    def idle_blink(self):
        if not self.processing:
            self.draw_eyes(True);self.root.after(130,self.draw_eyes)
        self.root.after(random.randint(5500,10500),self.idle_blink)

    def blink(self,count):
        if not getattr(self,'skin_ready',False):return super().blink(count)
        self.draw_eyes(count>0 and count%2==0)
        if count>0:self.root.after(170,lambda:self.blink(count-1))

    def animate_thinking(self):
        self.eye_job=None
        if not self.processing:self.draw_eyes();return
        self.eye_phase=time.monotonic()-self.thinking_started;self.draw_eyes()
        self.eye_job=self.root.after(33,self.animate_thinking)

    def menu(self,event):
        self.cancel_composer_animation()
        if self.composer.state()=='withdrawn':self.pill.window.withdraw();self.composer_fraction=0
        window=self.popup_window(self.root,354,514,position=(event.x_root,event.y_root))
        self.menu_rows=[]
        header=tk.Frame(window,bg=BG);header.pack(fill='x',padx=18,pady=(14,8))
        tk.Label(header,text='LECTURE',bg=BG,fg=INK,font=('Segoe UI',11,'bold')).pack(side='left')
        IconButton(header,'close',self.close_popup,size=26).pack(side='right')
        body=tk.Frame(window,bg=BG);body.pack(fill='x',padx=10)
        def item(label,action,variable=None):
            def choose():
                if variable is not None:variable.set(not variable.get())
                self.close_popup();action()
            mark=('✓  ' if variable.get() else '○  ') if variable is not None else '    '
            button=self.button(body,mark+tr(label),choose,quiet=True)
            button.configure(anchor='w',pady=5,font=('Segoe UI',10))
            button.pack(fill='x',pady=1);self.menu_rows.append(button)
        def line():tk.Frame(body,bg=LINE,height=1).pack(fill='x',padx=10,pady=6)
        item('Что сейчас на лекции?',self.request)
        item('Разобрать свежий слайд',self.analyze_presentation)
        item('По клику разбирать слайд',lambda:None,self.presentation_on_click)
        line()
        item('Звук нового ответа',lambda:save_settings(self.sound.get(),self.volume.get()),self.sound)
        item('Громкость уведомлений…',self.show_sound_settings)
        item('Мигание нового ответа',lambda:None,self.flashing)
        item('Пауза пересказов' if self.local_enabled else 'Включить пересказы',self.toggle_local)
        item('Показать ответы',self.render_card)
        item('Скрыть стопку',self.hide_answers)
        line()
        row=tk.Frame(body,bg=BG);row.pack(fill='x',padx=8,pady=3)
        tk.Label(row,text=tr('Язык'),bg=BG,fg=MUTED,font=('Segoe UI',9)).pack(side='left',padx=(0,12))
        self.language_buttons={}
        for code,label in [('de','DE'),('en','EN'),('ru','RU')]:
            button=self.button(row,label,lambda c=code:self.set_language(c),quiet=True)
            button.configure(bg=GOLD if code==self.language else BG);button.pack(side='left',padx=2)
            self.language_buttons[code]=button
        item('Закрыть помощника',self.root.destroy)
        self.raise_popup()

    def queue_layout(self):
        if self.layout_job is None:self.layout_job=self.root.after_idle(self.layout_now)

    def layout_now(self):
        self.layout_job=None;self.place_bubble()

    def restack(self):
        self.window_group.stack([*reversed(self.back_windows),self.bubble,self.root,self.pill.window,self.composer]+([self.popup] if self.popup else []))
    
    def place_bubble(self):
        if not self.skin_ready:return super().place_bubble()
        sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()-40
        bh=self.bubble.winfo_reqheight()
        pet,front,composer=deck_layout(*self.pet_xy,bh,self.composer_full_height,sw,sh,input_width=self.composer_width)
        self.pet_xy=pet[:2];self.composer_target=composer
        x,y,width,height=front
        placements=[(self.root,pet),(self.bubble,(x,y+self.deck_shift,width,height))]
        for depth,win in enumerate(self.back_windows,1):
            placements.append((win,(x+depth*9,y-depth*24+self.deck_shift*(1-depth*.22),width-depth*18,96)))
        cx,cy,cw,ch=composer
        fraction=self.composer_fraction
        placements.append((self.composer,(cx,cy,cw,ch)))
        placements.append((self.pill.window,(cx-12,cy-12,cw+24,self.pill.max_height+24)))
        self.window_group.move(placements)
        # Regions only change when SIZE changes, never when the windows move.
        self.pill.show_shape(ch,fraction)
        if fraction>=1:
            self.composer_panel.place_configure(x=16,y=9,width=self.composer_width-32,height=ch-18)
        self.window_group.rounded(self.bubble,width,height,18)
        self.card_outlines[0].resize(width,height)
        for depth,win in enumerate(self.back_windows,1):self.window_group.rounded(win,width-depth*18,96,18)
        for depth,outline in enumerate(self.card_outlines[1:],1):outline.resize(width-depth*18,96)

    def update_history(self,entries):
        if not self.skin_ready:return
        entries=entries[-10:]
        key=tuple((e.get('id'),e.get('text')) for e in entries)
        if key==self.history_key:return
        first=self.history_key is None;selected=self.entries[-1-self.offset].get('id') if self.entries else None
        self.history_key=key;was_browsing=self.offset>0;self.entries=entries
        if was_browsing and selected is not None:
            self.offset=next((len(entries)-1-i for i,e in enumerate(entries) if e.get('id')==selected),0)
        else:self.offset=0
        self.render_card()
        if not first and entries:
            if self.sound.get():play('answer',self.volume.get()/100)
            if self.flashing.get():self.blink(4)

    def render_card(self):
        if not self.entries:return
        visibility_changed=self.bubble.state()=='withdrawn';to_show=[]
        e=self.entries[-1-self.offset];self.last_answer=self.entries[-1]['text']
        self.meta.configure(text=e.get('time','')+'  ·  '+e.get('model',tr('Локальная модель'))+'  ·  '+str(e.get('seconds','—'))+' '+tr('с'))
        self.prompt_label.configure(text=e.get('question',''))
        self.answer.configure(text=e['text'])
        self.counter.configure(text=f'{len(self.entries)-self.offset} / {len(self.entries)}')
        for depth,win in enumerate(self.back_windows,1):
            if self.offset+depth<len(self.entries):
                prev=self.entries[-1-self.offset-depth];heading=prev.get('question') or prev['text'].splitlines()[0]
                self.back_labels[depth-1].configure(text=prev.get('time','')+'   '+heading[:47])
                if win.state()=='withdrawn':to_show.append(win);visibility_changed=True
            elif win.state()!='withdrawn':win.withdraw();visibility_changed=True
        self.text.configure(text='')
        if self.bubble.state()=='withdrawn':to_show.append(self.bubble)
        self.bubble.update_idletasks();self.place_bubble()
        for win in to_show:win.update_idletasks();self.window_group.show(win)
        if visibility_changed:self.root.after_idle(self.restack)

    def navigate(self,direction):
        if not self.entries:return
        target=max(0,min(len(self.entries)-1,self.offset+direction))
        if target==self.offset:return
        if self.animation:self.root.after_cancel(self.animation)
        self.offset=target;self.render_card()
        started=time.monotonic();distance=-24 if direction>0 else 24
        def animate():
            t=min(1,(time.monotonic()-started)/.20)
            self.deck_shift=round(distance*(1-t)**3);self.place_bubble()
            if t<1:self.animation=self.root.after(16,animate)
            else:self.animation=None;self.deck_shift=0
        animate()

    def watch(self):
        latest='';last_history=None
        while not self.closed.is_set():
            try:
                state=api('/api/ui-state?after='+latest);latest=state.get('latest','')
                if state.get('entries') is not None:last_history=state['entries'];self.events.put(('history',last_history))
                self.events.put(('telemetry',state))
            except Exception as exc:self.events.put(('connection',str(exc)[:100]))
            self.closed.wait(2)

    def telemetry(self,s):
        self.last_telemetry=s
        self.local_enabled=s.get('localEnabled',False)
        selected=s.get('responseMode','balanced');self.mode.set(selected)
        for mode,button in self.mode_buttons.items():button.configure(bg=GOLD if mode==selected else BG)
        p=s.get('progress',{});task=p.get('task');vision=s.get('vision',{})
        self.processing=bool(task or vision.get('active') or s.get('pendingQuestion'))
        if self.processing and self.eye_job is None:self.thinking_started=time.monotonic();self.animate_thinking()
        elif not self.processing and self.eye_job is not None:
            self.root.after_cancel(self.eye_job);self.eye_job=None;self.draw_eyes()
        if task:label=f"{tr(task['phase'])} · {task['phaseElapsed']} s  /  {tr('всего')} {task['elapsed']} s"
        elif s.get('pendingQuestion'):label='Вопрос в очереди · следующий'
        elif vision.get('active'):label=tr('GPU · фоновый разбор слайда')+f" · {vision['elapsed']} s"
        else:label='● Слушаю Teams' if self.local_enabled else 'Ⅱ Пересказы на паузе'
        if not task and not s.get('pendingQuestion') and not vision.get('active'):label='● Слушаю Teams' if self.local_enabled else 'Ⅱ Пересказы на паузе'
        if s.get('localError'):label='Ошибка · '+s['localError'][:100]
        self.stage.configure(text=tr(label))
        age=max(0,int((time.time()*1000-s.get('liveLast',0))/1000)) if s.get('liveLast') else None
        details=(tr('Прямой канал Teams')+' · '+str(age)+' s '+tr('назад')) if age is not None else tr(s.get('liveStatus','Подключение'))
        last=p.get('last')
        if last and last.get('seconds',0)>0:
            durations=' · '.join(tr(k).split(' · ')[0]+': '+str(round(v/1000,1))+' s' for k,v in last.get('timings',{}).items() if v>=500)
            details+='\n'+tr('Последний запрос: ')+str(last['seconds'])+' s'+(' · '+durations if durations else '')
        self.details.configure(text=details)
        self.canvas.itemconfigure(self.lamp,fill=GOLD if task or vision.get('active') else '#80D5C1')
        self.queue_layout()

    def poll(self):
        try:
            while True:
                kind,message=self.events.get_nowait()
                if kind=='language':self.language_pending=False;self.apply_language(message);continue
                if kind=='language_error':self.language_pending=False;self.show(tr('Не удалось сменить язык: ')+message);continue
                if kind=='history':self.update_history(message);continue
                if kind=='telemetry':
                    if self.skin_ready:self.telemetry(message)
                    continue
                if kind=='connection':
                    if self.skin_ready:self.stage.configure(text=tr('Нет связи с помощником'))
                    continue
                if kind in ('question_done','question_error'):self.question_busy=False
                if kind=='question_done':self.question.delete(0,'end');self.show('Готово · ответ появится в стопке');continue
                if kind in ('answer','info'):self.busy=False
                self.show('' if kind=='answer' else message)
        except queue.Empty:pass
        self.root.after(250,self.poll)

 return StyledPet()
