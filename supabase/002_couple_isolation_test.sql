-- Non-destructive integration test: every fixture is rolled back.
begin;
insert into auth.users(id,email,email_confirmed_at) values
 ('b165ab09-4b38-4e4e-8ec5-610efb3dc001','compasso-owner-fixture@example.invalid',now()),
 ('b165ab09-4b38-4e4e-8ec5-610efb3dc002','compasso-partner-fixture@example.invalid',now()),
 ('b165ab09-4b38-4e4e-8ec5-610efb3dc003','compasso-outsider-fixture@example.invalid',now());
insert into public.compasso_workspaces(user_id,data) values
 ('b165ab09-4b38-4e4e-8ec5-610efb3dc001','{"privateMarker":"do-not-share","opening":999999}');
set local role authenticated;
do $$
declare sid uuid; snapshot jsonb; rev integer;
begin
 perform set_config('request.jwt.claim.sub','b165ab09-4b38-4e4e-8ec5-610efb3dc001',true);
 sid:=public.compasso_couple_create('Fixture do casal');
 perform public.compasso_couple_invite(sid,'compasso-partner-fixture@example.invalid');
 snapshot:=public.compasso_couple_get();
 if snapshot::text like '%do-not-share%' or (snapshot->'space'->'data'->>'opening')::integer<>0 then raise exception 'private_data_leaked'; end if;
 perform set_config('request.jwt.claim.sub','b165ab09-4b38-4e4e-8ec5-610efb3dc003',true);
 if public.compasso_couple_get()->'space' is distinct from 'null'::jsonb then raise exception 'outsider_can_read'; end if;
 begin perform public.compasso_couple_save(sid,'{"opening":0,"entries":[],"goals":[]}',1);raise exception 'outsider_can_write'; exception when others then if sqlerrm<>'not_allowed' then raise; end if;end;
 begin perform public.compasso_couple_accept(sid);raise exception 'outsider_can_join'; exception when others then if sqlerrm<>'not_allowed' then raise; end if;end;
 perform set_config('request.jwt.claim.sub','b165ab09-4b38-4e4e-8ec5-610efb3dc002',true);
 if jsonb_array_length(public.compasso_couple_get()->'invites')<>1 then raise exception 'invite_missing'; end if;
 if (select count(*) from public.compasso_workspaces where user_id='b165ab09-4b38-4e4e-8ec5-610efb3dc001')<>0 then raise exception 'partner_can_read_personal_workspace'; end if;
 perform public.compasso_couple_accept(sid);
 rev:=public.compasso_couple_save(sid,'{"opening":1000,"entries":[],"goals":[]}',1);
 if rev<>2 then raise exception 'partner_save_failed';end if;
 begin perform public.compasso_couple_save(sid,'{"opening":999,"entries":[],"goals":[]}',1);raise exception 'stale_write_allowed'; exception when others then if sqlerrm<>'couple_conflict' then raise;end if;end;
 begin perform public.compasso_couple_save(sid,'{"opening":0,"entries":[],"goals":[],"tasks":["private"]}',2);raise exception 'private_payload_allowed'; exception when others then if sqlerrm<>'invalid_payload' then raise;end if;end;
 if has_table_privilege('authenticated','public.compasso_couples','SELECT') then raise exception 'direct_table_access_allowed';end if;
 if has_function_privilege('anon','public.compasso_couple_get()','EXECUTE') then raise exception 'anonymous_access_allowed';end if;
 perform set_config('request.jwt.claim.sub','b165ab09-4b38-4e4e-8ec5-610efb3dc001',true);
 snapshot:=public.compasso_couple_get();
 if jsonb_array_length(snapshot->'space'->'members')<>2 or (snapshot->'space'->'data'->>'opening')::integer<>1000 then raise exception 'shared_data_mismatch';end if;
 if snapshot::text like '%do-not-share%' then raise exception 'private_data_leaked';end if;
end $$;
rollback;
select 'PASS: two members, isolated private data, outsider denied, stale writes denied, fixtures rolled back' as result;
