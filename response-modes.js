const MODES={fast:{label:'Быстро',tokens:160},balanced:{label:'Обычно',tokens:240},deep:{label:'Вдумчиво',tokens:512}};
function profile(mode,question=false,bilingual=false){
 const id=Object.hasOwn(MODES,mode)?mode:'balanced';
 const thinking=id==='deep'&&question;
 const base=thinking?512:(id==='fast'?160:240);
 return {id,label:MODES[id].label,reasoning:thinking,max_new_tokens:bilingual?Math.min(512,Math.ceil(base*1.7)):base};
}
module.exports={MODES,profile};
