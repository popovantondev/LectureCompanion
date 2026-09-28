"""Short, softly enveloped local robot tones. No samples, download or audio service."""
import array,io,json,math,os,random,threading,wave,winsound
from pathlib import Path

LOCK=threading.Lock()
PREVIEW_LOCK=threading.Lock()
PREVIEW_ID=0
def settings_path():return Path(os.environ.get('LECTURE_DATA_DIR',str(Path.home()/'LectureCompanion')))/'ui-settings.json'
def settings():
    try:
        data=json.loads(settings_path().read_text(encoding='utf-8'))
        return {**data,'sound':bool(data.get('sound',True)),'volume':max(0,min(100,int(data.get('volume',35)))),'language':data.get('language','ru')}
    except (OSError,ValueError,TypeError):return {'sound':True,'volume':35,'language':'de'}
def save_settings(sound,volume,language=None):
    file=settings_path();file.parent.mkdir(parents=True,exist_ok=True)
    data=settings();data.update(sound=bool(sound),volume=max(0,min(100,int(volume))))
    if language in ('de','en','ru'):data['language']=language
    file.write_text(json.dumps(data),encoding='utf-8')
def tone(kind,volume):
    rate=24000;notes=[(620,830,.12),(980,1150,.16)] if kind=='startup' else [(980,1260,.14),(820,930,.10)]
    samples=array.array('h');phase=0
    if kind in ('drag','reveal'):
        # Seeded soft noise + a quiet chirp: no external samples and no harsh click.
        notes=[(330,650,.22)] if kind=='drag' else [(550,1050,.28)]
    noise=random.Random(42);filtered=0
    for low,high,duration in notes:
        count=int(rate*duration)
        for i in range(count):
            t=i/rate;phase+=2*math.pi*(low+(high-low)*i/count)/rate
            envelope=min(1,t/.018)*min(1,(duration-t)/.065)
            value=math.sin(phase)+.12*math.sin(phase*2)
            if kind in ('drag','reveal'):
                filtered=.84*filtered+.16*noise.uniform(-1,1)
                value=(.24*math.sin(phase)+1.3*filtered)*math.sin(math.pi*i/count)
            samples.append(int(5200*max(0,min(1,volume))*envelope*value))
        samples.extend([0]*int(rate*.035))
    buffer=io.BytesIO()
    with wave.open(buffer,'wb') as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(samples.tobytes())
    return buffer.getvalue()
def play(kind='answer',volume=None,preview=False):
    global PREVIEW_ID
    if volume is None:
        preferences=settings()
        if not preferences['sound']:return
        volume=preferences['volume']/100
    if volume<=0 and not preview:return
    request_id=None
    if preview:
        with PREVIEW_LOCK:PREVIEW_ID+=1;request_id=PREVIEW_ID
    def worker():
        if preview:
            # A new volume preview replaces the previous tone instead of being
            # silently dropped, queued at an old volume, or blocking the UI.
            with PREVIEW_LOCK:
                if request_id!=PREVIEW_ID:return
                try:winsound.PlaySound(None,0)
                except RuntimeError:pass
            if volume<=0:return
        acquired=LOCK.acquire(timeout=.5) if preview else LOCK.acquire(blocking=False)
        if not acquired:return
        try:
            if preview:
                with PREVIEW_LOCK:
                    if request_id!=PREVIEW_ID:return
            winsound.PlaySound(tone(kind,volume),winsound.SND_MEMORY|winsound.SND_NODEFAULT)
        except RuntimeError:pass
        finally:LOCK.release()
    threading.Thread(target=worker,daemon=True).start()
