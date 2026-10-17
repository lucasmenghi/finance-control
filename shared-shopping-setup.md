# Listas por cópia e metas pessoais

## Ativação

A estrutura de envio usa os RPCs e a tabela protegida de `supabase/003_shared_shopping.sql`. O teste `supabase/003_shared_shopping_test.sql` valida acesso por destinatário, aceite, isolamento e revisões. A tabela funciona como envelope de entrega; não é o armazenamento das listas pessoais. Não é necessária outra migração para o modo cópia.

## Enviar e receber

Em Compras, escolher Criar para outro usuário. Informar nome e e-mail e confirmar os itens da lista selecionada ou desmarcar a opção para enviar vazia. A lista original não é modificada. O destinatário acessa Enviadas e recebidas e escolhe Receber minha cópia. O e-mail precisa estar confirmado. Não há envio automático de e-mail.

A cópia é gravada no workspace privado do destinatário com novos IDs de itens e com confirmação do salvamento. Alterações futuras, renomeações e marcações não são sincronizadas entre as cópias. Receber novamente o mesmo envio abre a cópia existente, sem duplicar ou sobrescrever alterações. O app bloqueia o recebimento enquanto existem alterações pessoais pendentes de sincronização.

Envios interrompidos podem ser concluídos. A recepção aguarda a gravação do conteúdo antes de importar, inclusive quando o aceite ocorre durante a preparação. O criador pode cancelar envios pendentes.

## PDI privado

Backlog → Metas permite cadastrar objetivo, área, prazo, situação, resultado esperado, ações, contexto e revisão. As metas ficam somente em `developmentPlans` no workspace privado existente e não são incluídas no envio de listas. A edição preserva ações concluídas e arquiva ações removidas do plano. Metas podem ser arquivadas e restauradas.
