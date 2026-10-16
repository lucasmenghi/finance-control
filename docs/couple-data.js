(function(root){
function amount(raw,allowZero=false){raw=String(raw).trim();if(!/^\d+(?:[,.]\d{1,2})?$/.test(raw))throw Error('Use um valor como 150,00.');const n=Math.round(Number(raw.replace(',','.'))*100);if(!Number.isSafeInteger(n)||(allowZero?n<0:n<=0))throw Error('Informe um valor válido.');return n;}
function summary(data){const income=data.entries.filter(t=>!t.deleted&&t.kind==='income').reduce((n,t)=>n+t.amount,0),expense=data.entries.filter(t=>!t.deleted&&t.kind==='expense').reduce((n,t)=>n+t.amount,0);return {cash:data.opening+income-expense,income,expense};}
function payload(data){return {opening:data.opening,entries:data.entries.map(t=>({id:t.id,description:t.description,amount:t.amount,kind:t.kind,date:t.date,category:t.category||'Outros',deleted:!!t.deleted})),goals:data.goals.map(t=>({id:t.id,name:t.name,amount:t.amount,date:t.date||'',archived:!!t.archived}))};}
const api={amount,summary,payload};if(typeof module!=='undefined')module.exports=api;else root.CoupleFinance=api;
})(globalThis);
