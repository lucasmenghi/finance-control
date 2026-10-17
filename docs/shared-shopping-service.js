// The existing protected table is a delivery envelope, never a live personal list.
window.SharedShopping=(()=>{
 let generation=0,busy=false,snapshot={status:'idle',lists:[],invites:[],message:''};
 const draw=()=>{if(CompassoAccount.isActive()&&view==='shopping'&&shoppingScope==='shared')render();};
 function reset(){generation++;busy=false;snapshot={status:'idle',lists:[],invites:[],message:''};}
 function message(error){const m=error?.message||'';if(m.includes('verified_email_required'))return 'Confirme seu e-mail para receber a lista.';if(m.includes('invalid_email'))return 'Confira o e-mail do outro usuário.';if(m.includes('not_allowed'))return 'Você não tem acesso a esse envio.';if(error?.code==='PGRST202'||m.includes('Could not find the function'))return 'O envio de listas precisa ser ativado no Supabase.';return 'Não foi possível concluir o envio. Atualize para verificar o resultado.';}
 function ready(list){return list.status==='pending'?list.revision>=2:list.status==='accepted'&&list.revision>=3;}
 async function read(){return CompassoAccount.shoppingRequest('compasso_shopping_get',{});}
 function assign(data){snapshot={status:'ready',lists:data.lists,invites:data.invites,message:''};}
 async function load(){if(!CompassoAccount.isPrivate()||busy)return;const token=++generation;snapshot.status='loading';draw();try{const data=await read();if(token!==generation)return;assign(data);}catch(e){if(token!==generation)return;snapshot.status='error';snapshot.message=message(e);}draw();}
 async function send(name,email,items,resumeId=null){items=items.filter(t=>!t.deleted).map(t=>({id:t.id,name:t.name,quantity:t.quantity||'',category:t.category,bought:!!t.bought,deleted:false}));if(busy)throw Error('Aguarde o envio atual.');const token=generation;busy=true;draw();try{
  let id=resumeId,revision=1;
  if(id){const data=await read(),draft=data.lists.find(l=>l.id===id&&l.owner);if(!draft||ready(draft))throw Error('Este envio já foi finalizado.');revision=draft.revision;}
  else id=await CompassoAccount.shoppingRequest('compasso_shopping_create',{list_name:name,recipient_email:email,initial_items:[]});
  if(token!==generation)return false;
  try{await CompassoAccount.shoppingRequest('compasso_shopping_save',{list_id:id,list_name:name,list_items:items,expected_revision:revision});}
  catch(error){
   if(token!==generation)return false;
   // An acceptance can arrive between creation and the first save. It changes
   // revision but cannot edit either user's private copy. Finish the envelope.
   const data=await read(),draft=data.lists.find(l=>l.id===id&&l.owner);if(token!==generation)return false;
   if(!draft)throw error;
   if(!ready(draft))await CompassoAccount.shoppingRequest('compasso_shopping_save',{list_id:id,list_name:name,list_items:items,expected_revision:draft.revision});
   else{const canonical=rows=>JSON.stringify(rows.map(t=>[t.id,t.name,t.quantity||'',t.category,!!t.bought,!!t.deleted]));if(canonical(draft.items)!==canonical(items))throw error;}
  }
  if(token!==generation)return false;const data=await read();if(token!==generation)return false;assign(data);return true;
 }catch(e){if(token===generation)snapshot.message=message(e);throw e;}finally{if(token===generation){busy=false;draw();}}}
 async function receive(id){if(busy)throw Error('Aguarde a operação atual.');const token=generation;busy=true;draw();try{let data=await read();if(token!==generation)return null;let list=data.lists.find(l=>l.id===id&&!l.owner);if(!list){if(!data.invites.some(i=>i.id===id))throw Error('not_allowed');await CompassoAccount.shoppingRequest('compasso_shopping_accept',{list_id:id});if(token!==generation)return null;data=await read();if(token!==generation)return null;list=data.lists.find(l=>l.id===id&&!l.owner);}if(!list||!ready(list))throw Error('A cópia ainda está sendo preparada. Atualize e tente novamente.');assign(data);return structuredClone(list);}catch(e){if(token===generation)snapshot.message=e.message?.includes('preparada')?e.message:message(e);throw e;}finally{if(token===generation){busy=false;draw();}}}
 async function cancel(id){if(busy)return;const token=generation;busy=true;try{await CompassoAccount.shoppingRequest('compasso_shopping_cancel',{list_id:id});if(token!==generation)return;const data=await read();if(token===generation)assign(data);}catch(e){if(token===generation)snapshot.message=message(e);}finally{if(token===generation){busy=false;draw();}}}
 window.addEventListener('beforeunload',e=>{if(busy){e.preventDefault();e.returnValue='';}});
 return {get:()=>snapshot,reset,isBusy:()=>busy,load,send,receive,cancel,ready};
})();
