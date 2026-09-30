-- Execute no SQL Editor do projeto Supabase. Não altera tabelas do app antigo.
create table if not exists public.compasso_workspaces (
  user_id uuid primary key references auth.users(id) on delete cascade,
  data jsonb not null,
  revision integer not null default 1,
  updated_at timestamptz not null default now(),
  constraint compasso_data_object check (jsonb_typeof(data) = 'object')
);
alter table public.compasso_workspaces enable row level security;
revoke all on public.compasso_workspaces from anon;
grant select, insert, update on public.compasso_workspaces to authenticated;
drop policy if exists compasso_read_own on public.compasso_workspaces;
create policy compasso_read_own on public.compasso_workspaces for select to authenticated using (auth.uid() = user_id);
drop policy if exists compasso_insert_own on public.compasso_workspaces;
create policy compasso_insert_own on public.compasso_workspaces for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists compasso_update_own on public.compasso_workspaces;
create policy compasso_update_own on public.compasso_workspaces for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Compare-and-swap: um dispositivo antigo nunca sobrescreve silenciosamente outro.
create or replace function public.save_compasso_workspace(payload jsonb, expected_revision integer)
returns integer language plpgsql security invoker set search_path = '' as $$
declare next_revision integer;
begin
  if auth.uid() is null then raise exception 'authentication_required'; end if;
  if expected_revision = 0 then
    insert into public.compasso_workspaces(user_id, data, revision)
      values (auth.uid(), payload, 1) on conflict do nothing returning revision into next_revision;
  else
    update public.compasso_workspaces set data=payload, revision=revision+1, updated_at=now()
      where user_id=auth.uid() and revision=expected_revision returning revision into next_revision;
  end if;
  if next_revision is null then raise exception 'workspace_conflict'; end if;
  return next_revision;
end;
$$;
revoke all on function public.save_compasso_workspace(jsonb,integer) from public, anon;
grant execute on function public.save_compasso_workspace(jsonb,integer) to authenticated;
