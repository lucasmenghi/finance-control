(function(root){
function snapshot(items,uuid){return items.filter(t=>!t.deleted).map(t=>({id:uuid(),name:t.name,quantity:t.quantity||'',category:t.category,bought:!!t.bought,deleted:false}));}
function receive(current,envelope,uuid){
 if(envelope.owner||envelope.status!=='accepted'||envelope.revision<3)throw Error('A cópia ainda está sendo preparada. Atualize e tente novamente.');
 const next=structuredClone(current);next.shoppingLists||=[];next.shopping||=[];
 const existing=next.shoppingLists.find(l=>l.receivedFrom===envelope.id);
 if(existing){next.shoppingActiveList=existing.id;return next;}
 const list={id:'received-'+envelope.id,name:envelope.name,receivedFrom:envelope.id};
 next.shoppingLists.push(list);next.shoppingActiveList=list.id;
 next.shopping.push(...envelope.items.filter(t=>!t.deleted).map(t=>({id:uuid(),listId:list.id,name:t.name,quantity:t.quantity||'',category:t.category,bought:!!t.bought})));
 return next;
}
const api={snapshot,receive};if(typeof module!=='undefined')module.exports=api;else root.ShoppingCopy=api;
})(globalThis);
