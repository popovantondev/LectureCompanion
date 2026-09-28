const fs=require('fs'),vm=require('vm'),assert=require('assert');
let finish,calls=0;
const sandbox={require:n=>n==='fs'?{statSync:()=>({size:1}),readFileSync:()=>Buffer.from('image')}:require(n),module:{exports:{}},AbortSignal,Date,Map,
fetch:async url=>{calls++;if(url.endsWith('/api/tags'))return {ok:true,json:async()=>({models:[{name:'qwen3-vl:2b-instruct'}]})};return new Promise(resolve=>finish=()=>resolve({ok:true,json:async()=>({response:'diagram',total_duration:1e9})}));}};
vm.runInNewContext(fs.readFileSync(__dirname+'/vision.js','utf8'),sandbox);
const {queue}=sandbox.module.exports;
const s={key:'test',file:'test.jpg'};
let completed;
const immediate=queue(s,r=>completed=r);
assert.equal(immediate.visionStatus,require('./i18n').tr('Картинка разбирается в фоне; вопросы доступны','de'));
queue(s,()=>{throw new Error('Duplicate request');});
setImmediate(()=>{assert.equal(calls,2);finish();setImmediate(()=>{assert.equal(completed.vision,'diagram');assert.equal(queue(s,()=>{}).vision,'diagram');console.log('PASS: nonblocking, one inference, cached result.');});});
