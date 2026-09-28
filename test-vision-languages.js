const assert=require('assert'),vm=require('vm'),fs=require('fs');
let calls=[];
const box={module:{exports:{}},require,AbortSignal,Date,Map,fetch:async(url,options)=>{
 if(url.endsWith('/api/tags'))return {ok:true,json:async()=>({models:[{name:'qwen3-vl:2b-instruct'}]})};
 const data=JSON.parse(options.body);calls.push(data);return {ok:true,json:async()=>({response:data.system.includes('German')?'Deutsch':'English'})};
}};
vm.runInNewContext(fs.readFileSync(__dirname+'/vision.js','utf8'),box);
(async()=>{
 const api=box.module.exports,s={key:'same',imageBase64:'AA==',captured:1};
 const de=await api.inspect(s,()=>{},'de');assert.equal(de.vision,'Deutsch');
 const en=await api.inspect(de,()=>{},'en');assert.equal(en.vision,'English');assert.equal(calls.length,2);
 const cached=await api.inspect({...s,captured:2},()=>{},'de');assert.equal(cached.vision,'Deutsch');assert.equal(cached.captured,2);assert.equal(calls.length,2);
 const bilingual=await api.inspect(s,()=>{},'ru','de');
 assert.equal(calls.length,3);assert.ok(calls.at(-1).system.includes('German, then Russian'));
 assert.equal(bilingual.visionLectureLanguage,'de');assert.equal(calls.at(-1).options.num_predict,320);
 await api.inspect(s,()=>{},'ru','en');assert.equal(calls.length,4);
 assert.ok(calls.at(-1).system.includes('English, then Russian'));
 await api.inspect({...s,captured:3},()=>{},'ru','de');assert.equal(calls.length,4);
 await api.inspect(s,()=>{},'de','de');assert.equal(calls.length,4,'Same-language result is not duplicated');
 console.log('PASS: slide descriptions and cache are language-specific; refreshed capture time preserved.');
})().catch(e=>{console.error(e);process.exitCode=1});
