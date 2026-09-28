let task=null,last=null;
function begin(label){task={label,started:Date.now(),phase:'Подготовка',phaseStarted:Date.now(),timings:{}};}
function phase(name){if(!task)return;if(task.phase===name)return;const now=Date.now();task.timings[task.phase]=(task.timings[task.phase]||0)+(now-task.phaseStarted);task.phase=name;task.phaseStarted=now;}
function finish(error=''){if(!task)return;const now=Date.now();task.timings[task.phase]=(task.timings[task.phase]||0)+(now-task.phaseStarted);last={...task,seconds:Math.round((now-task.started)/1000),error};task=null;}
function snapshot(){return {task:task?{...task,elapsed:Math.floor((Date.now()-task.started)/1000),phaseElapsed:Math.floor((Date.now()-task.phaseStarted)/1000)}:null,last};}
module.exports={begin,phase,finish,snapshot};
