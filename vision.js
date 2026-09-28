const fs=require('fs');
const {tr}=require('./i18n');
const prompts=require('./answer-prompts');
const {key:languageKey,pair}=require('./lecture-language');
const matches=(screen,ui,lecture)=>screen.visionLanguage===ui&&languageKey(ui,screen.visionLectureLanguage)===languageKey(ui,lecture);
const MODEL='qwen3-vl:2b-instruct';
let nextCheck=0,available=false;
const ENDPOINT='http://127.0.0.1:11435';
let active=false;
let pending=null,lastFinished=0;
let visionStarted=0;
const completed=new Map();
function queue(screen,onComplete,manual=false,language='de',lectureLanguage=null){
  const t=text=>tr(text,language);
  if(!screen)return screen;
  const cacheKey=screen.key+':'+languageKey(language,lectureLanguage);
  if(completed.has(cacheKey))return {...completed.get(cacheKey),captured:screen.captured};
  if(!matches(screen,language,lectureLanguage))screen={...screen,vision:null,visionAttempted:null};
  if(screen.vision&&screen.visionEngine===MODEL&&matches(screen,language,lectureLanguage))return screen;
  if(screen.visionEngine===MODEL&&screen.visionAttempted===screen.key)return screen;
  if(active)return {...screen,visionStatus:t('Зрение занято; ответ пока по речи и OCR')};
  if(!manual&&Date.now()-lastFinished<180000)return {...screen,visionStatus:t('Зрение отдыхает: фоновый разбор раз в 3 минуты')};
  active=true;
  visionStarted=Date.now();
  const copy={...screen,vision:null,visionAttempted:null,visionEngine:MODEL,visionLanguage:language,visionLectureLanguage:lectureLanguage};
  pending=enrich(copy).then(result=>{
    if(result.visionAttempted){completed.set(cacheKey,result);if(completed.size>4)completed.delete(completed.keys().next().value);}
    onComplete(result);
    return result;
  }).finally(()=>{active=false;lastFinished=Date.now();});
  return {...screen,visionStatus:t('Картинка разбирается в фоне; вопросы доступны')};
}
async function inspect(screen,onPhase=()=>{},language='de',lectureLanguage=null){
 if(!screen)return null;
 if(screen.vision&&screen.visionEngine===MODEL&&matches(screen,language,lectureLanguage))return screen;
 const cacheKey=screen.key+':'+languageKey(language,lectureLanguage);
 if(completed.has(cacheKey))return {...completed.get(cacheKey),captured:screen.captured};
 if(pending&&active){onPhase('Очередь · GPU занят');const result=await pending;if(result?.key===screen.key&&matches(result,language,lectureLanguage))return {...result,captured:screen.captured};}
 onPhase('GPU · разбор презентации');
 queue(screen,()=>{},true,language,lectureLanguage);
 return pending?await pending:screen;
}
async function enrich(screen){
  const t=text=>tr(text,screen?.visionLanguage||'ru');
  if(!screen||screen.vision||screen.visionAttempted===screen.key)return screen;
  try{
    if(Date.now()>nextCheck){
      nextCheck=Date.now()+60000;
      const r=await fetch(ENDPOINT+'/api/tags',{signal:AbortSignal.timeout(5000)});
      if(!r.ok)throw new Error('Ollama недоступна');
      available=(await r.json()).models.some(m=>m.name===MODEL);
    }
    if(!available)return {...screen,visionStatus:t('Модель зрения ещё скачивается')};
    screen.visionAttempted=screen.key;
    if(!screen.imageBase64&&!/\.(png|jpe?g)$/i.test(screen.file))throw new Error('Формат картинки не поддерживается');
    if(screen.imageBase64?screen.imageBase64.length>14000000:fs.statSync(screen.file).size>10*1024*1024)throw new Error('Картинка больше 10 МБ');
    const r=await fetch(ENDPOINT+'/api/generate',{
      method:'POST',headers:{'Content-Type':'application/json'},signal:AbortSignal.timeout(110000),
      body:JSON.stringify({model:MODEL,stream:false,think:false,keep_alive:0,
        options:{num_ctx:4096,num_predict:pair(screen.visionLanguage,screen.visionLectureLanguage).length===2?320:180,num_thread:4,temperature:0.1},
        system:prompts.vision(screen.visionLanguage||'de',screen.visionLectureLanguage),
        prompt:'Describe the main educational slide. Explain its diagram if one is visible.',
        images:[screen.imageBase64||fs.readFileSync(screen.file).toString('base64')]})});
    if(!r.ok)throw new Error('Зрение HTTP '+r.status);
    const result=await r.json();
    const description=(result.response||'').replace(/<think>[\s\S]*?<\/think>/g,'').trim();
    if(!description)throw new Error('Пустое описание');
    return {...screen,vision:description.slice(0,2200),visionStatus:t('Локальное зрение: ')+MODEL,visionSeconds:Math.round((result.total_duration||0)/1e9)};
  }catch(e){return {...screen,visionStatus:t('Только OCR: ')+e.message};}
}
module.exports={enrich,queue,inspect,waitIdle:async()=>{if(active&&pending)await pending;},status:()=>({active,elapsed:active?Math.floor((Date.now()-visionStarted)/1000):0,cooldown:Math.max(0,Math.ceil((lastFinished+180000-Date.now())/1000))})};
