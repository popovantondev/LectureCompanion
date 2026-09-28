"""Thin native-window shell and local request controller for the styled companion."""
import json,os,queue,threading,time,tkinter as tk,urllib.request,urllib.error
from pathlib import Path
from i18n import tr

BASE='http://127.0.0.1:8765'
POSITION=Path(os.environ.get('LECTURE_DATA_DIR',str(Path(__file__).parent)))/'pet-position.json'

def api(route,post=False,payload=None):
    data=json.dumps(payload).encode('utf-8') if payload is not None else b'' if post else None
    request=urllib.request.Request(BASE+route,data=data,headers={'Origin':BASE,'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=390 if payload else 5) as response:
        raw=response.read()
    return json.loads(raw) if not post or payload is not None else None

class Pet:
    def __init__(self):
        self.root=tk.Tk();self.root.withdraw();self.root.title('Lecture Companion')
        self.root.overrideredirect(True);self.root.attributes('-topmost',True)
        self.root.configure(bg='#ff00ff');self.root.wm_attributes('-transparentcolor','#ff00ff')
        sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        x,y=sw-160,sh-300
        try:
            position=json.loads(POSITION.read_text(encoding='utf-8'))
            x,y=int(position['x']),int(position['y'])
        except (OSError,ValueError,KeyError,TypeError):pass
        self.initial_xy=(max(8,min(x,sw-136)),max(8,min(y,sh-240)))
        self.root.geometry(f'128x148+{self.initial_xy[0]}+{self.initial_xy[1]}')
        self.canvas=tk.Canvas(self.root,width=128,height=148,bg='#ff00ff',highlightthickness=0,cursor='hand2')
        self.canvas.pack();self.lamp=self.canvas.create_oval(0,0,1,1,fill='#80D5C1',outline='')
        self.bubble,self.previous,self.composer=[tk.Toplevel(self.root) for _ in range(3)]
        for window in (self.bubble,self.previous,self.composer):
            window.withdraw();window.overrideredirect(True);window.attributes('-topmost',True)
        self.busy=False;self.question_busy=False;self.events=queue.Queue();self.last_answer=''
        self.provider=tk.StringVar(value='local');self.presentation_on_click=tk.BooleanVar(value=False)
        self.sound=tk.BooleanVar(value=True);self.flashing=tk.BooleanVar(value=True)
        self.history_key=None;self.local_enabled=False;self.hide_question_job=None
        self.closed=threading.Event()
        self.root.bind('<Destroy>',lambda e:self.closed.set() if e.widget==self.root else None,add='+')
        threading.Thread(target=self.watch,daemon=True).start();self.root.after(100,self.poll)

    def place_bubble(self):pass
    def reveal_question(self,event=None):pass
    def blink(self,count):pass

    def press(self,event):
        self.anchor=(event.x_root,event.y_root,*self.initial_xy);self.moved=False

    def drag(self,event):pass

    def release(self,event):
        if self.moved:
            try:POSITION.write_text(json.dumps({'x':self.root.winfo_x(),'y':self.root.winfo_y()}),encoding='utf-8')
            except OSError:pass
        else:self.request()

    def defer_hide_question(self,event=None):
        if self.hide_question_job:self.root.after_cancel(self.hide_question_job)
        self.hide_question_job=self.root.after(600,self.hide_question)

    def request(self):
        if self.presentation_on_click.get():self.analyze_presentation();return
        if self.busy:self.show('Ещё читаю лекцию. Повторный запрос не отправляю.');return
        self.busy=True;self.show('Читаю новые слова преподавателя…')
        threading.Thread(target=self.fetch,daemon=True).start()

    def fetch(self):
        try:
            before=api('/api/state');old=before.get('entries',[])
            if not before.get('localBusy'):api('/api/local-run',True)
            deadline=time.monotonic()+195
            while time.monotonic()<deadline and not self.closed.is_set():
                state=api('/api/state')
                if not state.get('localBusy'):
                    if state.get('localError'):raise RuntimeError(state['localError'])
                    entries=state.get('entries',[])
                    if entries and entries!=old:self.events.put(('answer',entries[-1]['text']))
                    else:self.events.put(('info','Новых слов пока мало или нет. Запрос к модели не понадобился.'))
                    return
                self.closed.wait(1)
            if not self.closed.is_set():raise RuntimeError('Ответ задерживается. Автоматически повторять запрос не буду.')
        except Exception as exc:self.events.put(('info',tr('Не получилось получить пересказ.\n')+str(exc)[:260]))

    def toggle_local(self):
        def work():
            try:
                api('/api/local-toggle',True);state=api('/api/state')
                self.events.put(('notice','Локальные пересказы включены.' if state['localEnabled'] else 'Локальные пересказы на паузе. Текущий ответ может ещё прийти.'))
            except Exception as exc:self.events.put(('notice',str(exc)[:200]))
        threading.Thread(target=work,daemon=True).start()

    def submit_question(self,question):
        self.question_busy=True
        def work():
            try:
                entry=api('/api/ask',True,{'question':question})
                self.events.put(('question_done',entry['text']))
            except Exception as exc:self.events.put(('question_error',tr('Не получилось: ')+str(exc)[:220]))
        threading.Thread(target=work,daemon=True).start()

    def analyze_presentation(self):
        if self.question_busy:self.show('Вопрос уже обрабатывается. Дождись ответа.');return
        self.show('Снимаю свежую презентацию Teams и анализирую локально…')
        self.submit_question(tr('Разобрать презентацию'))

    def ask(self):
        question=self.question.get().strip()
        if not question:self.question.focus_set();return
        if self.question_busy:self.show('Твой вопрос уже принят. Он идёт перед следующим пересказом.');return
        if len(question)>2000:self.show('Вопрос слишком длинный: максимум 2000 символов.');return
        self.show('Отвечаю локально. Если идёт пересказ, сначала дождусь его…')
        self.submit_question(question)

if __name__=='__main__':
    from pet_ui import run
    run(Pet,api).root.mainloop()
