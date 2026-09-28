import io,wave,tkinter as tk,time,statistics
from pathlib import Path
from PIL import Image
from loading_surface import LoadingSurface
from robot_sound import tone

root=tk.Tk();root.overrideredirect(True);root.geometry('280x330+20+20')
with Image.open(Path(__file__).with_name('assets')/'companion.png') as source:surface=LoadingSurface(root,source)
frames=[];surface.paint_frame=frames.append;surface.step=1;surface.label='Загрузка модели на NPU…';surface.paint()
frame=frames[-1];assert frame.getpixel((0,0))[3]==0 and frame.getpixel((279,329))[3]==0
frame.save(Path(__file__).with_name('loading-preview.png'))
surface.paint_frame=lambda frame:None
samples=[]
for _ in range(120):
    before=time.perf_counter();surface.paint();samples.append((time.perf_counter()-before)*1000)
assert len(surface.motion_frames)==49
print('Cached startup render ms: median',round(statistics.median(samples),3),'p95',round(sorted(samples)[113],3))
root.destroy()
for kind in ['startup','answer','drag','reveal']:
    with wave.open(io.BytesIO(tone(kind,.35)),'rb') as wav:
        assert wav.getnchannels()==1 and wav.getsampwidth()==2
        assert wav.getnframes()/wav.getframerate()<.5
with wave.open(io.BytesIO(tone('answer',0)),'rb') as wav:assert not any(wav.readframes(wav.getnframes()))
print('PASS: transparent loading corners, native surface, sub-second tones, zero volume silence; no audio played by test.')
from unittest.mock import patch
import threading,robot_sound
done=threading.Event();played=[]
def fake_sound(data,flags):
    played.append((data,flags))
    if isinstance(data,bytes):done.set()
with patch('robot_sound.winsound.PlaySound',side_effect=fake_sound),patch('robot_sound.settings',side_effect=AssertionError('Explicit volume must not read preferences')):
    robot_sound.play('answer',.33,preview=True)
    assert done.wait(2),'Preview did not play'
    assert played[-1][0]==tone('answer',.33)
done.clear()
def stopped(data,flags):
    assert data is None
    done.set()
with patch('robot_sound.winsound.PlaySound',side_effect=stopped):
    robot_sound.play('answer',0,preview=True)
    assert done.wait(2),'Mute must stop preview without playing a tone'
print('PASS: preview uses selected amplitude, mute stops sound, explicit preview avoids settings I/O; audio mocked.')
