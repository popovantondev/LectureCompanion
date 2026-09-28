"""Small Windows launcher; model runtimes remain external and are never downloaded here."""
import ctypes
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import urllib.request
from PIL import Image, ImageTk
from pet_ui import run
from loading_surface import LoadingSurface
from robot_sound import play,settings,save_settings
from i18n import tr,set_language
from portable_config import load_config

RESOURCE = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
BUNDLE = Path(sys.executable).parent if getattr(sys,'frozen',False) else RESOURCE
PORTABLE = (BUNDLE/'portable.json').is_file() or (BUNDLE/'Laufzeit/python/python.exe').is_file()
DATA = BUNDLE/'Daten' if PORTABLE else Path(os.environ.get('LECTURE_DATA_DIR', str(Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'LectureCompanion')))
BASE = 'http://127.0.0.1:8765'
VERSION=json.loads((RESOURCE/'version.json').read_text(encoding='utf-8'))['version']

def request(url, post=False):
    req=urllib.request.Request(url,data=b'' if post else None,headers={'Origin':BASE})
    with urllib.request.urlopen(req,timeout=3) as response:
        raw=response.read()
    try:return json.loads(raw)
    except ValueError:return raw.decode()

def healthy(url,field,value):
    try:return request(url).get(field)==value
    except Exception:return False

def load_pet():
    loader=importlib.machinery.SourceFileLoader('lecture_pet',str(RESOURCE/'pet.pyw'))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec);loader.exec_module(module)
    return module

def main():
    demo='--demo' in sys.argv or Path(sys.executable).stem=='LectureCompanionDemo'
    ctypes.windll.kernel32.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_wchar_p]
    ctypes.windll.kernel32.CreateMutexW.restype=ctypes.c_void_p
    ctypes.windll.kernel32.CloseHandle.argtypes=[ctypes.c_void_p]
    ctypes.windll.kernel32.SetDllDirectoryW.argtypes=[ctypes.c_wchar_p]
    mutex=ctypes.windll.kernel32.CreateMutexW(None,False,'Local\\LectureCompanionDemo' if demo else 'Local\\LectureCompanionUI')
    if ctypes.windll.kernel32.GetLastError()==183:return
    DATA.mkdir(parents=True,exist_ok=True);os.environ['LECTURE_DATA_DIR']=str(DATA)
    preferences=settings();language=preferences['language']
    if '--language' in sys.argv:language=sys.argv[sys.argv.index('--language')+1]
    set_language(language)
    if not demo:save_settings(preferences['sound'],preferences['volume'],language)
    else:os.environ['LECTURE_UI_LANGUAGE']=language
    splash=tk.Tk();splash.title('Lecture Companion');splash.overrideredirect(True)
    splash.attributes('-topmost',True)
    splash.geometry(f'280x330+{(splash.winfo_screenwidth()-280)//2}+{(splash.winfo_screenheight()-330)//2}')
    with Image.open(RESOURCE/'assets'/'companion.png') as image:
        surface=LoadingSurface(splash,image)
        image.thumbnail((170,190),Image.Resampling.LANCZOS);portrait=ImageTk.PhotoImage(image)
    splash.iconphoto(True,portrait)
    if not demo:play('startup')
    def animate_loading():
        before=time.monotonic();surface.paint()
        # No backlog: animation follows wall time, with a bounded 30 FPS budget.
        splash.after(max(1,33-round((time.monotonic()-before)*1000)),animate_loading)
    splash.after(33,animate_loading)
    events=queue.Queue();owned=[];cancel=threading.Event();started=time.monotonic();failed=False
    def stop_owned():
        cancel.set()
        if any(kind=='server' for kind,_ in owned):
            try:request(BASE+'/api/shutdown',True)
            except Exception:pass
        for _,child in reversed(owned):
            if child.poll() is None:
                subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    def start_process(kind,args,env):
        if cancel.is_set():raise RuntimeError(tr('Запуск отменён'))
        with (DATA/(kind+'.log')).open('ab') as log:
            if getattr(sys,'frozen',False):ctypes.windll.kernel32.SetDllDirectoryW(None)
            try:child=subprocess.Popen(args,cwd=RESOURCE,env=env,creationflags=subprocess.CREATE_NO_WINDOW,stdout=log,stderr=log)
            finally:
                if getattr(sys,'frozen',False):ctypes.windll.kernel32.SetDllDirectoryW(str(RESOURCE))
        owned.append((kind,child));return child
    def wait_ready(url,field,value,child,seconds):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            if cancel.is_set():raise RuntimeError(tr('Запуск отменён'))
            if child.poll() is not None:raise RuntimeError(tr('Компонент завершился. Подробности в папке журналов.'))
            if healthy(url,field,value):return
            if ':8766/' in url:
                try:
                    status=json.loads((DATA/'runtime-startup.json').read_text(encoding='utf-8'))
                    if status['time']>=time.time()-3:events.put(('stage',(1,tr(status['stage'])+' · '+status.get('device',''))))
                except (OSError,ValueError,KeyError):pass
            cancel.wait(.5)
        raise RuntimeError(tr('Запуск занял слишком долго. Проверь модель и драйвер NPU.'))
    def boot():
        try:
            if demo:
                events.put(('ready',None));return
            bundle=Path(sys.executable).parent if getattr(sys,'frozen',False) else RESOURCE
            try:config=load_config(bundle,DATA)
            except FileNotFoundError:raise RuntimeError(tr('Сначала настрой local.json по инструкции INSTALL.ru.md.'))
            env=os.environ.copy()
            env.update(DO_NOT_TRACK='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',OLLAMA_NO_CLOUD='1',
                       OLLAMA_HOST='127.0.0.1:11435',OLLAMA_IGPU_ENABLE='1',OLLAMA_VULKAN='1')
            if PORTABLE:
                for url in (BASE+'/health','http://127.0.0.1:8766/health','http://127.0.0.1:11435/api/version'):
                    try:request(url)
                    except (urllib.error.URLError,TimeoutError):continue
                    raise RuntimeError(tr('Порт помощника занят. Закрой прежнюю копию перед запуском переносимой версии.'))
            env['LECTURE_MODEL_ROOT']=config['model_root'];env['LECTURE_OLLAMA']=config.get('ollama','')
            if config.get('ollama_models'):env['OLLAMA_MODELS']=config['ollama_models']
            events.put(('stage',(1,'Проверка локальной модели…')))
            if not healthy('http://127.0.0.1:8766/health','protocol',3):
                try:
                    request('http://127.0.0.1:8766/health')
                    raise RuntimeError(tr('Работает старая версия NPU-сервиса. Закрой её перед обновлением.'))
                except (urllib.error.URLError,TimeoutError):pass
                child=start_process('npu',[config['npu_python'],str(RESOURCE/'runtime_boot.py'),str(RESOURCE/'npu-server.py')],env)
                events.put(('stage',(1,'Загрузка модели на NPU. Первый запуск дольше…')))
                wait_ready('http://127.0.0.1:8766/health','protocol',3,child,660)
            env['LECTURE_TEXT_DEVICE']=request('http://127.0.0.1:8766/health')['device']
            events.put(('stage',(2,'Запуск прямого канала Teams…')))
            if not healthy(BASE+'/health','service','lecture-companion'):
                node=config.get('node') or shutil.which('node')
                if not node:raise RuntimeError(tr('Не найден Node.js. Укажи путь node в local.json.'))
                child=start_process('server',[node,str(RESOURCE/'server.js')],env)
                wait_ready(BASE+'/health','service','lecture-companion',child,30)
                if '--paused' not in sys.argv:request(BASE+'/api/local-toggle',True)
            try:request('http://127.0.0.1:11435/api/version')
            except (urllib.error.URLError,TimeoutError):
                child=start_process('vision',[config['ollama'],'serve'],env)
                deadline=time.monotonic()+30
                while time.monotonic()<deadline:
                    if cancel.is_set():raise RuntimeError(tr('Запуск отменён'))
                    if child.poll() is not None:raise RuntimeError(tr('Компонент завершился. Подробности в папке журналов.'))
                    try:request('http://127.0.0.1:11435/api/version');break
                    except (urllib.error.URLError,TimeoutError):cancel.wait(.5)
                else:raise RuntimeError('Ollama startup timed out')
            events.put(('stage',(3,'Открываю помощника…')));events.put(('ready',None))
        except Exception as exc:events.put(('error',str(exc)))
    def close():stop_owned();splash.destroy()
    splash.bind('<Escape>',lambda e:close())
    def poll():
        nonlocal failed
        while True:
            try:kind,value=events.get_nowait()
            except queue.Empty:break
            if kind=='stage':surface.step=value[0];surface.label=tr(value[1])
            elif kind=='error':
                failed=True;surface.label=tr('Не удалось запустить компонент')
                panel=tk.Toplevel(splash);panel.title(tr('Настройка помощника'));panel.attributes('-topmost',True);panel.configure(bg='#FAFBFD',padx=20,pady=20)
                tk.Label(panel,text=value,wraplength=360,bg='#FAFBFD',fg='#A34747',font=('Segoe UI',11)).pack(pady=(0,15))
                tk.Button(panel,text=tr('Инструкция'),command=lambda:os.startfile(RESOURCE/'Anleitungen'/({'de':'Deutsch','en':'English','ru':'Russisch'}[language]+'.html'))).pack(side='left')
                tk.Button(panel,text=tr('Закрыть'),command=close).pack(side='right');panel.protocol('WM_DELETE_WINDOW',close)
            elif kind=='ready':
                surface.step=4;surface.paint();splash.update_idletasks();splash.destroy();return
        splash.after(100,poll)
    threading.Thread(target=boot,daemon=True).start();splash.after(100,poll);splash.mainloop()
    if cancel.is_set() or failed:return
    legacy=load_pet()
    if demo:
        def fake_api(*args,**kwargs):return {'latest':'demo','entries':None,'localEnabled':False,'progress':{},'vision':{}}
        legacy.api=fake_api
        class DemoPet(legacy.Pet):
            def ask(self):self.show('Демонстрация: запросы отключены.')
            request=ask;analyze_presentation=ask;toggle_local=ask
        pet=run(DemoPet,fake_api)
        pet.update_history([{'id':i,'time':f'10:0{i}:00','provider':'local','model':tr('Демонстрация · без модели'),'seconds':12,'text':tr(text)} for i,text in enumerate([
            'Тема: IP-адреса.\nГлавное: адрес помогает доставлять данные нужному устройству.',
            'Тема: локальная сеть.\nГлавное: коммутатор соединяет устройства внутри сети.',
            'Тема: резервные копии.\nГлавное: отдельная копия позволяет восстановить потерянные файлы.',
            'Тема: защита данных.\nГлавное: доступ получают только нужные сотрудники.\nТебе: нового задания нет.'
        ])]);pet.reveal_question()
        pet.ask=lambda:pet.show('Демонстрация: запросы отключены.');pet.request=pet.ask;pet.analyze_presentation=pet.ask
    else:pet=run(legacy.Pet,legacy.api)
    (DATA/('demo-ready.json' if demo else 'ui-ready.json')).write_text(json.dumps({'pid':os.getpid(),'version':VERSION,'demo':demo,'cards':1+len(pet.back_windows),'native_alpha':hasattr(pet,'renderer'),'language':pet.language,'historyLimit':10,'started':time.time()}),encoding='utf-8')
    if demo and '--smoke-test' in sys.argv:pet.root.after(1200,pet.root.destroy)
    try:pet.root.mainloop()
    finally:stop_owned();ctypes.windll.kernel32.CloseHandle(mutex)

if __name__=='__main__':main()
