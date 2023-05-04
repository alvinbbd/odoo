/*------------DEAL-----------*/

-- create table deal_temp(reference text, listing_ref text, status text, sub_status text, contact_listing text, mobile text,
-- 	email text, listing_type text, price text, listing_category text, available_from text, listing_unit text, lead_ref text,
-- 	contact_lead text, lead_type text, assigned_to text, lead_source text, created_by text, transaction_type text, deal_price_aed text,
-- 	deposit_aed text, estimated_deal_date text, actual_deal_date text, cheques text, tenancy_contract_start_date text, tenancy_renewal_date text,
-- 	finance_type text, buyer_type text, gross_commission_aed text, inclusive_of_vat_yes_or_no text, total_gross_commission_aed text,
-- 	split_with_external_referral text, split_with_internal text, split_with_etwork text, total_earned_commission_aed text, emirate_or_city text,
-- 	location_or_roject text, sub_location_or_building text, bed text, bath text, floor text, street text, build_up_area_sqft text,
-- 	unit text, type text, view text, parking text, managed_status text, created_date_and_time text, last_updated_date_and_time text,
-- 	last_updated_by text, notes text);

-- alter table deal_temp add company_id integer;
psql -U postgres -d crm.asteco_crm_latest -c "alter table deal_temp add company_id integer;"
-- update deal_temp set company_id = 4 where LEFT(reference, 3) = 'HUT';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 4 where LEFT(reference, 3) = 'HUT';"
-- update deal_temp set company_id = 8 where LEFT(reference, 2) = 'PC';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 8 where LEFT(reference, 2) = 'PC';"
-- update deal_temp set company_id = 6 where LEFT(reference, 3) = 'ASA';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 6 where LEFT(reference, 3) = 'ASA';"
-- update deal_temp set company_id = 11 where LEFT(reference, 3) = 'ASB';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 11 where LEFT(reference, 3) = 'ASB';"
-- update deal_temp set company_id = 7 where LEFT(reference, 3) = 'APM';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 7 where LEFT(reference, 3) = 'APM';"
-- update deal_temp set company_id = 5 where LEFT(reference, 3) = 'AAR';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 5 where LEFT(reference, 3) = 'AAR';"
-- update deal_temp set company_id = 9 where LEFT(reference, 3) = 'ACO';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 9 where LEFT(reference, 3) = 'ACO';"
-- update deal_temp set company_id = 3 where LEFT(reference, 3) = 'HAX';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set company_id = 3 where LEFT(reference, 3) = 'HAX';"

-- delete from deal_temp where mobile = 'Mobile';

-- update deal_temp set status = 'Lost' where status = 'Closed';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set status = 'Lost' where status = 'Closed';"

-- update deal_temp set sub_status = 'unit_reserved' where sub_status = 'Unit Reserved';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set sub_status = 'unit_reserved' where sub_status = 'Unit Reserved';"
-- update deal_temp set sub_status = 'deal_lost' where sub_status = 'Deal Lost';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set sub_status = 'deal_lost' where sub_status = 'Deal Lost';"

-- update deal_temp set finance_type = 'cash' where finance_type = 'Cash';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set finance_type = 'cash' where finance_type = 'Cash';"
-- update deal_temp set buyer_type = 'investor' where buyer_type = 'Investor';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set buyer_type = 'investor' where buyer_type = 'Investor';"

-- update deal_temp set inclusive_of_vat_yes_or_no = 'no' where inclusive_of_vat_yes_or_no = 'Yes';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set inclusive_of_vat_yes_or_no = 'no' where inclusive_of_vat_yes_or_no = 'Yes';"

-- update deal_temp set tenancy_renewal_date = null where tenancy_renewal_date = '--';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set tenancy_renewal_date = null where tenancy_renewal_date = '--';"
-- update deal_temp set deal_price_aed = replace(deal_price_aed, ',', '') where deal_price_aed like '%,%';
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set deal_price_aed = replace(deal_price_aed, ',', '') where deal_price_aed like '%,%';"

psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set created_date_and_time='9/9/2019 12:21' where created_date_and_time='Open Market'"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set deal_price_aed='0' where deal_price_aed='';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set deal_price_aed='0' where deal_price_aed='Rental';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set deal_price_aed='0' where deal_price_aed='Sale';"
-- psql -U postgres -d crm.asteco_crm_latest -c "select CAST(dd.deal_price_aed AS FLOAT) from deal_temp as dd;"

psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set deposit_aed='0' where deposit_aed='';"
-- psql -U postgres -d crm.asteco_crm_latest -c "select CAST(dd.deposit_aed AS FLOAT) from deal_temp as dd;"

psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set total_earned_commission_aed='0' where total_earned_commission_aed='';"
-- psql -U postgres -d crm.asteco_crm_latest -c "select CAST(dd.total_earned_commission_aed AS FLOAT) from deal_temp as dd;"

psql -U postgres -d crm.asteco_crm_latest -c "update deal_temp set gross_commission_aed='0' where gross_commission_aed='';"
-- psql -U postgres -d crm.asteco_crm_latest -c "select CAST(dd.gross_commission_aed AS FLOAT) from deal_temp as dd;"

psql -U postgres -d crm.asteco_crm_latest -c "SELECT dd.reference, dd.parking, NULL, dd.company_id, NULL, NULL, to_timestamp(dd.estimated_deal_date, 'MM/DD/YY hh24:mi'), to_timestamp(dd.actual_deal_date, 'MM/DD/YY hh24:mi'), to_timestamp(dd.tenancy_contract_start_date, 'MM/DD/YY hh24:mi'), to_timestamp(dd.tenancy_renewal_date, 'MM/DD/YY hh24:mi'), dd.sub_status, dd.inclusive_of_vat_yes_or_no, dd.buyer_type, dd.finance_type, dd.status, CAST(dd.deal_price_aed AS FLOAT), CAST(dd.deposit_aed AS FLOAT), CAST(dd.total_earned_commission_aed AS FLOAT), CAST(dd.gross_commission_aed AS FLOAT), 9, to_timestamp(dd.created_date_and_time, 'MM/DD/YY hh24:mi'), NULL, to_timestamp(dd.last_updated_date_and_time, 'MM/DD/YY hh24:mi') FROM deal_temp as dd;"

-- INSERT INTO public.deal_deal(
-- 			name, listing_parking, cheque_id, company_id, listing_id, lead_id, 
-- 			estimated_date, actual_date, tenancy_contract_start_date, tenancy_renewal_date, 
-- 			sub_status_id, include_commission_vat, buyer_type, finance_type, deal_status, 
-- 			deal_price, deposit, total_earned_commission_amount, gross_commission,
-- 			create_uid, create_date, write_uid, write_date)
-- SELECT dd.reference, dd.parking, NULL, dd.company_id, NULL, NULL,
-- 		to_timestamp(dd.estimated_deal_date, 'MM/DD/YY hh24:mi'),to_timestamp(dd.actual_deal_date, 'MM/DD/YY hh24:mi'),
-- 		to_timestamp(dd.tenancy_contract_start_date, 'MM/DD/YY hh24:mi'), to_timestamp(dd.tenancy_renewal_date, 'MM/DD/YY hh24:mi'),
-- 		dd.sub_status, dd.inclusive_of_vat_yes_or_no, dd.buyer_type, dd.finance_type, dd.status,
-- 		CAST(dd.deal_price_aed AS FLOAT), CAST(dd.deposit_aed AS FLOAT), CAST(dd.total_earned_commission_aed AS FLOAT),
-- 		CAST(dd.gross_commission_aed AS FLOAT), 9, to_timestamp(dd.created_date_and_time, 'MM/DD/YY hh24:mi'),
-- 		NULL, to_timestamp(dd.last_updated_date_and_time, 'MM/DD/YY hh24:mi')
-- FROM deal_temp as dd;
-- psql -U postgres -d crm.asteco_crm_latest -c "INSERT INTO public.deal_deal(name, listing_parking, cheque_id, company_id, listing_id, lead_id, sub_status_id, include_commission_vat, buyer_type, finance_type, deal_status, deal_price, deposit, total_earned_commission_amount, gross_commission, create_uid, write_uid) SELECT dd.reference, dd.parking, NULL, dd.company_id, NULL, NULL,dd.sub_status, dd.inclusive_of_vat_yes_or_no, dd.buyer_type, dd.finance_type, dd.status,CAST(dd.deal_price_aed AS FLOAT), CAST(dd.deposit_aed AS FLOAT), CAST(dd.total_earned_commission_aed AS FLOAT),CAST(dd.gross_commission_aed AS FLOAT), 9, NULL FROM deal_temp as dd;"
psql -U postgres -d crm.asteco_crm_latest -c "INSERT INTO public.deal_deal(name, listing_parking, cheque_id, company_id, listing_id, lead_id, estimated_date, actual_date, tenancy_contract_start_date, tenancy_renewal_date, sub_status_id, include_commission_vat, buyer_type, finance_type, deal_status, deal_price, deposit, total_earned_commission_amount, gross_commission, create_uid, create_date, write_uid, write_date) SELECT dd.reference, dd.parking, NULL, dd.company_id, NULL, NULL,to_timestamp(dd.estimated_deal_date, 'MM/DD/YY hh24:mi'),to_timestamp(dd.actual_deal_date, 'MM/DD/YY hh24:mi'),to_timestamp(dd.tenancy_contract_start_date, 'MM/DD/YY hh24:mi'), to_timestamp(dd.tenancy_renewal_date, 'MM/DD/YY hh24:mi'),dd.sub_status, dd.inclusive_of_vat_yes_or_no, dd.buyer_type, dd.finance_type, dd.status,CAST(dd.deal_price_aed AS FLOAT), CAST(dd.deposit_aed AS FLOAT), CAST(dd.total_earned_commission_aed AS FLOAT),CAST(dd.gross_commission_aed AS FLOAT), 9, to_timestamp(dd.created_date_and_time, 'MM/DD/YY hh24:mi'),NULL, to_timestamp(dd.last_updated_date_and_time, 'MM/DD/YY hh24:mi') FROM deal_temp as dd;"

psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set estimated_date=null where estimated_date='0001-01-01 BC';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set actual_date=null where actual_date='0001-01-01 BC';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set tenancy_contract_start_date=null where tenancy_contract_start_date='0001-01-01 BC';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set tenancy_renewal_date=null where tenancy_renewal_date='0001-01-01 BC';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set create_date=null where create_date='0001-01-01 BC';"
psql -U postgres -d crm.asteco_crm_latest -c "update deal_deal set write_date=null where write_date='0001-01-01 BC';"

-- CREATE OR REPLACE FUNCTION isnumeric(text) RETURNS BOOLEAN AS $$
-- DECLARE x NUMERIC;
-- BEGIN
--     x = $1::NUMERIC;
--     RETURN TRUE;
-- EXCEPTION WHEN others THEN
--     RETURN FALSE;
-- END;
-- $$
-- STRICT
-- LANGUAGE plpgsql IMMUTABLE;

/*---uodate listing_id---*/
-- UPDATE deal_deal dd
-- SET    listing_id = ll.id
-- FROM   deal_temp  dt
-- JOIN   listing_listing ll ON trim(ll.ref_name) = trim(dt.listing_ref)
-- WHERE  dd.name = dt.reference;
psql -U postgres -d crm.asteco_crm_latest -c "UPDATE deal_deal dd SET listing_id = ll.id FROM deal_temp dt JOIN listing_listing ll ON trim(ll.ref_name) = trim(dt.listing_ref) WHERE dd.name = dt.reference;"

/*---uodate lead_id---*/
-- UPDATE deal_deal dd
-- SET    lead_id = ll.id
-- FROM   deal_temp  dt
-- JOIN   atk_lead_lead ll ON trim(ll.name) = trim(dt.lead_ref)
-- WHERE  dd.name = dt.reference;
psql -U postgres -d crm.asteco_crm_latest -c "UPDATE deal_deal dd SET    lead_id = ll.id FROM   deal_temp  dt JOIN   atk_lead_lead ll ON trim(ll.name) = trim(dt.lead_ref) WHERE  dd.name = dt.reference;"

/*---uodate cheque_id---*/
-- update deal_temp set cheques = concat(cheques,' Cheque') where isnumeric(cheques);
-- UPDATE deal_deal dd
-- SET    cheque_id = ll.id
-- FROM   deal_temp  dt
-- JOIN   number_of_cheque ll ON trim(ll.name) = trim(dt.cheques)
-- WHERE  dd.name = dt.reference;

/*---uodate write_uid---*/
-- UPDATE deal_deal iw
-- SET    write_uid=iv.id
-- FROM   deal_temp  iwvs
-- JOIN   (select rp.name,ru.id,ru.company_id 
-- from res_partner rp
-- join res_users ru
-- on ru.partner_id=rp.id) iv ON trim(lower(iv.name)) = trim(lower(iwvs.last_updated_by)) and iv.company_id = iwvs.company_id
-- WHERE  iw.name = iwvs.reference;
psql -U postgres -d crm.asteco_crm_latest -c "UPDATE deal_deal iw SET    write_uid=iv.id FROM   deal_temp  iwvs JOIN   (select rp.name,ru.id,ru.company_id from res_partner rp join res_users ru on ru.partner_id=rp.id) iv ON trim(lower(iv.name)) = trim(lower(iwvs.last_updated_by)) and iv.company_id = iwvs.company_id WHERE  iw.name = iwvs.reference;"

/*---uodate notes---*/
-- INSERT INTO crm_notes(deal_id,name,create_uid,create_date,write_uid,write_date)
-- SELECT rp.id,ct.notes,9,CURRENT_TIMESTAMP,rp.write_uid,CURRENT_TIMESTAMP FROM deal_temp as ct
-- join deal_deal rp
-- on rp.name=ct.reference
-- where ct.notes is not null;
psql -U postgres -d crm.asteco_crm_latest -c "INSERT INTO crm_notes(deal_id,name,create_uid,create_date,write_uid,write_date) SELECT rp.id,ct.notes,9,CURRENT_TIMESTAMP,rp.write_uid,CURRENT_TIMESTAMP FROM deal_temp as ct join deal_deal rp on rp.name=ct.reference where ct.notes is not null;"
