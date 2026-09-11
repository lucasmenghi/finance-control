create extension if not exists pgcrypto;

create table if not exists public.transactions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    description text not null,
    amount numeric(14,2) not null check (amount > 0),
    kind text not null check (kind in ('Receita', 'Despesa')),
    category text not null,
    account text not null,
    occurred_on date not null,
    status text not null default 'Pago' check (status in ('Previsto', 'Pago', 'Atrasado')),
    notes text not null default '',
    created_at timestamptz not null default now()
);
create table if not exists public.budgets (
    user_id uuid not null references auth.users(id) on delete cascade,
    month text not null check (month ~ '^\\d{4}-\\d{2}$'), category text not null,
    amount numeric(14,2) not null check (amount >= 0),
    primary key (user_id, month, category)
);
create table if not exists public.settings (
    user_id uuid not null references auth.users(id) on delete cascade,
    key text not null, value text not null, primary key (user_id, key)
);

create index if not exists transactions_user_id_idx on public.transactions(user_id);
create index if not exists transactions_user_month_idx on public.transactions(user_id, occurred_on);
create index if not exists budgets_user_id_idx on public.budgets(user_id);
create index if not exists settings_user_id_idx on public.settings(user_id);

alter table public.transactions enable row level security;
alter table public.budgets enable row level security;
alter table public.settings enable row level security;
revoke all on public.transactions, public.budgets, public.settings from anon, authenticated;
grant select, insert, update, delete on public.transactions, public.budgets, public.settings to authenticated;

create policy "transactions_select_own" on public.transactions for select to authenticated using ((select auth.uid()) = user_id);
create policy "transactions_insert_own" on public.transactions for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "transactions_update_own" on public.transactions for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "transactions_delete_own" on public.transactions for delete to authenticated using ((select auth.uid()) = user_id);
create policy "budgets_select_own" on public.budgets for select to authenticated using ((select auth.uid()) = user_id);
create policy "budgets_insert_own" on public.budgets for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "budgets_update_own" on public.budgets for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "budgets_delete_own" on public.budgets for delete to authenticated using ((select auth.uid()) = user_id);
create policy "settings_select_own" on public.settings for select to authenticated using ((select auth.uid()) = user_id);
create policy "settings_insert_own" on public.settings for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "settings_update_own" on public.settings for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "settings_delete_own" on public.settings for delete to authenticated using ((select auth.uid()) = user_id);

