-- Separate shared data. No changes to compasso_workspaces or its policies.
begin;
create table if not exists public.compasso_couples (
 id uuid primary key default gen_random_uuid(),
 name text not null check (length(name) between 1 and 80),
 owner_id uuid not null references auth.users(id),
 invited_email text,
 data jsonb not null default '{"opening":0,"entries":[],"goals":[]}'::jsonb,
 revision integer not null default 1,
 updated_at timestamptz not null default now(),
 check (jsonb_typeof(data)='object')
);
create table if not exists public.compasso_couple_members (
 user_id uuid primary key references auth.users(id),
 couple_id uuid not null references public.compasso_couples(id),
 role text not null check (role in ('owner','partner')),
 joined_at timestamptz not null default now(),
 unique(couple_id,role)
);
alter table public.compasso_couples enable row level security;
alter table public.compasso_couple_members enable row level security;
revoke all on public.compasso_couples,public.compasso_couple_members from public,anon,authenticated;

-- Only constrained RPCs can read/write these tables. All caller identities come from auth.uid().
create or replace function public.compasso_couple_get()
returns jsonb language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); mail text; result jsonb; invites jsonb;
begin
 if me is null then raise exception 'authentication_required'; end if;
 select lower(email) into mail from auth.users where id=me and email_confirmed_at is not null;
 select jsonb_build_object('id',c.id,'name',c.name,'data',c.data,'revision',c.revision,'role',m.role,
   'invitedEmail',c.invited_email,'members',(select jsonb_agg(jsonb_build_object('id',cm.user_id,'role',cm.role)) from public.compasso_couple_members cm where cm.couple_id=c.id))
 into result from public.compasso_couples c join public.compasso_couple_members m on m.couple_id=c.id where m.user_id=me;
 select coalesce(jsonb_agg(jsonb_build_object('id',c.id,'name',c.name)), '[]'::jsonb) into invites
 from public.compasso_couples c where c.invited_email=mail and not exists(select 1 from public.compasso_couple_members m where m.couple_id=c.id and m.role='partner');
 return jsonb_build_object('space',result,'invites',invites);
end; $$;

create or replace function public.compasso_couple_create(space_name text)
returns uuid language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); space_id uuid;
begin
 if me is null then raise exception 'authentication_required'; end if;
 if length(trim(space_name)) not between 1 and 80 then raise exception 'invalid_name'; end if;
 if exists(select 1 from public.compasso_couple_members where user_id=me) then raise exception 'already_member'; end if;
 insert into public.compasso_couples(name,owner_id) values(trim(space_name),me) returning id into space_id;
 insert into public.compasso_couple_members(user_id,couple_id,role) values(me,space_id,'owner');
 return space_id;
end; $$;

create or replace function public.compasso_couple_invite(space_id uuid, partner_email text)
returns void language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); own_email text;
begin
 if me is null then raise exception 'authentication_required'; end if;
 perform 1 from public.compasso_couples where id=space_id and owner_id=me for update;
 if not found then raise exception 'not_allowed'; end if;
 if exists(select 1 from public.compasso_couple_members where couple_id=space_id and role='partner') then raise exception 'space_full'; end if;
 if partner_email is null or trim(partner_email)='' then
  update public.compasso_couples set invited_email=null,updated_at=now() where id=space_id;return;
 end if;
 select lower(email) into own_email from auth.users where id=me;
 if length(trim(partner_email)) not between 3 and 254 or position('@' in partner_email)<2 or lower(trim(partner_email))=own_email then raise exception 'invalid_email'; end if;
 update public.compasso_couples set invited_email=lower(trim(partner_email)),updated_at=now() where id=space_id;
end; $$;

create or replace function public.compasso_couple_accept(space_id uuid)
returns void language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); mail text; invited text;
begin
 if me is null then raise exception 'authentication_required'; end if;
 select lower(email) into mail from auth.users where id=me and email_confirmed_at is not null;
 if mail is null then raise exception 'verified_email_required'; end if;
 select invited_email into invited from public.compasso_couples where id=space_id for update;
 if not found or invited is distinct from mail then raise exception 'not_allowed'; end if;
 if exists(select 1 from public.compasso_couple_members where user_id=me) then raise exception 'already_member'; end if;
 if exists(select 1 from public.compasso_couple_members where couple_id=space_id and role='partner') then raise exception 'space_full'; end if;
 insert into public.compasso_couple_members(user_id,couple_id,role) values(me,space_id,'partner');
 update public.compasso_couples set invited_email=null,updated_at=now() where id=space_id;
end; $$;

create or replace function public.compasso_couple_save(space_id uuid,payload jsonb,expected_revision integer)
returns integer language plpgsql security definer set search_path='' as $$
declare me uuid:=auth.uid(); next_revision integer; item jsonb;
begin
 if me is null then raise exception 'authentication_required'; end if;
 if not exists(select 1 from public.compasso_couple_members where user_id=me and couple_id=space_id) then raise exception 'not_allowed'; end if;
 if jsonb_typeof(payload) is distinct from 'object' or jsonb_typeof(payload->'entries') is distinct from 'array'
 or jsonb_typeof(payload->'goals') is distinct from 'array' or jsonb_typeof(payload->'opening') is distinct from 'number'
 or length(payload::text)>2000000 then raise exception 'invalid_payload'; end if;
 if exists(select 1 from jsonb_object_keys(payload) as fields(key) where key not in ('opening','entries','goals')) then raise exception 'invalid_payload'; end if;
 if (payload->>'opening')::numeric<>trunc((payload->>'opening')::numeric) or abs((payload->>'opening')::numeric)>9007199254740991 then raise exception 'invalid_amount'; end if;
 for item in select value from jsonb_array_elements(payload->'entries') loop
  if jsonb_typeof(item->'amount') is distinct from 'number' or (item->>'amount')::numeric<=0 or (item->>'amount')::numeric<>trunc((item->>'amount')::numeric)
  or (item->>'amount')::numeric>9007199254740991 or coalesce(item->>'kind','') not in ('income','expense')
  or length(coalesce(item->>'description','')) not between 1 and 120 or coalesce(item->>'date','')!~'^\d{4}-\d{2}-\d{2}$'
  or length(coalesce(item->>'id','')) not between 1 and 80 then raise exception 'invalid_entry'; end if;
  perform (item->>'date')::date;
  if item ? 'deleted' and jsonb_typeof(item->'deleted') is distinct from 'boolean' then raise exception 'invalid_entry';end if;
 end loop;
 for item in select value from jsonb_array_elements(payload->'goals') loop
  if jsonb_typeof(item->'amount') is distinct from 'number' or (item->>'amount')::numeric<=0 or (item->>'amount')::numeric<>trunc((item->>'amount')::numeric)
  or (item->>'amount')::numeric>9007199254740991 or length(coalesce(item->>'name','')) not between 1 and 120
  or length(coalesce(item->>'id','')) not between 1 and 80 then raise exception 'invalid_goal'; end if;
  if item ? 'archived' and jsonb_typeof(item->'archived') is distinct from 'boolean' then raise exception 'invalid_goal';end if;
  if coalesce(item->>'date','')<>'' then perform (item->>'date')::date;end if;
 end loop;
 if (select count(distinct t->>'id') from jsonb_array_elements(payload->'entries') t)<>jsonb_array_length(payload->'entries') then raise exception 'duplicate_entry';end if;
 if (select count(distinct t->>'id') from jsonb_array_elements(payload->'goals') t)<>jsonb_array_length(payload->'goals') then raise exception 'duplicate_goal';end if;
 update public.compasso_couples set data=payload,revision=revision+1,updated_at=now() where id=space_id and revision=expected_revision returning revision into next_revision;
 if next_revision is null then raise exception 'couple_conflict'; end if;
 return next_revision;
end; $$;

revoke all on function public.compasso_couple_get() from public,anon;
revoke all on function public.compasso_couple_create(text) from public,anon;
revoke all on function public.compasso_couple_invite(uuid,text) from public,anon;
revoke all on function public.compasso_couple_accept(uuid) from public,anon;
revoke all on function public.compasso_couple_save(uuid,jsonb,integer) from public,anon;
grant execute on function public.compasso_couple_get(),public.compasso_couple_create(text),public.compasso_couple_invite(uuid,text),public.compasso_couple_accept(uuid),public.compasso_couple_save(uuid,jsonb,integer) to authenticated;
commit;
