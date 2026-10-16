# Finanças do casal

O módulo usa tabelas próprias e não altera as políticas de `compasso_workspaces`.

1. No SQL Editor do projeto Supabase já configurado no app, executar `supabase/002_couple_finances.sql`.
2. Executar `supabase/002_couple_isolation_test.sql`. O teste usa três usuários fictícios dentro de uma transação e termina com rollback; deve retornar PASS.
3. No Compasso, entrar na conta pessoal, abrir Casal e criar o espaço.
4. Informar o e-mail que a outra pessoa já usa no Compasso. O convite fica dentro do aplicativo, sem disparar e-mail.
5. A outra pessoa entra na própria conta, abre Casal e aceita o convite. O e-mail precisa estar confirmado no Supabase.

Cada espaço tem no máximo dois participantes. Ambos podem registrar aportes, resgates e metas. Exclusões de movimentos e arquivamentos de metas podem ser desfeitos. Convites pendentes podem ser cancelados pelo criador.

O resumo compartilhado aparece nas finanças pessoais em um quadro separado. Ele não soma receitas, não altera o saldo pessoal nem copia lançamentos pessoais. O payload compartilhado admite apenas saldo inicial, movimentos e metas.

As tabelas compartilhadas têm RLS habilitado e nenhum acesso direto para anon/authenticated. RPCs com busca de schema fixa checam auth.uid() e o vínculo antes de cada leitura ou gravação. Escritas usam revisão para impedir que um dispositivo sobrescreva outro silenciosamente.

Não colocar e-mails reais, senhas, chaves administrativas ou dados financeiros pessoais neste repositório público. A ativação não cria participantes reais nem compartilha registros existentes.
