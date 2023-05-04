CREATE TABLE public.leads_temp
(
  reference text,
  lead_type text,
  status text,
  pre_qualified_status text,
  opportunity_stage text,
  reason_for_loss text,
  priority text,
  hot text,
  contact text,
  company_name text,
  idd text,
  mobile text,
  phone_home text,
  email text,
  category text,
  emirate text,
  location text,
  sub_location text,
  unit_type text,
  unit_no text,
  bed text,
  min_price text,
  max_price text,
  bua_min text,
  bua_max text,
  offered_units text,
  lead_source text,
  assigned_to text,
  created_by text,
  created_date_and_time text,
  last_updated_date_and_time text,
  country text,
  notes text
)

delete from leads_temp where status = 'Status';

/*update status field in temp table*/
update leads_temp set status='new' where status='New';
update leads_temp set status='work_Progress' where status='Work In Progress';
update leads_temp set status='closed' where status='Closed';

update leads_temp set lead_type=lower(lead_type);
update leads_temp set lead_type='land_lord' where lead_type='landlord';

update leads_temp set hot='yes' where hot='Hot Lead';
update leads_temp set priority=lower(priority);

update leads_temp set created_date_and_time = NULL
where created_date_and_time= '--';


alter table leads_temp add company_id integer;

select distinct LEFT(reference, 3) from leads_temp;

update leads_temp set company_id = 4 where LEFT(reference, 3) = 'HUT';
update leads_temp set company_id = 8 where LEFT(reference, 2) = 'PC';
update leads_temp set company_id = 6 where LEFT(reference, 3) = 'ASA';
update leads_temp set company_id = 10 where LEFT(reference, 3) = 'AMS';
update leads_temp set company_id = 7 where LEFT(reference, 3) = 'APM';
update leads_temp set company_id = 5 where LEFT(reference, 3) = 'AAR';
update leads_temp set company_id = 9 where LEFT(reference, 3) = 'ACO';




/* Initial insertion of leads */

INSERT INTO atk_lead_lead(state, name, lead_type, contact_id, 
    auto_assign, lead_source_id, sub_status_id,
    is_hot_lead, agent_id, priority, user_uid, company_id)
SELECT lt.status, lt.reference, lt.lead_type, 1,
    'FALSE', 1, NULL,
    lt.hot, NULL, lt.priority, 1, lt.company_id FROM leads_temp as lt;

/* update source */
insert into source_master(name)
select distinct trim(lt.lead_source) from leads_temp lt
where trim(lt.lead_source) not in (select name from source_master);

UPDATE atk_lead_lead iw
SET    lead_source_id = iv.id
FROM   leads_temp  iwvs
JOIN   source_master iv ON trim(lower(iv.name)) = trim(lower(iwvs.lead_source))
WHERE  iw.name = iwvs.reference;


/* update sub status */
UPDATE atk_lead_lead iw
SET    sub_status_id = iv.id
FROM   leads_temp  iwvs
JOIN   lead_sub_status iv ON trim(lower(iv.name)) = trim(lower(iwvs.pre_qualified_status))
WHERE  iw.name = iwvs.reference;

/* update reason for loss */
UPDATE atk_lead_lead iw
SET    loss_reason = iv.id
FROM   leads_temp  iwvs
JOIN   loss_reason iv ON trim(lower(iv.name)) = trim(lower(iwvs.reason_for_loss))
WHERE  iw.name = iwvs.reference;

/* update category */
UPDATE atk_lead_lead iw
SET    category_id_list = iv.id
FROM   leads_temp  iwvs
JOIN   listing_category iv ON trim(lower(iv.name)) = trim(lower(iwvs.category))
WHERE  iw.name = iwvs.reference;

/*update emirates/city*/
UPDATE atk_lead_lead iw
SET    emirate_id_list = iv.id
FROM   leads_temp  iwvs
JOIN   res_country_state iv ON trim(lower(iv.name)) = trim(lower(iwvs.emirate))
WHERE  iw.name = iwvs.reference;

/* inserted new location with emairate id 1*/
insert into res_location(name,emirate_id,create_uid,create_date,write_uid,write_date)
select distinct lt.location,1,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from leads_temp lt
where lt.location not in (select name from res_location);
/*update emirates in location table*/
UPDATE res_location iw
SET    emirate_id = iv.id
FROM   leads_temp  iwvs
JOIN   res_country_state iv ON trim(lower(iv.name)) = trim(lower(iwvs.emirate))
WHERE  trim(lower(iw.name)) = trim(lower(iwvs.location))
and emirate_id=1;

/* inserted new sub location with location id 1*/
insert into res_sub_location(name,location_id,create_uid,create_date,write_uid,write_date)
select distinct lt.sub_location,1,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from leads_temp lt
where lt.sub_location not in (select name from res_sub_location);
/*update emirates in location table*/
UPDATE res_sub_location iw
SET    location_id = iv.id
FROM   leads_temp  iwvs
JOIN   res_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.location))
WHERE  trim(lower(iw.name)) = trim(lower(iwvs.sub_location))
and location_id=1;

/*update location*/
UPDATE atk_lead_lead iw
SET    location_id_list = iv.id
FROM   leads_temp  iwvs
JOIN   res_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.location))
WHERE  iw.name = iwvs.reference;

/*update sub location*/
UPDATE atk_lead_lead iw
SET    sub_location_id_list = iv.id
FROM   leads_temp  iwvs
JOIN   res_sub_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.sub_location))
WHERE  iw.name = iwvs.reference;

/*update created & updated date*/
UPDATE atk_lead_lead iw
SET    create_date = to_timestamp(iwvs.created_date_and_time, 'MM-DD-YY hh24:mi'), 
write_date = to_timestamp(iwvs.last_updated_date_and_time, 'MM-DD-YY hh24:mi'),
lead_write_date = to_timestamp(iwvs.last_updated_date_and_time, 'MM-DD-YY hh24:mi')
FROM   leads_temp  iwvs
WHERE  iw.name = iwvs.reference;

/*insert notes into notes table */
INSERT INTO crm_notes(lead_id,name,create_uid,create_date,write_uid,write_date)
SELECT rp.id,ct.notes,41,CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP FROM leads_temp as ct
join atk_lead_lead rp
on rp.name=ct.reference
where ct.notes is not null;

/*update idd */
UPDATE atk_lead_lead iw
SET    isd_code_id = iv.id
FROM   leads_temp  iwvs
JOIN   res_country_code iv ON iv.country_name = iwvs.country
WHERE  iw.name = iwvs.reference;

select * from atk_lead_requirement

/*insert lead requirement */
INSERT INTO atk_lead_requirement(ref_req,category_id,emirate_id,country_id,location_id,sub_location_id,bed_id,
  min_bua,max_bua,lead_id,list_id,min_price,max_price,company_id,create_uid,
  create_date,write_uid,write_date)
select  reference,null,null,null,null,null,null,
CAST(bua_min AS FLOAT),CAST(bua_max AS FLOAT),null,null,CAST(min_price AS FLOAT),CAST(max_price AS FLOAT),company_id,41,
CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP
 from leads_temp; 

/*update lead requirement */
UPDATE atk_lead_requirement iw
SET    lead_id = iwvs.id,category_id=iwvs.category_id_list,emirate_id=emirate_id_list,
location_id=location_id_list,sub_location_id=sub_location_id_list
FROM   atk_lead_lead  iwvs
WHERE  iw.ref_req = iwvs.name and iw.ref_req not like all(array['HAX%','AST%']);

/* update contact */
UPDATE atk_lead_lead iw
SET    contact_id = iv.id
FROM   leads_temp  iwvs
JOIN   res_partner iv ON lower(iv.name) = lower(iwvs.contact) and iv.company_id = iwvs.company_id
WHERE  iw.name = iwvs.reference;

/*update users*/
UPDATE atk_lead_lead iw
SET    create_uid = iv.id, user_uid = iv.id, write_uid = iv.id, lead_write_uid = iv.id
FROM   leads_temp  iwvs
JOIN   (select rp.name,ru.id,ru.company_id
from res_partner rp
join res_users ru
on ru.partner_id=rp.id) iv ON iv.name = iwvs.created_by and iv.company_id = iwvs.company_id 
WHERE  iw.name = iwvs.reference;

/* update assigned to */
UPDATE atk_lead_lead iw
SET    agent_id = iv.id
FROM   leads_temp  iwvs
JOIN   hr_employee iv ON trim(lower(iv.name)) = trim(lower(iwvs.assigned_to)) and iv.company_id = iwvs.company_id
WHERE  iw.name = iwvs.reference;