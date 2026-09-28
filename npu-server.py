"""Loopback-only, single-request OpenVINO NPU runtime. No cloud fallback."""
import json,re,threading,time,os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import openvino_genai as genai
from device_runtime import select_pipeline
from i18n import tr

ROOT=Path(os.environ.get('LECTURE_MODEL_ROOT',str(Path.home()/'LectureModels')))
lock=threading.Lock()
pipe,DEVICE,SELECTION=select_pipeline(ROOT)
tokenizer=pipe.get_tokenizer()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,code,value):
        data=json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)));self.end_headers()
        try:self.wfile.write(data)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_GET(self):
        if self.path=='/health':self.reply(200,{'ready':True,'protocol':3,'device':DEVICE,'model':'Qwen3-8B','busy':lock.locked(),'selection':SELECTION})
        else:self.reply(404,{})
    def do_POST(self):
        if self.path!='/generate':return self.reply(404,{})
        if self.headers.get('Origin')!='http://127.0.0.1:8765':return self.reply(403,{})
        length=int(self.headers.get('Content-Length','0'))
        if not 0<length<=64000:return self.reply(413,{'error':'Request too large'})
        try:
            body=json.loads(self.rfile.read(length))
            reasoning=body.get('reasoning') is True
            switch=' /think' if reasoning else ' /no_think'
            system=body['system']+switch
            prompt=body['prompt']+switch
            limit=max(80,min(512,int(body.get('max_new_tokens',240))))
            if not isinstance(system,str) or not isinstance(prompt,str):raise ValueError()
        except Exception:return self.reply(400,{'error':'Invalid request'})
        if not lock.acquire(blocking=False):return self.reply(409,{'error':DEVICE+' is busy'})
        started=time.perf_counter();chat=False;trimmed=False
        try:
            # Keep newest speech / user question at the end, drop oldest context first.
            while tokenizer.encode(system+'\n'+prompt).input_ids.shape[-1]>1750:
                trimmed=True
                if len(prompt)<200:raise ValueError('System prompt exceeds context limit')
                prompt=prompt[max(100,len(prompt)//10):]
            pipe.start_chat(system);chat=True
            output=str(pipe.generate(prompt,max_new_tokens=limit,do_sample=False))
            if '</think>' in output:answer=output.split('</think>',1)[1].strip()
            elif '<think>' in output or reasoning:answer=tr('Разбор не уложился в заданный лимит. Выбери «Обычно» или задай более короткий вопрос.',body.get('language','de'))
            else:answer=output.strip()
            if not answer:raise RuntimeError('NPU returned empty text')
            self.reply(200,{'response':answer,'device':DEVICE,'reasoning':reasoning,'max_new_tokens':limit,'context_trimmed':trimmed,'seconds':round(time.perf_counter()-started,2)})
        except Exception as exc:self.reply(500,{'error':str(exc)})
        finally:
            if chat:
                try:pipe.finish_chat()
                except Exception:pass
            lock.release()

if __name__=='__main__':
    print(DEVICE+' ready on 127.0.0.1:8766',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
