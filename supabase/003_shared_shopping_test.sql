begin;
insert into auth.users(id,email,email_confirmed_at) values
 ('8b76a64d-b046-42cd-a1cd-0f1500000001','shopping-owner@example.invalid',now()),
 ('8b76a64d-b046-42cd-a1cd-0f1500000002','shopping-recipient@example.invalid',now()),
 ('8b76a64d-b046-42cd-a1cd-0f1500000003','shopping-outsider@example.invalid',now());
insert into public.compasso_workspaces(user_id,data) values('8b76a64d-b046-42cd-a1cd-0f1500000001','{"developmentPlans":[{"title":"pdi-private-marker"}],"opening":12345}');
set local role authenticated;
do $$
declare lid uuid;other_list uuid;response jsonb;rev integer;items jsonb:='[{"id":"rice","name":"Arroz","quantity":"5 kg","category":"pantry","bought":false,"deleted":false}]';
begin
 perform set_config('request.jwt.claim.sub','8b76a64d-b046-42cd-a1cd-0f1500000001',true);
 lid:=public.compasso_shopping_create('Lista compartilhada','shopping-recipient@example.invalid');
 other_list:=public.compasso_shopping_create('Outra lista','different-recipient@example.invalid');
 rev:=public.compasso_shopping_save(lid,'Lista compartilhada',items,1);
 if rev<>2 then raise exception 'owner_save_failed';end if;
 perform set_config('request.jwt.claim.sub','8b76a64d-b046-42cd-a1cd-0f1500000003',true);
 response:=public.compasso_shopping_get();
 if jsonb_array_length(response->'lists')<>0 or jsonb_array_length(response->'invites')<>0 then raise exception 'outsider_can_read';end if;
 begin perform public.compasso_shopping_accept(lid);raise exception 'outsider_can_accept';exception when others then if sqlerrm<>'not_allowed' then raise;end if;end;
 begin perform public.compasso_shopping_save(lid,'Hack',items,2);raise exception 'outsider_can_write';exception when others then if sqlerrm<>'not_allowed' then raise;end if;end;
 perform set_config('request.jwt.claim.sub','8b76a64d-b046-42cd-a1cd-0f1500000002',true);
 response:=public.compasso_shopping_get();
 if jsonb_array_length(response->'lists')<>0 or jsonb_array_length(response->'invites')<>1 or response::text like '%Arroz%' then raise exception 'pending_invite_exposes_items';end if;
 perform public.compasso_shopping_accept(lid);
 response:=public.compasso_shopping_get();
 if jsonb_array_length(response->'lists')<>1 or response::text like '%pdi-private-marker%' then raise exception 'private_data_leaked';end if;
 if (select count(*) from public.compasso_workspaces where user_id='8b76a64d-b046-42cd-a1cd-0f1500000001')<>0 then raise exception 'private_workspace_readable';end if;
 items:=jsonb_set(items,'{0,bought}','true');
 rev:=public.compasso_shopping_save(lid,'Lista compartilhada',items,3);
 if rev<>4 then raise exception 'recipient_save_failed';end if;
 begin perform public.compasso_shopping_save(lid,'Stale',items,3);raise exception 'stale_write_allowed';exception when others then if sqlerrm<>'shopping_conflict' then raise;end if;end;
 begin perform public.compasso_shopping_save(lid,'Invalid','[{"id":"x","name":"X","category":"other","bought":false,"developmentPlans":[]}]',4);raise exception 'private_payload_allowed';exception when others then if sqlerrm<>'invalid_item' then raise;end if;end;
 perform set_config('request.jwt.claim.sub','8b76a64d-b046-42cd-a1cd-0f1500000001',true);
 perform public.compasso_shopping_cancel(other_list);
 if has_table_privilege('authenticated','public.compasso_shared_shopping','SELECT') then raise exception 'direct_access_allowed';end if;
 if has_function_privilege('anon','public.compasso_shopping_get()','EXECUTE') then raise exception 'anonymous_access_allowed';end if;
end $$;
rollback;
select 'PASS: shared shopping isolated, acceptance required, private PDI protected, stale writes denied, fixtures rolled back' as result;
