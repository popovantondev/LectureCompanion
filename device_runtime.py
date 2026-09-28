"""Select an installed local OpenVINO device. Benchmark fallback sequentially once.

No packages, models or drivers are installed here. Probe processes are isolated
and bounded; failed drivers cannot leave a second inference process behind.
"""
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path

def data_dir():
    return Path(os.environ.get('LECTURE_DATA_DIR',str(Path.home()/'LectureCompanion')))

def report(stage,device=''):
    data_dir().mkdir(parents=True,exist_ok=True)
    (data_dir()/'runtime-startup.json').write_text(json.dumps({'stage':stage,'device':device,'time':time.time()}),encoding='utf-8')

def options(device,root):
    config={'CACHE_DIR':str(root/('cache-'+device.replace('.','-')))}
    if device=='NPU':config.update(MAX_PROMPT_LEN=2048,MIN_RESPONSE_LEN=256)
    elif device=='CPU':config.update(INFERENCE_NUM_THREADS=min(4,os.cpu_count() or 2),PERFORMANCE_HINT='LATENCY')
    return config

def fingerprint(core,model):
    import openvino as ov
    devices={}
    for device in core.available_devices:
        properties={}
        for key in ('FULL_DEVICE_NAME','DRIVER_VERSION','DEVICE_UUID'):
            try:properties[key]=str(core.get_property(device,key))
            except Exception:pass
        devices[device]=properties
    files=[(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in model.iterdir() if p.is_file()]
    value={'schema':1,'ov':ov.__version__,'devices':devices,'model':str(model),'files':sorted(files),'platform':platform.platform()}
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def rank_results(results):
    return sorted((r for r in results if r.get('ok') and r.get('seconds',0)>0),key=lambda r:r['seconds'])

def probe(device,root,timeout=150):
    command=[sys.executable,str(Path(__file__).resolve()),'--probe',device,str(root)]
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        out,err=child.communicate(timeout=timeout)
        for line in reversed(out.decode('utf-8',errors='replace').splitlines()):
            if line.startswith('BENCHMARK_JSON='):return json.loads(line.split('=',1)[1])
        return {'device':device,'ok':False,'error':'probe failed','exitCode':child.returncode}
    except subprocess.TimeoutExpired:
        if os.name=='nt':subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:child.kill()
        child.communicate()
        return {'device':device,'ok':False,'error':'benchmark timeout'}

def fallback_candidates(core):
    return [d for d in core.available_devices if d=='CPU' or d.startswith('GPU')]

def select_pipeline(root):
    import openvino as ov
    import openvino_genai as genai
    core=ov.Core();model=root/'Qwen3-8B-int4-cw-ov'
    if not (model/'openvino_model.xml').exists():raise RuntimeError('OpenVINO model missing: '+str(model))
    def load(device):
        report('Загрузка модели',device)
        return genai.LLMPipeline(str(model),device,options(device,root))
    # Preserve the tested NPU route; do not benchmark it on every start.
    if 'NPU' in core.available_devices:
        try:return load('NPU'),'NPU',{'selection':'NPU preferred'}
        except Exception as exc:print('NPU unavailable, trying measured fallback:',str(exc)[:200],flush=True)
    candidates=fallback_candidates(core)
    if not candidates:raise RuntimeError('No compatible OpenVINO CPU/GPU device found')
    key=fingerprint(core,model);cache=data_dir()/'device-benchmark.json';saved={}
    try:saved=json.loads(cache.read_text(encoding='utf-8'))
    except (OSError,ValueError):pass
    ranked=rank_results(saved.get('results',[])) if saved.get('fingerprint')==key else []
    for row in ranked:
        if row['device'] not in candidates:continue
        try:return load(row['device']),row['device'],{'selection':'cached benchmark','results':saved['results']}
        except Exception:pass
    results=[]
    for device in candidates:
        report('Проверка CPU/GPU · один раз',device)
        results.append(probe(device,root))
    ranked=rank_results(results)
    cache.write_text(json.dumps({'fingerprint':key,'results':results,'time':time.time()},indent=2),encoding='utf-8')
    for row in ranked:
        try:return load(row['device']),row['device'],{'selection':'benchmark','results':results}
        except Exception:pass
    raise RuntimeError('CPU/GPU benchmark failed. See device-benchmark.json; verify model, RAM and drivers.')

def run_probe(device,root):
    import openvino_genai as genai
    started=time.perf_counter()
    pipe=genai.LLMPipeline(str(root/'Qwen3-8B-int4-cw-ov'),device,options(device,root))
    loaded=time.perf_counter()-started
    prompt='Summarize in one simple sentence: A switch connects devices in one local network. A router connects different networks. /no_think'
    # Same input/token budget on each device; a warm-up excludes first compilation.
    times=[]
    for _ in range(2):
        started=time.perf_counter()
        pipe.start_chat('Answer in English. No reasoning. /no_think')
        try:answer=str(pipe.generate(prompt,max_new_tokens=48,do_sample=False))
        finally:pipe.finish_chat()
        if not answer.strip():raise RuntimeError('Empty benchmark output')
        times.append(time.perf_counter()-started)
    return {'ok':True,'device':device,'loadSeconds':round(loaded,3),'coldSeconds':round(times[0],3),'seconds':round(times[1],3),'maxTokens':48}

if __name__=='__main__':
    device=sys.argv[2]
    try:result=run_probe(device,Path(sys.argv[3]))
    except Exception as exc:result={'ok':False,'device':device,'error':str(exc)[:300]}
    print('BENCHMARK_JSON='+json.dumps(result),flush=True)
