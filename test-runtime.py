"""Explicit local-only integration check. Run only with automatic summaries paused."""
import json,urllib.request

def request(path,body=None):
    req=urllib.request.Request('http://127.0.0.1:'+path,data=json.dumps(body,ensure_ascii=False).encode() if body else None,headers={'Origin':'http://127.0.0.1:8765','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as response:return json.load(response)

assert request('8765/health')['localOnly'] is True
assert request('8766/health')['protocol']==3
state=request('8765/api/ui-state?after=skip')
assert not state['localEnabled'] and not state['localBusy'],'Pause automatic summaries before this check'
for reasoning,tokens in [(False,160),(True,512)]:
    result=request('8766/generate',{'system':'Ответь по-русски коротко.','prompt':'Сколько будет 7 умножить на 8? В ответе достаточно числа.','reasoning':reasoning,'max_new_tokens':tokens})
    assert result['reasoning']==reasoning and result['max_new_tokens']==tokens
    assert '<think>' not in result['response'] and '</think>' not in result['response']
    assert '56' in result['response'],result['response']
    print(json.dumps({'reasoning':reasoning,'seconds':result['seconds'],'answer':result['response']},ensure_ascii=False),flush=True)
print('PASS: real local fast and thinking modes; no cloud calls.')
