(function(root){
const categories=[
 {id:'produce',name:'Hortifruti',suggestions:['Banana','Maçã','Tomate','Cebola','Alface']},
 {id:'pantry',name:'Despensa',suggestions:['Arroz','Feijão','Macarrão','Azeite','Café']},
 {id:'protein',name:'Carnes e proteínas',suggestions:['Frango','Carne','Peixe','Ovos']},
 {id:'dairy',name:'Leites e derivados',suggestions:['Leite','Queijo','Iogurte','Manteiga']},
 {id:'bakery',name:'Pães e café da manhã',suggestions:['Pão','Aveia','Tapioca']},
 {id:'frozen',name:'Congelados',suggestions:['Legumes congelados','Polpa de fruta']},
 {id:'drinks',name:'Bebidas',suggestions:['Água','Suco','Chá']},
 {id:'cleaning',name:'Limpeza e lavanderia',suggestions:['Detergente','Sabão para roupas','Desinfetante','Saco de lixo']},
 {id:'hygiene',name:'Higiene pessoal',suggestions:['Papel higiênico','Sabonete','Pasta de dente','Shampoo']},
 {id:'house',name:'Casa e utilidades',suggestions:['Esponja','Papel-toalha','Pilha','Lâmpada']},
 {id:'pets',name:'Pets',suggestions:['Ração','Areia']},
 {id:'other',name:'Outros',suggestions:[]}
];
function values(name,quantity,category){name=String(name||'').trim();quantity=String(quantity||'').trim();if(!name||name.length>120)throw Error('Informe um item com até 120 caracteres.');if(quantity.length>60)throw Error('Quantidade muito longa.');if(!categories.some(c=>c.id===category))throw Error('Categoria inválida.');return {name,quantity,category};}
function format(items,onlyPending=false){const selected=items.filter(t=>!onlyPending||!t.bought);if(!selected.length)return '';return ['*Lista de compras*',...categories.flatMap(c=>{const rows=selected.filter(t=>t.category===c.id);return rows.length?['',`*${c.name}*`,...rows.map(t=>`${t.bought?'☑':'☐'} ${String(t.name).replace(/[\r\n]+/g,' ')}${t.quantity?' — '+String(t.quantity).replace(/[\r\n]+/g,' '):''}`)]:[];})].join('\n');}
const api={categories,values,format};if(typeof module!=='undefined')module.exports=api;else root.Shopping=api;
})(globalThis);
