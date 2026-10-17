# Listas para outro usuário e metas pessoais

## Ativação de listas compartilhadas

No mesmo projeto Supabase, executar `supabase/003_shared_shopping.sql` e depois `supabase/003_shared_shopping_test.sql`. O teste deve terminar com PASS. Ele usa apenas fixtures e faz rollback ao final; não altera contas ou listas reais.

Em Compras, escolher Criar para outro usuário e informar um nome e o e-mail usado pela pessoa no Compasso. A lista começa vazia; o criador pode preenchê-la por categoria. A outra pessoa encontra o convite em Compras → Com outro usuário e precisa aceitá-lo. O e-mail precisa estar confirmado.

Só a lista criada é compartilhada. Antes do aceite, a outra pessoa vê apenas nome e convite. Depois, os dois podem editar e marcar os itens. Não há envio automático de e-mail. O criador pode cancelar um convite pendente. Itens removidos podem ser restaurados. As gravações conferem revisão para evitar que uma alteração sobrescreva outra silenciosamente.

As tabelas de finanças pessoais, casal e workspaces não recebem novas políticas ou permissões. A nova tabela tem RLS e acesso apenas por RPC com checagem de identidade e vínculo por lista.

## Metas pessoais — PDI

Backlog → Metas permite cadastrar objetivo, área, prazo, situação, resultado esperado, plano de ação, contexto e revisão. As metas são armazenadas somente no workspace privado existente (`developmentPlans`); não é necessária migração para o PDI.

O progresso acompanha as ações concluídas. A edição preserva o progresso de ações que continuam no plano e arquiva ações retiradas. Metas podem ser arquivadas e restauradas. Não se confundem com metas financeiras pessoais ou metas do casal.
