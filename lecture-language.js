// Conservative, local language recognition. Short technical fragments abstain.
// Only caption data is used, never the user question or the selected UI language.
const {valid}=require("./i18n");
const words={
  de:new Set("der die das den dem des ein eine einen einem und oder aber nicht mit für von auf wir ihr werden wird ist sind dass dieser diese wurde verbindet netzwerk netzwerke aufgabe bildschirm heute jetzt".split(" ")),
  en:new Set("the a an and or but not with for from we you is are this that these will was were connects network networks today now have has should".split(" "))
};
function detect(text=""){
  const clean=String(text).replace(/^(?:\[[^\]]*\]\s*)?[^:\n]{1,90}:\s*/gm,"");
  const letters=clean.match(/\p{L}/gu)||[],cyrillic=clean.match(/[а-яё]/giu)||[];
  if(cyrillic.length>=8&&cyrillic.length/Math.max(1,letters.length)>.35)return "ru";
  const tokens=new Set((clean.toLowerCase().match(/[a-zäöüß]+/g)||[]));
  const score=language=>[...tokens].filter(word=>words[language].has(word)).length;
  const de=score("de"),en=score("en");
  if(de>=2&&de>en)return "de";
  if(en>=2&&en>de)return "en";
  return null;
}
function resolve(delta={},previous=null){
  return detect(delta.text)||detect(delta.context)||(valid(previous)?previous:null);
}
function pair(ui,lecture){
  ui=valid(ui)?ui:"de";
  return valid(lecture)&&lecture!==ui?[lecture,ui]:[ui];
}
module.exports={detect,resolve,pair,key:(ui,lecture)=>pair(ui,lecture).join(":")};
