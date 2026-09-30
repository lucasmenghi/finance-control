alter table public.transactions
add column if not exists income_type text not null default 'Não se aplica';

alter table public.transactions
drop constraint if exists transactions_income_type_check;

alter table public.transactions
add constraint transactions_income_type_check check (
    income_type in ('Não se aplica', 'Salário', 'VA/VR', '13º salário', 'Renda extra', 'Bônus', 'Benefício', 'Outros')
);

update public.transactions
set income_type = case
    when lower(description) like '%vale-alimenta%' or lower(description) like '%va/vr%' then 'VA/VR'
    when lower(description) like '%13º%' or lower(description) like '%13°%' then '13º salário'
    when lower(description) like '%ppr%' or lower(description) like '%bônus%' then 'Bônus'
    when lower(description) like '%auxílio%' or lower(description) like '%benefício%' then 'Benefício'
    when lower(description) like '%salário%' or lower(description) like '%dissídio%' then 'Salário'
    else 'Outros'
end
where kind = 'Receita' and income_type = 'Não se aplica';
