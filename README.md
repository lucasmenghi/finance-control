# Finance Control

Aplicação pessoal para registrar receitas e despesas, acompanhar o orçamento mensal e visualizar projeções de caixa.

## Funcionalidades

- Login por e-mail e senha com Supabase Auth.
- Dados permanentes no PostgreSQL/Supabase.
- Isolamento por usuário com Row Level Security (RLS).
- Visão geral executiva com projeção de caixa, lançamentos, importação XLSX e backup CSV.
- Tema claro ou escuro com identidade visual consistente em todas as páginas.
- SQLite opcional exclusivamente para desenvolvimento local.

## Configurar o Supabase

1. Crie um projeto em https://supabase.com.
2. Abra **SQL Editor**, copie `supabase/migrations/001_initial_schema.sql` e execute.
   Em instalações existentes, execute também as migrações seguintes em ordem numérica.
3. Em **Authentication > Users**, crie seu usuário por e-mail e senha.
4. Em **Authentication > Providers > Email**, desative novos cadastros públicos após criar o usuário.
5. Copie a URL do projeto e a chave **Publishable**. Nunca use `service_role` no app.

## Configurar o Streamlit Cloud

Abra **Settings > Secrets** no app e cadastre:

```toml
[supabase]
url = "https://SEU-PROJETO.supabase.co"
publishable_key = "SUA_CHAVE_PUBLICAVEL"
```

Salve e reinicie o app. A tela de login aparecerá antes de qualquer dado.

## Executar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
streamlit run app.py
```

Para desenvolvimento SQLite: `FINANCE_LOCAL_MODE=1 streamlit run app.py`.

## Testes

```bash
pytest
```

## Segurança

- Segredos e banco local não são versionados.
- Usuários anônimos não recebem privilégios nas tabelas.
- Operações são filtradas por `auth.uid() = user_id` no PostgreSQL.
- O app usa somente a chave publicável e a sessão do usuário, nunca `service_role`.
- A importação grava os dados no `user_id` da sessão e ignora lançamentos idênticos em reenvios.
