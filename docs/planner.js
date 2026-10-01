(function(root){
  const date = value => new Date(value+'T12:00:00');
  const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  const shift = (value,n) => {const d=date(value);d.setDate(d.getDate()+n);return iso(d);};
  const week = value => {const d=date(value);return Array.from({length:7},(_,i)=>shift(value,i-d.getDay()));};
  const minutes = value => {const [h,m]=value.split(':').map(Number);return h*60+m;};
  function occurrences(state,days){
    const tasks=(state.tasks||[]).filter(t=>days.includes(t.date)).map(t=>({...t,source:'task'}));
    const recurring=(state.routines||[]).flatMap(r=>days.filter(d=> (!r.from||d>=r.from)&&(!r.until||d<=r.until)&&r.days.includes(date(d).getDay())&&!r.exceptions?.[d]?.skip).map(d=>({...r,...r.exceptions?.[d],date:d,source:'routine',done:!!r.exceptions?.[d]?.done})));
    return [...tasks,...recurring];
  }
  function layout(events){
    const sorted=events.filter(e=>e.time).map(e=>({...e,start:minutes(e.time),end:Math.min(1440,minutes(e.time)+(Number(e.duration)||30))})).sort((a,b)=>a.start-b.start||b.end-a.end);
    let group=[],end=-1;
    const flush=()=>{let lanes=[];for(const e of group){let lane=lanes.findIndex(n=>n<=e.start);if(lane<0)lane=lanes.length;e.lane=lane;lanes[lane]=e.end;}group.forEach(e=>e.lanes=lanes.length);group=[];};
    for(const e of sorted){if(e.start>=end){flush();end=-1;}group.push(e);end=Math.max(end,e.end);}flush();return sorted;
  }
  function importData(current,incoming){
    if(incoming.format!=='compasso-import-v1'||!incoming.batch||!incoming.data)throw Error('Arquivo de importação inválido.');
    if(current.imports?.includes(incoming.batch))throw Error('Este arquivo já foi importado nesta conta.');
    const data=incoming.data,next=structuredClone(current);
    if(data.opening!=null){if(next.opening!==0&&next.opening!==data.opening)throw Error('O saldo inicial já possui outro valor. Revise antes de importar.');if(!Number.isSafeInteger(data.opening))throw Error('Saldo inválido.');next.opening=data.opening;}
    for(const key of ['tasks','entries','bills','library','routines','health']){
      if(!data[key])continue;
      if(!Array.isArray(data[key]))throw Error('Dados inválidos: '+key);
      next[key]||=[];
      for(const item of data[key]){
        if(!item.id||typeof item.id!=='string'||!/^[a-z0-9_-]+$/i.test(item.id))throw Error('Identificação de registro inválida.');
        const existing=next[key].find(x=>x.id===item.id);
        if(existing){if(['entries','bills'].includes(key)&&existing.amount!==item.amount)throw Error('Já existe um registro com outro valor. Revise antes de importar.');continue;}
        if(key==='entries'){
          if(!Number.isSafeInteger(item.amount)||item.amount<=0||!['income','expense'].includes(item.kind)||!['pix','cash','credit'].includes(item.method)||!/^\d{4}-\d{2}-\d{2}$/.test(item.date)||!item.category)throw Error('Lançamento inválido.');
          if(next.entries.some(x=>x.date===item.date&&x.amount===item.amount&&x.kind===item.kind&&(x.description===item.description||item.importSalary)))continue;
        }
        if(key==='bills'){
          if(!Number.isSafeInteger(item.amount)||item.amount<=0||!/^\d{4}-\d{2}$/.test(item.month))throw Error('Fatura inválida.');
          const old=next.bills.find(x=>x.card===item.card&&x.month===item.month);
          if(old){if(old.amount===item.amount)continue;throw Error('Já existe uma fatura de '+item.card+' em '+item.month+' com outro valor. Revise antes de importar.');}
        }
        if((key==='routines'||(key==='health'&&item.days))&&(!Array.isArray(item.days)||item.days.some(d=>!Number.isInteger(d)||d<0||d>6)))throw Error('Rotina inválida.');
        if(['tasks','routines','health'].includes(key)){
          if(!item.name||typeof item.name!=='string')throw Error('Título inválido.');
          if(item.time&&!/^([01]\d|2[0-3]):[0-5]\d$/.test(item.time))throw Error('Horário inválido.');
          if(item.duration!=null&&(!Number.isInteger(item.duration)||item.duration<0||item.duration>1440))throw Error('Duração inválida.');
        }
        next[key].push(structuredClone(item));
      }
    }
    if(data.goals)next.goals={...data.goals,...next.goals};
    if(data.preferences)next.preferences={...data.preferences,...next.preferences};
    next.imports=[...(next.imports||[]),incoming.batch];return next;
  }
  const api={iso,shift,week,minutes,occurrences,layout,importData};
  if(typeof module!=='undefined')module.exports=api;else root.Planner=api;
})(globalThis);
