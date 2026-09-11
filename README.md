# Finance Control

Aplicação pessoal para registrar receitas e despesas, acompanhar o orçamento mensal e visualizar projeções de caixa.

## Funcionalidades do MVP

- Dashboard mensal com receitas, despesas, saldo e comprometimento da renda.
- Cadastro e exclusão de lançamentos.
- Status pago, previsto ou atrasado.
- Orçamento por categoria com comparação entre limite e gasto.
- Projeção de caixa para até 24 meses.
- Persistência local em SQLite.

## Executar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

O banco é criado automaticamente em `data/finance.db`. A pasta `data/` não é enviada ao GitHub.

## Testes

```bash
pytest
```

## Segurança e próximos passos

O MVP não salva dados financeiros no repositório. Para uso online e sincronização entre dispositivos, a próxima evolução será substituir SQLite por PostgreSQL/Supabase e adicionar autenticação.

