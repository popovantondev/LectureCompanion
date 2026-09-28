"""Explicit local integration tests with synthetic data, never a real lecture.

Requires Pillow only to draw the test slide. Start the portable app --paused.
"""
import base64,io,json,time,urllib.request,sys,argparse,subprocess,re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image,ImageDraw,ImageFont

def request(port,route,body=None):
    payload=None if body is None else json.dumps(body,ensure_ascii=False).encode()
    req=urllib.request.Request(f"http://127.0.0.1:{port}"+route,data=payload,
        headers={"Origin":"http://127.0.0.1:8765","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as response:return json.load(response)

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--bilingual",action="store_true");parser.add_argument("--node")
    args=parser.parse_args();prompts={}
    if args.bilingual:
        if not args.node:parser.error("--bilingual requires --node")
        code='const p=require("./answer-prompts");console.log(JSON.stringify({text:p.system("ru",true,"de"),vision:p.vision("ru","de")}))'
        prompts=json.loads(subprocess.check_output([args.node,"-e",code],cwd=Path(__file__).parent,encoding="utf-8"))
    state=request(8765,"/api/ui-state?after=test")
    assert not state["localEnabled"] and not state["localBusy"],"Pause summaries first"
    results=[]
    cases=[("ru","Russian","сет")] if args.bilingual else [("de","German","Netz"),("en","English","network"),("ru","Russian","сет")]
    for language,label,term in cases:
        result=request(8766,"/generate",{"language":language,"reasoning":False,"max_new_tokens":408 if args.bilingual else 160,
            "system":prompts.get("text",f"Write only in {label}. Explain briefly in simple words, without timestamps or names."),
            "prompt":"Summarize in one or two sentences: A switch connects computers in one local network. A router connects different networks. No new homework was assigned."})
        answer=result["response"]
        assert term.lower() in answer.lower(),(language,answer)
        assert "<think>" not in answer
        if args.bilingual:
            assert "Deutsch" in answer and "Русский" in answer and "Netz" in answer,answer
            assert answer.index("Deutsch")<answer.index("Русский"),answer
        row={"kind":"text","language":language,"device":result["device"],"seconds":result["seconds"],"answer":answer}
        results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    slide=Image.new("RGB",(960,540),"white");draw=ImageDraw.Draw(slide)
    font=ImageFont.truetype("arial.ttf",38);title=ImageFont.truetype("arial.ttf",54)
    draw.text((60,50),"LAN und WAN",font=title,fill="#142a40")
    draw.text((60,180),"LAN: ein lokales Netzwerk",font=font,fill="black")
    draw.text((60,280),"WAN: verbindet entfernte Netzwerke",font=font,fill="black")
    draw.text((60,420),"Kein neues Arbeitsblatt.",font=font,fill="black")
    buffer=io.BytesIO();slide.save(buffer,format="PNG")
    result=request(11435,"/api/generate",{"model":"qwen3-vl:2b-instruct","stream":False,"think":False,"keep_alive":0,
        "options":{"num_ctx":4096,"num_predict":320 if args.bilingual else 180,"num_thread":4,"temperature":0.1},
        "system":prompts.get("vision","Beschreibe nur den sichtbaren Lerninhalt auf Deutsch. Kurz, in einfachen Worten. Nichts erfinden."),
        "prompt":"Was steht auf dieser Folie?", "images":[base64.b64encode(buffer.getvalue()).decode()]})
    answer=result["response"];assert "LAN" in answer and "WAN" in answer,answer
    if args.bilingual:
        assert "Deutsch" in answer and "Русский" in answer,answer
        assert answer.index("Deutsch")<answer.index("Русский"),answer
        assert len(re.findall("[а-яё]",answer.split("Русский")[-1].lower()))>=10,answer
    row={"kind":"vision","language":"de+ru" if args.bilingual else "de","seconds":round(result.get("total_duration",0)/1e9,2),"answer":answer}
    results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    print("PASS: synthetic text and slide, "+("lecture+interface languages" if args.bilingual else "DE/EN/RU text")+"; all requests loopback-only.",flush=True)

if __name__=="__main__":main()
