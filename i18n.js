const catalog=require('./locales.json');
const languages=['de','en','ru'];
const valid=value=>languages.includes(value);
function tr(text,language='de'){
  if(catalog[text])return catalog[text][language]||text;
  const key=Object.keys(catalog).sort((a,b)=>b.length-a.length).find(k=>k.length>8&&text.startsWith(k));
  return key?(catalog[key][language]||key)+text.slice(key.length):text;
}
module.exports={tr,valid,languages};
