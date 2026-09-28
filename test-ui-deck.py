"""Synthetic native-UI checks. Never opens Teams or calls a model."""
import importlib.machinery,importlib.util,sys,time,faulthandler
faulthandler.dump_traceback_later(180)
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
loader=importlib.machinery.SourceFileLoader('legacy_pet',str(Path(__file__).with_name('pet.pyw')))
spec=importlib.util.spec_from_loader(loader.name,loader);legacy=importlib.util.module_from_spec(spec);loader.exec_module(legacy)
from pet_ui import run
from window_group import deck_layout

def fake_api(*args,**kwargs):return {'latest':'','entries':None,'localEnabled':False,'progress':{},'vision':{}}
pet=run(legacy.Pet,fake_api);pet.sound.set(False);pet.closed.set()
def settle(ms=120):
 pet.root.after(ms,pet.root.quit);pet.root.mainloop()
 # Timer expiry can precede Tk's final idle geometry pass on a loaded desktop.
 pet.root.update_idletasks()
def capture(name,windows,target=None):
 from PIL import ImageGrab
 windows=[w for w in windows if w.winfo_viewable()]
 box=(min(w.winfo_rootx() for w in windows)-14,min(w.winfo_rooty() for w in windows)-14,max(w.winfo_rootx()+w.winfo_width() for w in windows)+14,max(w.winfo_rooty()+w.winfo_height() for w in windows)+14)
 backdrop=legacy.tk.Toplevel(pet.root);backdrop.overrideredirect(True);backdrop.configure(bg='#DDE5ED');backdrop.attributes('-topmost',True)
 backdrop.geometry(f'{box[2]-box[0]}x{box[3]-box[1]}+{box[0]}+{box[1]}');backdrop.update()
 pet.restack()
 if pet.popup:pet.popup.lift()
 settle(120);ImageGrab.grab(bbox=box,all_screens=True).save(target or Path(__file__).with_name(name));backdrop.destroy()

try:
 entries=[{'id':i,'time':'12:30:00','provider':'local','model':'Qwen NPU','text':'Тема: сетевой уровень.\nГлавное: IP помогает передавать пакеты между сетями.\nТебе: нового задания нет.','seconds':20} for i in range(5)]
 pet.pet_xy=(650,650);pet.update_history(entries);pet.place_bubble();settle()
 before_open=pet.window_group.move_batches
 pet.reveal_question();settle(300)
 assert pet.window_group.move_batches-before_open<=2,'Opening must animate cached pixels, not resize native windows every frame'
 assert pet.composer.winfo_x()==pet.composer_target[0] and pet.composer.winfo_y()==pet.composer_target[1]
 assert pet.pill.window.winfo_x()==pet.composer.winfo_x()-12 and pet.pill.window.winfo_y()==pet.composer.winfo_y()-12
 face=pet.pill.frame(620,56)
 assert face.getpixel((322,40))==(250,251,253,255)
 assert all(abs(a-b)<=3 for a,b in zip(face.getpixel((322,12))[:3],(220,227,235)))
 assert face.getpixel((12,12))[3]<15,'Capsule corners must remain transparent'
 pet.question.focus_force();settle(20)
 assert len(pet.back_windows)==3 and all(w.winfo_viewable() for w in pet.back_windows)
 assert pet.composer.winfo_width()==620 and pet.composer.winfo_height()==56,pet.composer.geometry()
 assert pet.question.winfo_height()<50 and pet.slide_button.winfo_width()==36,(pet.question.geometry() if hasattr(pet.question,'geometry') else pet.question.winfo_height(),pet.slide_button.winfo_width(),pet.composer_animation)
 assert pet.slide_button.winfo_rootx()<pet.send_button.winfo_rootx()
 assert pet.slide_label.winfo_rootx()<pet.slide_button.winfo_rootx()
 assert [round(w.attributes('-alpha'),2) for w in pet.back_windows]==[.88,.72,.57]
 assert pet.bubble.attributes('-alpha')==1
 pet.question.insert('1.0','Первая строка\nВторая строка\nТретья строка\nЧетвёртая строка');settle()
 assert pet.composer.winfo_height()>=110 and '\n' in pet.question.get(),pet.composer.geometry()
 assert pet.composer.winfo_y()>=pet.root.winfo_y()+pet.root.winfo_height()+8
 assert pet.composer.winfo_y()>=pet.bubble.winfo_y()+pet.bubble.winfo_height()+8
 if '--preview' in sys.argv:capture('ui-preview.png',[pet.root,pet.bubble,*pet.back_windows,pet.composer])
 pet.question.delete(0,'end');settle();assert pet.composer.winfo_height()==56
 pet.question.insert('1.0','Очень длинный вопрос о лекции, который автоматически переносится. '*16);settle()
 assert 56<pet.composer.winfo_height()<=196,(pet.composer.geometry(),pet.composer_full_height,pet.composer_fraction)
 pet.question.delete(0,'end');settle()
 pet.bubble.detached=True
 positions=[(w.winfo_x(),w.winfo_y()) for w in [pet.root,pet.bubble,*pet.back_windows,pet.composer,pet.pill.window]]
 pet.press(SimpleNamespace(x_root=700,y_root=710))
 pet.drag(SimpleNamespace(x_root=770,y_root=690));settle(40)
 with patch('pathlib.Path.write_text'):pet.release(SimpleNamespace(x_root=770,y_root=690),header=True)
 settle()
 for win,(x,y) in zip([pet.root,pet.bubble,*pet.back_windows,pet.composer,pet.pill.window],positions):
  assert abs(win.winfo_x()-x-70)<=1 and abs(win.winfo_y()-y+20)<=1,(win.geometry(),x,y)
 counters={'stack':0,'unmap':0};original_stack=pet.restack
 pet.restack=lambda:counters.__setitem__('stack',counters['stack']+1)
 for win in [pet.bubble,*pet.back_windows]:win.bind('<Unmap>',lambda e:counters.__setitem__('unmap',counters['unmap']+1))
 state={'localEnabled':True,'responseMode':'deep','progress':{},'vision':{}}
 pet.telemetry(state);settle();before=pet.window_group.move_batches
 for _ in range(20):pet.telemetry(state);pet.place_bubble()
 settle();assert pet.window_group.move_batches==before,(pet.window_group.move_batches,before)
 assert counters=={'stack':0,'unmap':0},counters
 pet.press(SimpleNamespace(x_root=700,y_root=710))
 for i in range(30):
  pet.drag(SimpleNamespace(x_root=700+i*2,y_root=710-i));settle(18)
 with patch('pathlib.Path.write_text'):pet.release(SimpleNamespace(x_root=758,y_root=681),header=True)
 assert counters=={'stack':0,'unmap':0},counters
 pet.restack=original_stack
 assert not pet.presentation_on_click.get() and pet.mode.get()=='deep'
 pet.navigate(1);settle(240);assert pet.offset==1 and pet.bubble.attributes('-alpha')==1
 pet.update_history(entries+[dict(entries[-1],id=6)]);assert pet.offset==2
 pet.navigate(-999);settle(240);assert pet.offset==0
 pet.telemetry({'localEnabled':True,'progress':{'task':{'phase':'NPU','elapsed':12,'phaseElapsed':10}},'vision':{}})
 assert '12' in pet.stage.cget('text')
 pet.telemetry(state);settle()
 with patch('pet_ui.save_settings'),patch('pet_ui.play') as sound:
  pet.show_sound_settings();settle();pet.volume_choose(0);assert not pet.sound.get()
  pet.volume_buttons[0].invoke();sound.assert_called_with('answer',0,preview=True)
  pet.volume_buttons[1].invoke();sound.assert_called_with('answer',.33,preview=True)
  pet.volume_buttons[2].invoke();sound.assert_called_with('answer',.67,preview=True)
  pet.volume_buttons[3].invoke();sound.assert_called_with('answer',1,preview=True)
  pet.volume_choose(75);assert pet.sound.get() and pet.volume.get()==75
  pet.volume_track.event_generate('<ButtonRelease-1>',x=170,y=12);sound.assert_called_with('answer',.75,preview=True)
  if '--preview' in sys.argv:capture('volume-preview.png',[pet.popup])
 pet.close_popup();pet.sound.set(False)
 pet.composer.withdraw();pet.pill.window.withdraw();pet.composer_fraction=0
 pet.pet_xy=(700,600);pet.place_bubble();settle(30);pet.reveal_question();settle(300)
 assert pet.composer.winfo_x()==pet.composer_target[0] and pet.pill.window.winfo_x()==pet.composer.winfo_x()-12
 pet.root.focus_force();pet.question_changed();settle(80)
 if pet.hide_question_job:pet.root.after_cancel(pet.hide_question_job);pet.hide_question_job=None
 assert abs(pet.placeholder.winfo_rootx()-(pet.composer.winfo_rootx()+16))<=1
 assert abs(pet.placeholder.winfo_rooty()+pet.placeholder.winfo_height()/2-(pet.composer.winfo_rooty()+28))<=1
 pet.hover_enter();settle(200);assert pet.hover_offset==-5
 pet.hover_leave();settle(200);assert pet.hover_offset==0
 if '--preview' in sys.argv:capture('ui-preview-capsule.png',[pet.root,pet.bubble,*pet.back_windows,pet.composer])
 for xy in [(650,8),(1400,900),(650,420)]:
  pet.pet_xy=xy;pet.place_bubble();settle()
  p,b,c=deck_layout(*pet.pet_xy,pet.bubble.winfo_reqheight(),pet.composer_full_height,pet.root.winfo_screenwidth(),pet.root.winfo_screenheight()-40)
  assert c[1]>=p[1]+p[3]+8
  assert b[1]+b[3]<=c[1] or b[1]>=c[1]+c[3],(p,b,c)
 # Regression: menu is above composer, also after any delayed stack operation.
 pet.pet_xy=(650,550);pet.place_bubble();pet.reveal_question();settle(280)
 pet.menu(SimpleNamespace(x_root=760,y_root=550));settle(100)
 popup=pet.popup
 pet.reveal_question();pet.restack();settle(60)
 assert pet.popup is popup and popup.winfo_viewable()
 import ctypes
 from ctypes import wintypes
 u=ctypes.windll.user32;u.GetWindow.argtypes=[wintypes.HWND,wintypes.UINT];u.GetWindow.restype=wintypes.HWND
 top=pet.window_group.handle(popup)
 above=u.GetWindow(top,3)
 # GW_HWNDPREV walks windows above the popup.
 owned={pet.window_group.handle(w) for w in [pet.root,pet.composer,pet.pill.window,pet.bubble,*pet.back_windows]}
 seen=set()
 while above and above not in seen:
  seen.add(above)
  assert above not in owned,'Another companion window covers its context menu'
  above=u.GetWindow(above,3)
 if '--preview' in sys.argv:capture('test-preview-menu.png',[popup,pet.root,pet.composer])
 pet.close_popup()
 from i18n import tr
 with patch('pet_ui.save_settings'):
  for language in ['de','en','ru']:
   pet.apply_language(language);settle(50)
   assert pet.placeholder.cget('text')==tr('Спроси о лекции…')
   pet.root.focus_force();pet.question_changed();settle(30)
   assert pet.placeholder.winfo_rootx()+pet.placeholder.winfo_width()<pet.slide_label.winfo_rootx(),'Placeholder overlaps controls'
   pet.menu(SimpleNamespace(x_root=760,y_root=350));settle(80)
   assert all(b.winfo_rooty()+b.winfo_height()<=pet.popup.winfo_rooty()+pet.popup.winfo_height() for b in pet.menu_rows),'Clipped menu'
   if '--preview' in sys.argv:capture('test-preview-'+language+'.png',[pet.popup,pet.bubble,pet.root,pet.composer])
   pet.close_popup()
 pet.update_history([dict(entries[0],id=i) for i in range(30)]);assert len(pet.entries)==10
 from binary_visor import BinaryVisor
 visor=BinaryVisor();first=visor.render(.6)
 assert len(visor.bits)==10 and set(visor.bits)<=set('01')
 assert first.tobytes()!=visor.render(2.2).tobytes(),'Sweep must have a quiet pause'
 assert len(visor.glyphs)<=18
 pet.processing=True;pet.eye_phase=.6;pet.draw_eyes()
 if '--preview' in sys.argv:capture('test-preview-binary.png',[pet.root])
 pet.processing=False;pet.draw_eyes()
 with patch('pet_ui.play') as effect:
  pet.sound.set(True);pet.sound_times={}
  for _ in range(10):pet.sound_effect('drag')
  assert effect.call_count==1,'Motion audio must be throttled'
 pet.sound.set(False)
 print('PASS: popup on top, three live UI languages, no clipped menu/placeholder, 10 answers, binary sweep/pause, throttled drag sound.')
 pet.hide_answers();settle(60)
 assert all(not w.winfo_viewable() for w in [pet.bubble,*pet.back_windows,pet.composer,pet.pill.window])
 print('PASS: antialiased capsule and uniform outline; left-aligned placeholder; note/slider previews (audio mocked); fixed-size reveal; remap after drag; smooth subpixel hover.')
 print('PASS: anchored drag, zero idle moves/remaps/restacks, opaque main + 3 translucent cards, deck navigation, circle input, wrapped auto-height, rocket/image, volume popup, timers, screen edges.')
 if '--release-screenshots' in sys.argv:
  from i18n import tr
  screenshot_dir=Path(__file__).parent/'docs'/'screenshots';screenshot_dir.mkdir(parents=True,exist_ok=True)
  demo_texts=[
   'Тема: IP-адреса.\nГлавное: адрес помогает доставлять данные нужному устройству.',
   'Тема: локальная сеть.\nГлавное: коммутатор соединяет устройства внутри сети.',
   'Тема: резервные копии.\nГлавное: отдельная копия позволяет восстановить потерянные файлы.',
   'Тема: защита данных.\nГлавное: доступ получают только нужные сотрудники.\nТебе: нового задания нет.'
  ]
  with patch('pet_ui.save_settings'):
   for language in ('de','en','ru'):
    pet.apply_language(language)
    pet.text.configure(text='')
    entries=[{'id':100+index,'time':f'10:2{index}:00','provider':'local','model':tr('Демонстрация · без модели',language),'seconds':12,'text':tr(text,language)} for index,text in enumerate(demo_texts)]
    pet.update_history(entries);pet.telemetry({'localEnabled':False,'responseMode':'balanced','progress':{},'vision':{}});pet.pet_xy=(650,650);pet.processing=False;pet.draw_eyes();pet.place_bubble();pet.reveal_question();settle(420)
    capture(f'app-{language}.png',[pet.root,pet.bubble,*pet.back_windows,pet.composer],screenshot_dir/f'app-{language}.png')
    pet.hide_answers();settle(80)
  print('PASS: generated three isolated, synthetic UI screenshots; each uses one UI and answer language.')
finally:pet.root.destroy()
