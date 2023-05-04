INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,type,country_id,email,
mobile,is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,contact_type,head,ref_name,
city_id,source,isd_code_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)

SELECT ct.full_name,1,ct.full_name,'en_US',
'TRUE','TRUE','FALSE','FALSE','contact',2,ct.email,
ct.mobile,'FALSE',0,'TRUE',NULL, to_timestamp(ct.created_date_and_time, 'DD-MM-YY hh24:mi'),
1,to_timestamp(ct.last_updated_date_and_time, 'DD-MM-YY hh24:mi'),0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message',ct.contact_type,'individual',ct.ref,
NULL,NULL,NULL,'FALSE','FALSE','FALSE','TRUE' FROM contacts_temp as ct;

/*update source*/
UPDATE res_partner iw
SET    source = iv.id
FROM   contacts_temp  iwvs
JOIN   source_master iv ON iv.name = iwvs.source
WHERE  iw.ref_name = iwvs.ref;

/*update users*/
UPDATE res_partner iw
SET    create_uid = iv.id
FROM   contacts_temp  iwvs
JOIN   (select rp.name,ru.id 
from res_partner rp
join res_users ru
on ru.partner_id=rp.id) iv ON iv.name = iwvs.created_by
WHERE  iw.ref_name = iwvs.ref;

/*convert contact type to lowercase to satisfy selection field*/
update res_partner set contact_type = lower(contact_type);

/*update emirates/city*/
UPDATE res_partner iw
SET    city_id = iv.id
FROM   contacts_temp  iwvs
JOIN   res_country_state iv ON iv.name = iwvs.emirate_or_city
WHERE  iw.ref_name = iwvs.ref;

/*update idd */
UPDATE res_partner iw
SET    isd_code_id = iv.id
FROM   contacts_temp  iwvs
JOIN   res_country_code iv ON iv.country_name = iwvs.country
WHERE  iw.ref_name = iwvs.ref;

/*insert notes into notes table */
INSERT INTO crm_notes(partner_id,name,create_uid,create_date,write_uid,write_date)
SELECT rp.id,ct.notes,41,CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP FROM contacts_temp as ct
join res_partner rp
on rp.ref_name=ct.ref
where ct.notes is not null;

/* set updated by with created by */
update res_partner set write_uid = create_uid ;
update res_partner set write_uid = 41 where write_uid is null ;
update res_partner set create_uid = 41 where create_uid is null ;


/* clean up garbage - contact*/
update contacts_temp set created_date_and_time = NULL
where created_date_and_time= '--';

update contacts_temp set contact_type = 'private'
where contact_type is NULL;

update contacts_temp set full_name = email
where full_name is NULL;

update contacts_temp set full_name = ref
where full_name is NULL;

select * from contacts_temp ct where ct.full_name is null;

select * from res_partner where created_date;



update res_partner set create_date= write_date where is_contact=true ;

select * from contacts_temp where created_date_and_time like '%50239%';

update contacts_temp set created_date_and_time = last_updated_date_and_time where created_date_and_time like '%50239%';

/* clean up garbage - contact*/


/*-------------------- Loading Leads ------------------------*/

/*update status field in temp table*/
update leads_temp set status='new' where status='New';
update leads_temp set status='work_Progress' where status='Work In Progress';
update leads_temp set status='closed' where status='Closed';

update leads_temp set lead_type=lower(lead_type);
update leads_temp set lead_type='land_lord' where lead_type='landlord';

update leads_temp set hot='yes' where hot='Hot Lead';
update leads_temp set priority=lower(priority);

update leads_temp set assigned_to='Asteco AUH' where assigned_to='Asteco  AUH';

update leads_temp set created_date_and_time = NULL
where created_date_and_time= '--';

/* Initial insertion of leads */

INSERT INTO atk_lead_lead(state, name, lead_type, contact_id, 
    auto_assign, lead_source_id, sub_status_id,
    is_hot_lead, agent_id, priority, user_uid, company_id)
SELECT lt.status, lt.reference, lt.lead_type, 1,
    'FALSE', 1, NULL,
    lt.hot, NULL, lt.priority, 1, 3 FROM leads_temp as lt;

/* update contact */
UPDATE atk_lead_lead iw
SET    contact_id = iv.id
FROM   leads_temp  iwvs
JOIN   res_partner iv ON lower(iv.name) = lower(iwvs.contact)
WHERE  iw.name = iwvs.reference;

/* update source */
insert into source_master(name)
select distinct trim(lt.lead_source) from leads_temp lt
where trim(lt.lead_source) not in (select name from source_master);

UPDATE atk_lead_lead iw
SET    lead_source_id = iv.id
FROM   leads_temp  iwvs
JOIN   source_master iv ON trim(lower(iv.name)) = trim(lower(iwvs.lead_source))
WHERE  iw.name = iwvs.reference;

/*update users*/
UPDATE atk_lead_lead iw
SET    create_uid = iv.id, user_uid = iv.id, write_uid = iv.id, lead_write_uid = iv.id
FROM   leads_temp  iwvs
JOIN   (select rp.name,ru.id 
from res_partner rp
join res_users ru
on ru.partner_id=rp.id) iv ON iv.name = iwvs.created_by
WHERE  iw.name = iwvs.reference;

/* update sub status */
UPDATE atk_lead_lead iw
SET    sub_status_id = iv.id
FROM   leads_temp  iwvs
JOIN   lead_sub_status iv ON trim(lower(iv.name)) = trim(lower(iwvs.pre_qualified_status))
WHERE  iw.name = iwvs.reference;

/* update assigned to */
UPDATE atk_lead_lead iw
SET    agent_id = iv.id
FROM   leads_temp  iwvs
JOIN   hr_employee iv ON trim(lower(iv.name)) = trim(lower(iwvs.assigned_to))
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

UPDATE atk_lead_lead iw
SET    create_date = CURRENT_TIMESTAMP, 
write_date = CURRENT_TIMESTAMP,
lead_write_date = CURRENT_TIMESTAMP
FROM   leads_temp  iwvs
WHERE  iw.name = iwvs.reference;

/*insert notes into notes table */
INSERT INTO crm_notes(lead_id,name,create_uid,create_date,write_uid,write_date)
SELECT rp.id,ct.notes,41,CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP FROM leads_temp as ct
join atk_lead_lead rp
on rp.name=ct.reference
where ct.notes is not null;

/*created date replaced with current date */
update atk_lead_lead set create_date = write_date;

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
CAST(bua_min AS FLOAT),CAST(bua_max AS FLOAT),null,null,CAST(min_price AS FLOAT),CAST(max_price AS FLOAT),3,41,
CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP
 from leads_temp; 

/*update lead requirement */
UPDATE atk_lead_requirement iw
SET    lead_id = iwvs.id,category_id=iwvs.category_id_list,emirate_id=emirate_id_list,
location_id=location_id_list,sub_location_id=sub_location_id_list
FROM   atk_lead_lead  iwvs
WHERE  iw.ref_req = iwvs.name;


/******************FOR HAXXON**********************/
UPDATE atk_lead_requirement iw
SET    lead_id = iwvs.id,category_id=iwvs.category_id_list,emirate_id=emirate_id_list,
location_id=location_id_list,sub_location_id=sub_location_id_list
FROM   atk_lead_lead  iwvs
WHERE  iw.ref_req = iwvs.name and iw.ref_req like 'HAX%';


/*-------------------- Loading Listing ------------------------*/


/*--------------------NOTES UPDATION------------------------*/

INSERT INTO crm_notes(listing_id,name,create_uid,create_date,write_uid,write_date)
SELECT rp.id,ct.notes,41,CURRENT_TIMESTAMP,41,CURRENT_TIMESTAMP FROM listing_temp as ct
join listing_listing rp
on rp.ref_name=ct.reference
where ct.notes is not null;

UPDATE crm_notes iw
SET    create_uid = iwvs.create_uid, create_date = iwvs.create_date, write_uid = iwvs.list_write_uid,
write_date = iwvs.list_write_date
FROM   listing_listing  iwvs
WHERE  iw.listing_id = iwvs.id;

UPDATE crm_notes iw
SET    create_uid = iwvs.create_uid, create_date = iwvs.create_date, write_uid = iwvs.lead_write_uid,
write_date = iwvs.lead_write_date
FROM   atk_lead_lead  iwvs
WHERE  iw.lead_id = iwvs.id;

UPDATE crm_notes iw
SET    create_uid = iwvs.create_uid, create_date = iwvs.create_date, write_uid = iwvs.write_uid,
write_date = iwvs.write_date
FROM   res_partner  iwvs
WHERE  iw.partner_id = iwvs.id;



