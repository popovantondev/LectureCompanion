// Exercise the release routes without starting Teams, models, or a real listener.
// Optional argument: the frozen app resource directory, for packaging regression.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const {createRequire}=require("node:module");
const root=path.resolve(process.argv[2]||__dirname);
const serverFile=path.join(root,"server.js"),runtimeRequire=createRequire(serverFile);
const reads=[];let handler;
class NoCapture {start(){}stop(){}}
const dependencies={
  http:{createServer(fn){handler=fn;return {listen(){},close(){}}}},
  fs:{mkdirSync(){},readFileSync(file){
    reads.push(path.basename(file));
    throw Object.assign(new Error("File deliberately absent in route test"),{code:"ENOENT"});
  },writeFileSync(){throw new Error("Read-only route attempted a write");}},
  "./live-source":{LiveSource:NoCapture}
};
const sandbox={require:name=>Object.hasOwn(dependencies,name)?dependencies[name]:runtimeRequire(name),
  __dirname:root,process:{env:{},on(){}},console:{log(){}},setInterval(){},setTimeout(){},Date,URL};
vm.runInNewContext(fs.readFileSync(serverFile,"utf8"),sandbox,{filename:serverFile});
function call(url,method="GET"){
  const result={status:200,headers:{},body:null};
  handler({url,method,headers:{}},{setHeader(k,v){result.headers[k]=v;},
    writeHead(status){result.status=status;},end(body=""){result.body=body;}});
  return result;
}
const health=call("/health");assert.equal(health.status,200);
assert.equal(JSON.parse(health.body).version,"2.4");
for(let i=0;i<3;i++){
  const home=call("/");assert.equal(home.status,200);
  assert.equal(home.headers["Content-Type"],"application/json; charset=utf-8");
  assert.deepEqual(JSON.parse(home.body),JSON.parse(health.body));
  assert.equal(call("/health").status,200,"Health must work after the root request");
}
assert.equal(call("/favicon.ico").status,404);
assert.equal(call("/does-not-exist").status,404);
assert.equal(call("/","POST").status,404);
assert.ok(!reads.includes("index.html"),"Native release must not depend on legacy web assets");
console.log("PASS: root/health stay alive without index.html; repeated requests and 404 routes; no capture or writes.");
