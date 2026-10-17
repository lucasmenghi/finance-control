-- Shopping sharing is independent from private workspaces and couple finances.
begin;
create table if not exists public.compasso_shared_shopping (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references auth.users(id),
 recipient_email text not null,
 recipient_id uuid references auth.users(id),
 name text not null check(length(name) between 1 and 80),
 items jsonb not null default '[]'::jsonb check(jsonb_typeof(items)='array'),
 status text not null default 'pending' check(status in ('pending','accepted','cancelled')),
 revision integer not null default 1,
 updated_at timestamptz not null default now(),
 check(recipient_id is null or recipient_id<>owner_id)
);
alter table public.compasso_shared_shopping enable row level security;
revoke all on public.compasso_shared_shopping from public,anon,authenticated;

create or replace function public.compasso_shopping_get()
returns jsonb language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid();mail text;lists jsonb;invites jsonb;
begin
 if me is null then raise exception 'authentication_required';end if;
 select lower(email) into mail from auth.users where id=me and email_confirmed_at is not null;
 select coalesce(jsonb_agg(jsonb_build_object('id',id,'name',name,'items',items,'revision',revision,'status',status,'owner',owner_id=me,'recipientEmail',recipient_email) order by updated_at desc),'[]'::jsonb)
 into lists from public.compasso_shared_shopping where status<>'cancelled' and (owner_id=me or(recipient_id=me and status='accepted'));
 select coalesce(jsonb_agg(jsonb_build_object('id',id,'name',name)),'[]'::jsonb) into invites
 from public.compasso_shared_shopping where recipient_email=mail and status='pending' and owner_id<>me;
 return jsonb_build_object('lists',lists,'invites',invites);
end; $$;

create or replace function public.compasso_shopping_create(list_name text,recipient_email text,initial_items jsonb default '[]'::jsonb)
returns uuid language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid();own_email text;list_id uuid;
begin
 if me is null then raise exception 'authentication_required';end if;
 select lower(email) into own_email from auth.users where id=me;
 if length(trim(list_name)) not between 1 and 80 then raise exception 'invalid_name';end if;
 if length(trim(recipient_email)) not between 3 and 254 or position('@' in recipient_email)<2 or lower(trim(recipient_email))=own_email then raise exception 'invalid_email';end if;
 -- Initial contents must be added through the validated save RPC.
 if initial_items is distinct from '[]'::jsonb then raise exception 'invalid_items';end if;
 insert into public.compasso_shared_shopping(owner_id,recipient_email,name) values(me,lower(trim(recipient_email)),trim(list_name)) returning id into list_id;
 return list_id;
end; $$;

create or replace function public.compasso_shopping_accept(list_id uuid)
returns void language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid();mail text;row_data public.compasso_shared_shopping%rowtype;
begin
 if me is null then raise exception 'authentication_required';end if;
 select lower(email) into mail from auth.users where id=me and email_confirmed_at is not null;
 if mail is null then raise exception 'verified_email_required';end if;
 select * into row_data from public.compasso_shared_shopping where id=list_id for update;
 if not found or row_data.status<>'pending' or row_data.recipient_email is distinct from mail or row_data.owner_id=me then raise exception 'not_allowed';end if;
 update public.compasso_shared_shopping set recipient_id=me,status='accepted',revision=revision+1,updated_at=now() where id=list_id;
end; $$;

create or replace function public.compasso_shopping_save(list_id uuid,list_name text,list_items jsonb,expected_revision integer)
returns integer language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid();next_revision integer;item jsonb;
begin
 if me is null then raise exception 'authentication_required';end if;
 if not exists(select 1 from public.compasso_shared_shopping where id=list_id and status<>'cancelled' and(owner_id=me or(recipient_id=me and status='accepted'))) then raise exception 'not_allowed';end if;
 if length(trim(list_name)) not between 1 and 80 or jsonb_typeof(list_items) is distinct from 'array' or length(list_items::text)>1000000 then raise exception 'invalid_items';end if;
 if jsonb_array_length(list_items)>500 then raise exception 'too_many_items';end if;
 for item in select value from jsonb_array_elements(list_items) loop
  if length(trim(coalesce(item->>'name',''))) not between 1 and 120 or length(coalesce(item->>'quantity',''))>60
  or coalesce(item->>'id','')!~'^[a-zA-Z0-9_-]{1,100}$' or jsonb_typeof(item->'bought') is distinct from 'boolean'
  or coalesce(item->>'category','') not in ('produce','pantry','protein','dairy','bakery','frozen','drinks','cleaning','hygiene','house','pets','other') then raise exception 'invalid_item';end if;
  if item ? 'deleted' and jsonb_typeof(item->'deleted') is distinct from 'boolean' then raise exception 'invalid_item';end if;
  if exists(select 1 from jsonb_object_keys(item) as fields(key) where key not in ('id','name','quantity','category','bought','deleted')) then raise exception 'invalid_item';end if;
 end loop;
 if (select count(distinct t->>'id') from jsonb_array_elements(list_items) t)<>jsonb_array_length(list_items) then raise exception 'duplicate_item';end if;
 update public.compasso_shared_shopping set name=trim(list_name),items=list_items,revision=revision+1,updated_at=now() where id=list_id and revision=expected_revision returning revision into next_revision;
 if next_revision is null then raise exception 'shopping_conflict';end if;
 return next_revision;
end; $$;

create or replace function public.compasso_shopping_cancel(list_id uuid)
returns void language plpgsql security definer set search_path='' as $$
begin
 if auth.uid() is null then raise exception 'authentication_required';end if;
 update public.compasso_shared_shopping set status='cancelled',revision=revision+1,updated_at=now() where id=list_id and owner_id=auth.uid() and status='pending';
 if not found then raise exception 'not_allowed';end if;
end; $$;
revoke all on function public.compasso_shopping_get(),public.compasso_shopping_create(text,text,jsonb),public.compasso_shopping_accept(uuid),public.compasso_shopping_save(uuid,text,jsonb,integer),public.compasso_shopping_cancel(uuid) from public,anon;
grant execute on function public.compasso_shopping_get(),public.compasso_shopping_create(text,text,jsonb),public.compasso_shopping_accept(uuid),public.compasso_shopping_save(uuid,text,jsonb,integer),public.compasso_shopping_cancel(uuid) to authenticated;
commit;
