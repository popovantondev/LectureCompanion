const assert=require('assert'),fs=require('fs'),vm=require('vm');
const catalog=require('./locales.json'),prompts=require('./answer-prompts');
for(const row of Object.values(catalog))for(const language of ['de','en','ru'])assert(row[language]?.trim());
let handler,writes={},lastPayload,speech='NEW speech '.repeat(30);
class Live{start(){}stop(){}delta(){return {context:'OLD',text:speech}}commit(){}}
const sandbox={require:n=>({
  './live-source':{LiveSource:Live},
  './npu-client':{generate:async payload=>{lastPayload=payload;return {ok:true,json:async()=>({response:payload.language+': answer'})}}},
  './vision':{queue:s=>s,inspect:async(s,p,language)=>({...s,vision:language+': slide'}),waitIdle:async()=>{},status:()=>({})},
  fs:{mkdirSync:()=>{},readFileSync:()=>JSON.stringify({entries:Array.from({length:50},(_,id)=>({id,text:'old'}))}),existsSync:()=>false,copyFileSync:(a,b)=>writes.backup=b,writeFileSync:(p,v)=>writes[p]=v},
  child_process:{spawn:()=>({on:()=>{}})},http:{createServer:fn=>(handler=fn,{listen:()=>{}})}
}[n]||require(n)),__dirname,process:{env:{},on:()=>{}},console:{log:()=>{}},setInterval:()=>{},setTimeout,Date,URL};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(__dirname+'/server.js','utf8')+'\nthis.test={busy:v=>localBusy=v,entries:()=>state.entries};',sandbox);
async function call(url,body,origin='http://127.0.0.1:8765'){
 const events={};let status=200,result;
 handler({url,method:'POST',headers:{origin},on:(k,v)=>events[k]=v},{setHeader(){},writeHead:n=>status=n,end:t=>result=t});
 if(events.data)events.data(Buffer.from(JSON.stringify(body)));
 if(events.end)await events.end();
 return {status,result};
}
(async()=>{
 assert(writes.backup.endsWith('history-before-10.json'));assert.equal(sandbox.test.entries().length,10);
 for(const language of ['de','en','ru']){
  assert.equal((await call('/api/language',{language})).status,200);
  const answer=JSON.parse((await call('/api/ask',{question:'Explain a switch'})).result);
  assert.equal(answer.language,language);assert.equal(answer.text,language+': answer');
  assert.equal(lastPayload.system,prompts.system(language,true));assert.equal(sandbox.test.entries().length,10);
 }
 assert.equal((await call('/api/language',{language:'xx'})).status,400);
 assert.equal((await call('/api/language',{language:'en'},'https://example.com')).status,403);
 await call('/api/language',{language:'de'});sandbox.test.busy(true);
 const pending=call('/api/ask',{question:'Explain IP'});
 await call('/api/language',{language:'en'});sandbox.test.busy(false);
 assert.equal(JSON.parse((await pending).result).language,'de','Pending request must keep its original language');
 speech='Der Router verbindet die Netzwerke und das ist die Aufgabe.';
 await call('/api/language',{language:'ru'});sandbox.test.busy(true);
 const bilingualPending=call('/api/ask',{question:'Explain IP'});
 speech='The router connects the networks and this is the task.';
 await call('/api/language',{language:'en'});sandbox.test.busy(false);
 const bilingual=JSON.parse((await bilingualPending).result);
 assert.equal(bilingual.language,'ru');assert.equal(bilingual.lectureLanguage,'de');
 assert.equal(lastPayload.system,prompts.system('ru',true,'de'));
 assert.equal(lastPayload.max_new_tokens,408);
 console.log('PASS: three prompt languages, 10-answer migration/backup, history cap, locale validation/origin and in-flight language.');
})().catch(e=>{console.error(e);process.exitCode=1});
