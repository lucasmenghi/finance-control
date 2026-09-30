# Ativar contas pessoais

1. Reutilize o projeto Supabase ou crie um projeto. Execute `supabase/001_private_workspaces.sql` no SQL Editor.
2. Em Authentication → Users, crie as duas contas por um fluxo de convite/configuração de senha feito pelos próprios usuários. Senhas nunca devem ser colocadas em commits ou enviadas ao assistente.
3. Restrinja novos cadastros públicos em Authentication → Providers/Sign In settings se o uso for somente do casal.
4. Preencha `docs/config.js` com URL HTTPS do projeto e chave publishable/anon. Nunca coloque service_role ou secret key no frontend.
5. Publique e teste com duas contas: A grava uma tarefa e sai; B deve iniciar vazio e não ler/escrever a linha de A, mesmo fazendo requisição direta. A entra novamente e recupera seus dados. Faça essa validação antes de dados reais.

Cada conta usa uma linha própria no banco, protegida por RLS em SELECT/INSERT/UPDATE. O RPC é security invoker e usa auth.uid(), sem aceitar ID arbitrário. Não há compartilhamento entre casal. Conta nova começa vazia; não importa dados da demonstração automaticamente.

Tokens de sessão são gerenciados pelo SDK Supabase no navegador. Dados pessoais ficam em memória durante uso e no banco; não são copiados para o cache da demonstração. Ao sair, a interface e o estado são limpos. Falha de leitura não inicia conta vazia nem sobrescreve o banco. Conflitos de edição entre dispositivos bloqueiam novas gravações até exportar/recarregar, evitando perda silenciosa.

Limites: sem recuperação de senha no app ainda; administração pelo painel. Revisão por documento inteiro, sem mesclagem automática. Uso simultâneo pode exigir exportar a versão local e recarregar a remota. Validação de isolamento precisa ser executada no projeto real após configuração.
