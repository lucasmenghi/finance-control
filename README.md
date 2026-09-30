# Compasso

Planejamento pessoal, tarefas, leituras, jogos e finanças em uma interface responsiva.

## Versão atual

Demonstração navegável com dados fictícios e armazenamento local no navegador. Sem login, servidor de dados, sincronização entre dispositivos ou integração bancária/Google Agenda. Não é ainda a versão para controle financeiro real.

- Hoje, semana e backlog; concluir, reagendar e reduzir tarefas.
- Leituras e jogos com progresso, situação e sessões planejadas.
- Receitas, despesas, categoria obrigatória, parcelas e faturas.
- Gráfico mensal de entradas, saídas e caixa acumulado realizado.
- Exportação JSON e persistência local. Limpar dados do navegador remove os registros locais.
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

Autenticação, persistência por usuário, homologação privada da carga inicial, edição financeira, regras reais de fechamento/vencimento e integração de agenda com aprovação.

Nenhum dado pessoal do planejamento foi incluído nesta publicação. O saldo inicial e os lançamentos de exemplo são fictícios. Dados digitados pelo visitante ficam no navegador dele.
