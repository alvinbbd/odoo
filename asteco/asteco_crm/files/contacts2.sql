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
'no-message','no-message','within_company',lower(ct.type),ct.ref,
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

select count(*) from contacts_temp

select * from res_partner where is_contact = true and ref_name='AST-C-121591'
select * from res_partner where is_contact = true and id=120674

/* set updated by with created by */
update res_partner set write_uid = create_uid where is_contact = true and id>120673;
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


/* clean up garbage - contact*/


/*----------------- Contacts Multi-company --------------------*/

INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,type,country_id,email,
mobile,is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,contact_type,head,ref_name,
city_id,source,isd_code_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)

SELECT ct.full_name,3,ct.full_name,'en_US',
'TRUE','TRUE','FALSE','FALSE','contact',2,ct.email,
ct.mobile,'FALSE',0,'TRUE',NULL, to_timestamp(ct.created_date_and_time, 'MM-DD-YY hh24:mi'),
NULL,to_timestamp(ct.last_updated_date_and_time, 'MM-DD-YY hh24:mi'),0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message','within_company',lower(ct.type),ct.ref,
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






/*-------------------------------------------------------*/
select id, ref_name from res_partner where ref_name like 'HAX%' order by id asc;

update res_partner set write_uid = create_uid where id > 121258;

select * from res_partner where name like 'Nilesh Ranpura';121215
select * from res_users where partner_id = 121215;72


select * from res_partner where create_uid is NULL;

update atk_lead_lead set  create_uid = 72 where create_uid is NULL and name like 'HAX%';
update atk_lead_lead set  write_uid = 72 where write_uid is NULL and name like 'HAX%';
update atk_lead_lead set  lead_write_uid = 72 where lead_write_uid is NULL and name like 'HAX%';




/*--------------------------CONTACTS MULTI-COMPANY-----------------------------*/

delete from contacts_temp where title = 'Title';

alter table contacts_temp add company_id text;

select distinct LEFT(ref, 3) from contacts_temp;

update contacts_temp set company_id = 4 where LEFT(ref, 3) = 'HUT';
update contacts_temp set company_id = 8 where LEFT(ref, 2) = 'PC';
update contacts_temp set company_id = 6 where LEFT(ref, 3) = 'ASA';
update contacts_temp set company_id = 11 where LEFT(ref, 3) = 'ASB';
update contacts_temp set company_id = 10 where LEFT(ref, 3) = 'AMS';
update contacts_temp set company_id = 7 where LEFT(ref, 3) = 'APM';
update contacts_temp set company_id = 5 where LEFT(ref, 3) = 'AAR';
update contacts_temp set company_id = 9 where LEFT(ref, 3) = 'ACO';

INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,type,country_id,email,
mobile,is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,contact_type,head,ref_name,
city_id,source,isd_code_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)

SELECT ct.full_name,cast(ct.company_id as integer),ct.full_name,'en_US',
'TRUE','TRUE','FALSE','FALSE','contact',2,ct.email,
ct.mobile,'FALSE',0,'TRUE',NULL, to_timestamp(ct.created_date_and_time, 'MM-DD-YY hh24:mi'),
NULL,to_timestamp(ct.last_updated_date_and_time, 'MM-DD-YY hh24:mi'),0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message','within_company',lower(ct.type),ct.ref,
NULL,NULL,NULL,'FALSE','FALSE','FALSE','TRUE' FROM contacts_temp as ct;

select distinct country from contacts_temp;
select count(*) from contacts_temp where country = 'Jordan';

select distinct emirate_or_city from contacts_temp;
select count(*) from contacts_temp where emirate_or_city = 'Amman';


/*update country*/
UPDATE res_partner iw
SET    country_id = iv.id
FROM   contacts_temp  iwvs
JOIN   res_country iv ON iv.name = iwvs.country
WHERE  iw.ref_name = iwvs.ref;

/*update source*/
UPDATE res_partner iw
SET    source = iv.id
FROM   contacts_temp  iwvs
JOIN   source_master iv ON iv.name = iwvs.source
WHERE  iw.ref_name = iwvs.ref;

/*update users*/
select distinct created_by from contacts_temp  where created_by not in
(select distinct name from res_partner where is_contact = False);

select distinct company_id from contacts_temp where created_by = ;
select name from res_company where id = ;

UPDATE res_partner iw
SET    create_uid = iv.id, write_uid = iv.id
FROM   contacts_temp  iwvs
JOIN   (select rp.name,ru.id,ru.company_id 
from res_partner rp
join res_users ru
on ru.partner_id=rp.id) iv ON trim(iv.name) = trim(iwvs.created_by) and iv.company_id = CAST (iwvs.company_id AS integer)
WHERE  iw.ref_name = iwvs.ref;

-- UPDATE res_partner iw
-- SET    create_uid = iv.id, write_uid = iv.id
-- FROM   contacts_temp  iwvs
-- JOIN   (select rp.name,ru.id
-- from res_partner rp
-- join res_users ru
-- on ru.partner_id=rp.id) iv ON iv.name = iwvs.created_by
-- WHERE  iw.ref_name = iwvs.ref;

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