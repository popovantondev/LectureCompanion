const {spawn}=require('child_process'),path=require('path'),crypto=require('crypto');
class LiveSource{
 constructor(){this.rows=new Map();this.status='Подключение к Teams';this.last=0;this.screen=null;this.initial=true;}
 start(){
  this.child=spawn('C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',['-NoProfile','-File',path.join(__dirname,'teams-live.ps1')],{windowsHide:true});
  let buffer='';this.child.stdout.on('data',b=>{buffer+=b.toString('utf8');let pos;while((pos=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,pos);buffer=buffer.slice(pos+1);try{this.accept(JSON.parse(line));}catch{}}if(buffer.length>20000000)buffer='';});
  this.child.stderr.on('data',()=>{});this.child.on('error',e=>this.status=e.message);this.child.on('exit',()=>this.status='Канал Teams остановлен');
 }
 async captureFresh(){
  return new Promise((resolve,reject)=>{
   const child=spawn('C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',['-NoProfile','-File',path.join(__dirname,'teams-live.ps1'),'-Once'],{windowsHide:true});
   let out='',err='';const timer=setTimeout(()=>{child.kill();reject(new Error('Свежий захват Teams не завершился'));},25000);
   child.stdout.on('data',b=>out+=b.toString('utf8'));child.stderr.on('data',b=>err+=b.toString('utf8'));
   child.on('error',e=>{clearTimeout(timer);reject(e)});
   child.on('close',code=>{clearTimeout(timer);try{if(code!==0)throw new Error(err.slice(-200));const data=JSON.parse(out.trim());if(data.error||data.screenError)throw new Error(data.error||data.screenError);if(!data.imageBase64)throw new Error('Презентация недоступна');resolve({key:crypto.createHash('sha256').update(data.imageBase64).digest('hex'),name:'Презентация Teams — '+new Date(data.imageTime).toLocaleTimeString('ru-RU'),captured:data.imageTime,imageBase64:data.imageBase64,text:'',scope:'teams-presentation'});}catch(e){reject(e)}});
  });
 }
 accept(data){
  if(data.error){this.status=data.error;this.initial=true;return}
  this.last=data.time;this.status=data.captionsAvailable?'Teams напрямую':'Включите живые субтитры Teams';
  for(const row of data.captions||[]){
   const old=this.rows.get(row.id);
   if(!old)this.rows.set(row.id,{...row,at:data.time,consumed:this.initial?row.text.length:0});
   else if(old.text!==row.text){
    const prefix=old.text.slice(0,old.consumed);old.consumed=row.text.startsWith(prefix)?old.consumed:row.text.length;old.text=row.text;old.at=data.time;
   }
  }
  this.initial=false;
  while(this.rows.size>600)this.rows.delete(this.rows.keys().next().value);
  if(data.imageBase64){
   const key=crypto.createHash('sha256').update(data.imageBase64).digest('hex');
   this.screen={...(this.screen?.key===key?this.screen:{}),key,name:'Teams — '+new Date(data.imageTime).toLocaleTimeString('ru-RU'),captured:data.imageTime,imageBase64:data.imageBase64,text:(data.screenText||'').slice(0,3500),scope:data.scope||'teams-window'};
  }
  if(data.screenError){this.status+='; '+data.screenError;this.screen=null;}
 }
 delta(){
  const now=Date.now(),fresh=[...this.rows.values()].filter(r=>r.consumed<r.text.length&&now-r.at<180000);
  const selected=fresh.slice(-30),stamp=t=>new Date(t).toLocaleTimeString('ru-RU');
  return {text:selected.map(r=>'['+stamp(r.at)+'] '+r.speaker+': '+r.text.slice(r.consumed)).join('\n').slice(-6500),context:[...this.rows.values()].filter(r=>!selected.includes(r)).map(r=>r.speaker+': '+r.text).join('\n').slice(-3000),from:selected.length?stamp(selected[0].at):null,to:selected.length?stamp(selected.at(-1).at):null,liveMarks:selected.map(r=>[r.id,r.text.length])};
 }
 commit(delta){for(const [id,length] of delta.liveMarks||[]){const row=this.rows.get(id);if(row)row.consumed=Math.max(row.consumed,length);}}
 stop(){this.child?.kill();}
}
module.exports={LiveSource};
