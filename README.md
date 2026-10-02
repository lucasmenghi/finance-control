# Compasso

Planejamento pessoal, tarefas, leituras, jogos e finanças em uma interface responsiva.

## Versão atual

Login com Supabase Auth e espaço privado por usuário. Tarefas, leituras, jogos e finanças ficam no banco, com políticas RLS. A demonstração continua disponível separadamente, apenas no navegador, e nunca é importada automaticamente para uma conta. Sem integração bancária ou Google Agenda; regras financeiras ainda em homologação.

- Hoje, semana e backlog; concluir, reagendar e reduzir tarefas.
- Leituras e jogos com progresso, situação e sessões planejadas.
- Receitas, despesas, categoria obrigatória, parcelas e faturas.
- Gráfico mensal de entradas, saídas e caixa acumulado realizado.
- Exportação JSON e persistência privada no Supabase após login. A demonstração usa armazenamento local. Confira o status de sincronização antes de sair; conflitos entre dispositivos exigem exportar/recarregar.
- Sem gamificação ou notificações.

## Executar

Requer Node.js 20 ou superior. Não há dependências para instalar.

```sh
npm start
npm test
```

Abra http://127.0.0.1:4173.

## Publicar no GitHub Pages

Settings → Pages → Deploy from a branch → main → /docs → Save.
Os caminhos são relativos para funcionar sob o endereço do repositório, inclusive após renomeação.
Abra a URL HTTPS fornecida pelo GitHub no Safari e use Compartilhar → Adicionar à Tela de Início. Não há suporte offline nesta versão.

## Organização

- docs/: aplicação estática publicável.
- finance.test.cjs: testes das regras monetárias e histórico.
- server.cjs: servidor local, somente loopback.
- legacy/: versão anterior Streamlit/Supabase preservada para referência.

## Próximas etapas

Homologação privada da carga inicial, edição financeira, regras reais de fechamento/vencimento e integração de agenda com aprovação. Configuração das contas em [auth-setup.md](auth-setup.md).

Nenhum dado pessoal do planejamento foi incluído nesta publicação. Contas novas começam vazias. O saldo inicial e os lançamentos de exemplo são fictícios e exclusivos da demonstração. A configuração frontend contém somente a chave publicável, nunca credenciais administrativas.

## Planejamento e saúde

Agenda semanal com horários, tarefas sem hora e rotinas recorrentes. A aba Saúde organiza treinos e refeições; treinos aparecem na mesma agenda. Tema claro/escuro segue a preferência do dispositivo e pode ser alternado.

A importação privada usa arquivos `compasso-import-v1`, preserva registros existentes e rejeita conflitos financeiros. Arquivos pessoais não devem ser enviados para este repositório público. As contas fixas nas referências são orçamento, não pagamentos realizados.

Validação: 28 testes de lógica financeira, autenticação, agenda, importação e handlers da interface. Execute `npm test` com Node.js.

## Compras

Lista privada por categoria da casa, com item, quantidade livre, sugestões opcionais e marcação de comprado. A lista inteira é copiada em texto organizado para colar no WhatsApp. Quando o navegador não permite acessar a área de transferência, o texto fica disponível em uma caixa para cópia manual.
