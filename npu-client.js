const {tr}=require('./i18n');
async function generate(payload,onPhase=()=>{}){
 const deadline=Date.now()+170000;
 while(true){
  onPhase((process.env.LECTURE_TEXT_DEVICE||'NPU')+' · '+tr('NPU · обработка текста',payload.language).split(' · ').at(-1));
  const response=await fetch('http://127.0.0.1:8766/generate',{method:'POST',headers:{'Content-Type':'application/json',Origin:'http://127.0.0.1:8765'},signal:AbortSignal.timeout(Math.max(1000,deadline-Date.now())),body:JSON.stringify(payload)});
  if(response.status!==409)return response;
  await response.text();
  onPhase('Очередь · NPU занят');
  if(Date.now()+1500>=deadline){const error=new Error(tr('NPU занят, попробуем позже',payload.language));error.transient=true;throw error;}
  await new Promise(resolve=>setTimeout(resolve,1500));
 }
}
module.exports={generate};
