(function(root){
const P=typeof module!=='undefined'?require('./planner.js'):root.Planner;
function ensure(state,today){
 state.shopping||=[];state.shoppingLists||=[];
 if(!state.shoppingLists.length)state.shoppingLists.push({id:'default-list',name:'Minha lista'});
 for(const item of state.shopping)if(!state.shoppingLists.some(l=>l.id===item.listId))item.listId=state.shoppingLists[0].id;
 if(!state.shoppingLists.some(l=>l.id===state.shoppingActiveList))state.shoppingActiveList=state.shoppingLists[0].id;
 state.health||=[];state.healthWeek||=[];state.healthWeekSources||=[];state.healthWeekStart||=today;
 for(const r of state.health){
  if(!r.days||state.healthWeekSources.includes(r.id))continue;
  if(!r.until||r.until>=today)for(const weekday of r.days){const id=r.id+'-day-'+weekday;if(!state.healthWeek.some(t=>t.id===id))state.healthWeek.push({id,name:r.name,kind:r.kind,time:r.time||'',duration:r.duration||0,notes:r.notes||'',weekday,from:r.from||today,until:r.until,exceptions:structuredClone(r.exceptions||{})});}
  state.healthWeekSources.push(r.id);
 }
 return state;
}
function healthEvents(state,days){const start=state.healthWeekStart;const dated=P.occurrences({tasks:(state.health||[]).filter(t=>!t.days),routines:(state.health||[]).filter(t=>t.days)},days).filter(t=>!start||t.date<start||(!t.days&&!state.healthWeekSources?.includes(t.id)));const fixed=P.occurrences({tasks:[],routines:(state.healthWeek||[]).map(t=>({...t,days:[t.weekday],from:t.from&&t.from>start?t.from:start}))},days);return [...dated,...fixed];}
function listItems(state){return state.shopping.filter(t=>t.listId===state.shoppingActiveList);}
function listName(state,name,exceptId){name=String(name||'').trim();if(!name||name.length>80)throw Error('Informe um nome com até 80 caracteres.');if(state.shoppingLists.some(l=>l.id!==exceptId&&l.name.toLocaleLowerCase('pt-BR')===name.toLocaleLowerCase('pt-BR')))throw Error('Já existe uma lista com esse nome.');return name;}
function clipped(events,start,end){return P.layout(events.filter(t=>t.time&&P.minutes(t.time)<end*60&&P.minutes(t.time)+(Number(t.duration)||30)>start*60)).map(t=>({...t,visibleStart:Math.max(t.start,start*60),visibleEnd:Math.min(t.end,end*60)}));}
const api={ensure,healthEvents,listItems,listName,clipped};if(typeof module!=='undefined')module.exports=api;else root.Workspace=api;
})(globalThis);
