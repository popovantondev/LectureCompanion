const fs=require('fs'),vm=require('vm'),assert=require('assert');
const {LiveSource}=require('./live-source');
const now=Date.now(),source=new LiveSource();
source.accept({time:now-1200000,captionsAvailable:true,captions:[{id:'old',speaker:'Teacher',text:'OLD TOPIC'}]});
source.accept({time:now-60000,captionsAvailable:true,captions:[{id:'prior',speaker:'Teacher',text:'ALREADY SUMMARIZED'}]});
source.commit(source.delta());
source.accept({time:now-10000,captionsAvailable:true,captions:[{id:'fresh',speaker:'Teacher',text:'NEW SPEECH'}]});
const delta=source.delta();
assert(delta.text.includes('NEW SPEECH'));assert(!delta.text.includes('OLD TOPIC'));assert(!delta.text.includes('ALREADY SUMMARIZED'));
assert(delta.context.includes('OLD TOPIC'));source.commit(delta);assert.equal(source.delta().text,'');
let handler;
class FakeLive extends LiveSource{start(){}stop(){}}
const sandbox={require:name=>({
'./live-source':{LiveSource:FakeLive},'./npu-client':{generate:async()=>({ok:true,json:async()=>({response:'TEST ANSWER'})})},
'./vision':{queue:s=>s,status:()=>({})},
'fs':{readFileSync:()=>'{}',writeFileSync:()=>{},mkdirSync:()=>{}},
'child_process':{spawn:()=>({on:()=>{}})},
'http':{createServer:fn=>(handler=fn,{listen:()=>{}})}
}[name]||require(name)),__dirname,console:{log:()=>{}},process:{env:{},on:()=>{}},setInterval:()=>{},setTimeout,Date,URL};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(__dirname+'/server.js','utf8')+'\nthis.test={setBusy:v=>localBusy=v,isPending:()=>pendingQuestion};',sandbox);
const t=sandbox.test;t.setBusy(true);const events={};let result='';
handler({method:'POST',url:'/api/ask',headers:{origin:'http://127.0.0.1:8765'},on:(k,fn)=>events[k]=fn},{setHeader:()=>{},writeHead:code=>assert.equal(code,200),end:text=>result=text});
events.data(Buffer.from(JSON.stringify({question:'Test question'})));const done=events.end();assert(t.isPending());
setTimeout(()=>t.setBusy(false),10);
done.then(()=>{assert.equal(JSON.parse(result).question,'Test question');assert(!t.isPending());console.log('PASS: 20-minute-old context is not fresh speech, committed text excluded, manual question priority.');});
