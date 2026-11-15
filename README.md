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

Validação: 60 testes de lógica financeira, autenticação, agenda, importação e handlers da interface. Execute `npm test` com Node.js.

## Compras

Lista privada por categoria da casa, com item, quantidade livre, sugestões opcionais e marcação de comprado. A lista inteira é copiada em texto organizado para colar no WhatsApp. Quando o navegador não permite acessar a área de transferência, o texto fica disponível em uma caixa para cópia manual.

## Rotina e listas salvas

O backlog mostra tarefas da data escolhida, iniciando no dia atual. Saúde exibe uma rotina fixa de domingo a sábado; dados recorrentes existentes são migrados e os registros anteriores são preservados. Listas de compras podem ser criadas, renomeadas e duplicadas; a lista antiga passa a se chamar Minha lista. A agenda inicia em 6h–22h, aceita uma faixa personalizada e oferece a visão completa de 24 horas com indicação de eventos fora da faixa.


## Metas pessoais e listas para outro usuário

Backlog → Metas organiza o PDI com objetivo, prazo, indicador de sucesso e ações acompanháveis. As metas ficam privadas.

Compras → Criar para outro usuário envia uma cópia da lista selecionada ou uma lista vazia. O destinatário recebe em Minhas listas e as alterações posteriores são independentes. A ativação já existente é aproveitada. Consulte shared-shopping-setup.md.

## Edição e planejamento financeiro

Finanças permite alternar entre lista e tabela editável. Use Editar ou Mais detalhes para corrigir pagamento e parcelas. Compras com faturas já pagas exigem desfazer o registro de pagamento antes de alterar as parcelas. A gravação continua usando a sincronização privada existente.

Contas fixas mensais têm valor, categoria, dia de vencimento, início, fim opcional e pausa. Gere os previstos de cada mês pelo botão; repetir a geração não duplica os lançamentos existentes. Meses curtos usam o último dia. Regras alteradas não reescrevem lançamentos já gerados.

Custo de vida soma despesas do mês e parcelas vinculadas às faturas desse mês, sem duplicar pagamentos de faturas e sem investimentos. Compras antigas sem vínculo de parcelas precisam ser revisadas para entrar nesse cálculo. Investimentos mostra aportes realizados menos resgates, usando a categoria Investimentos; não estima rendimentos nem saldo de corretoras. O gráfico oferece detalhes por mouse, clique ou teclado, preservando as cores do aplicativo.

## Usabilidade das finanças

A tela prioriza contas e faturas do mês, com navegação entre meses, atalhos para despesa, receita e valor fechado de fatura. A pagar permite abrir a composição exata; cada fatura detalha os lançamentos vinculados, inclusive registros com datas de outros meses. A lista usa por padrão o mês da fatura para compras no cartão, com busca, filtro por situação e opção de consultar pela data ou todos os meses.

O formulário mostra o efeito no caixa e o mês de cobrança antes de salvar. Novos lançamentos seguem o mês selecionado; o mês da fatura acompanha a data até ser escolhido manualmente. Uma fatura anterior à data exige confirmação explícita. A tabela permite mudar diretamente o mês de uma compra de parcela única, recalculando as faturas de origem e destino. Compras parceladas continuam editáveis pelo formulário completo. Valores com milhares em português, como 1.234,56, são aceitos.

Ao cadastrar conta fixa, uma opção cria o previsto do mês selecionado junto com a regra; pagamentos continuam dependendo de confirmação do usuário. Os gráficos interativos, cards de custo de vida e investimentos, metas, referências anteriores e resumo do casal permanecem disponíveis.

## Finanças pessoais: simplificar e personalizar

Finanças se divide em Mês, Fixos e Investimentos. A tela mensal destaca três indicadores e recolhe faturas, gráficos e explicações. Meu caixa é a sobra após receitas previstas e contas em aberto do mês, podendo ser negativo; recebimentos e pagamentos de meses posteriores não entram antes da hora. O gráfico continua mostrando movimentações realizadas, separado da projeção mensal.

Custo de vida pode ser personalizado por categoria e com exceções por lançamento. Essas escolhas só alteram esse indicador. Compras no cartão entram por suas parcelas vinculadas ao mês da fatura.

Fixos aceita despesas e recebimentos mensais, como salário e benefícios. A geração cria previstos, respeita início, fim e pausa e não duplica lançamentos já criados. Valores recebidos continuam exigindo confirmação.

Investimentos acompanha saldo inicial investido, aportes, resgates, rendimentos e perdas em reais. Patrimônio e rendimentos não são adicionados ao caixa. Por padrão, registros novos só alteram esse indicador; em aportes e resgates, o usuário pode marcar explicitamente a movimentação do dinheiro disponível. Movimentações antigas realizadas da categoria Investimentos são preservadas e integram o patrimônio acompanhado.

## Identidade e ícone do celular

A proposta Direção combina um C com uma agulha de bússola em verde-menta sobre verde escuro. SVG editável em docs/brand/direction.svg. PNGs opacos de 32, 180, 192 e 512 px servem favicon, Safari/iPhone e manifesto Android; o símbolo fica dentro da área segura para recortes maskable. A marca anterior permanece em docs/icon.svg.

Veja as três propostas em marca.html. Para adicionar o aplicativo à tela inicial, abra a página principal. Atalhos instalados antes da atualização podem exigir que o usuário adicione novamente para atualizar o ícone. Não há instalação automática nem promessa de uso offline.
