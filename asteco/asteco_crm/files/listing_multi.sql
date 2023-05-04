delete from listing_temp where status = 'Status';

alter table listing_temp add company_id integer;


select distinct LEFT(reference, 3) from listing_temp;

update listing_temp set company_id = 11 where LEFT(reference, 3) = 'ASB';
update listing_temp set company_id = 4 where LEFT(reference, 3) = 'HUT';
update listing_temp set company_id = 8 where LEFT(reference, 2) = 'PC';
update listing_temp set company_id = 6 where LEFT(reference, 3) = 'ASA';
update listing_temp set company_id = 10 where LEFT(reference, 3) = 'AMS';
update listing_temp set company_id = 7 where LEFT(reference, 3) = 'APM';
update listing_temp set company_id = 5 where LEFT(reference, 3) = 'AAR';
update listing_temp set company_id = 9 where LEFT(reference, 3) = 'ACO';


update listing_temp set listing_type='Sale' where listing_type='Sales';
update listing_temp set featured='true' where featured='Yes';
update listing_temp set featured='false' where featured='No';
update listing_temp set property_tenanted='true' where property_tenanted='Yes';
update listing_temp set property_tenanted='false' where property_tenanted='No';
update listing_temp set furnished=lower(furnished);
update listing_temp set category='Town House' where category='Townhouse';
update listing_temp set category='Staff Accomodation' where category='Staff Accommodation';
update listing_temp set bed=concat(bed,' Bed')
update listing_temp set cheques=concat(cheques,' Cheque')


INSERT INTO public.listing_listing (
	available_date, ref_name, unit, 
	listing_detail_type, street, floor, plot_area, property_view, 
	name, consumer_number, str, key_location, 
	regulatory_permit, description, 
	build_up_area_sqf, price, 
	price_per_sqft, commission_amount, 
	deposit_amount, maintenance_fee, listing_type, 
	listing_status, listing_region, is_featured, is_property_tenanted, 	
	furnished_id, 	
	customer_id, agent_id, visibility_id, category_id, 
	bed_id, fitted_id, bath_id, emirate_id, country_id, location_id, sub_location_id, 
	no_of_cheques, property_status_id, listing_source_id, 	
	managed_status_id, company_id, list_write_date, list_write_uid, active, 	
	create_date)
	
select to_timestamp(lt.available_from, 'MM-DD-YYYY hh24:mi'),reference,unit,
lt.type,street,lt.floor,plot_area,listing_view,
title,consumer,str,key_location,
rera_permit_no,description,
CAST(build_up_area_sqft AS FLOAT),
REPLACE(price, ',', '')::numeric,
REPLACE(price_per_sqft, ',', '')::numeric,
REPLACE(commission, ',', '')::numeric,
REPLACE(deposit, ',', '')::numeric, 
REPLACE(maintenance_fee, ',', '')::numeric, listing_type,
status,listing_region,CAST(featured AS BOOLEAN),CAST(property_tenanted AS BOOLEAN),
furnished,
NULL,NULL,NULL,NULL,
NULL,NULL,NULL,NULL,NULL,NULL,NULL,
NULL,NULL,NULL,
NULL,lt.company_id,to_timestamp(lt.last_updated_date_and_time, 'MM-DD-YYYY hh24:mi'),1,TRUE,
to_timestamp(lt.created_date_and_time, 'MM-DD-YYYY hh24:mi')
from listing_temp lt;

/*update idd */
UPDATE listing_listing iw
SET    isd_code_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_country_code iv ON trim(iv.country_code) = trim(iwvs.idd)
WHERE  iw.ref_name = iwvs.reference;

/* update customer */
UPDATE listing_listing iw
SET    customer_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_partner iv ON trim(lower(iv.name)) = trim(lower(iwvs.contact)) and iv.company_id = iwvs.company_id
WHERE  iw.ref_name = iwvs.reference;
														   
/* update agent*/
UPDATE listing_listing iw
SET    agent_id = iv.id
FROM   listing_temp  iwvs
JOIN   hr_employee iv ON trim(lower(iv.name)) = trim(lower(iwvs.assigned_to)) and iv.company_id = iwvs.company_id
WHERE  iw.ref_name = iwvs.reference;

/* update visibility*/
UPDATE listing_listing iw
SET    visibility_id = iv.id
FROM   listing_temp  iwvs
JOIN   listing_visibility iv ON trim(lower(iv.name)) = trim(lower(iwvs.visibility))
WHERE  iw.ref_name = iwvs.reference;
																  
/* update category*/															  
UPDATE listing_listing iw
SET    category_id = iv.id
FROM   listing_temp  iwvs
JOIN   listing_category iv ON trim(lower(iv.name)) = trim(lower(iwvs.category))
WHERE  iw.ref_name = iwvs.reference;	
																
update listing_listing set is_office=true where category_id in (3,4,6);
																
/* update bed*/															  
UPDATE listing_listing iw
SET    bed_id = iv.id
FROM   listing_temp  iwvs
JOIN   listing_bed iv ON trim(lower(iv.name)) = trim(lower(iwvs.bed))
WHERE  iw.ref_name = iwvs.reference;																	
																
/* update fitted id*/															  
UPDATE listing_listing iw
SET    fitted_id = iv.id
FROM   listing_temp  iwvs
JOIN   listing_fitted iv ON trim(lower(iv.name)) = trim(lower(iwvs.fitted))
WHERE  iw.ref_name = iwvs.reference;
															  
/* update bath id*/															  
UPDATE listing_listing iw
SET    bath_id = iv.id
FROM   listing_temp  iwvs
JOIN   listing_bath iv ON trim(lower(iv.name)) = trim(lower(iwvs.bath))
WHERE  iw.ref_name = iwvs.reference;	
	
/*update emirates/city*/
UPDATE listing_listing iw
SET    emirate_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_country_state iv ON trim(lower(iv.name)) = trim(lower(iwvs.emirate))
WHERE  iw.ref_name = iwvs.reference;	
																 
select distinct listing_location from listing_temp 
where trim(lower(listing_location)) not in (select trim(lower(name)) from res_location); 

/* inserted new location with emairate id 1*/
insert into res_location(name,emirate_id,create_uid,create_date,write_uid,write_date)
select distinct lt.listing_location,1,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from listing_temp lt
where lt.listing_location not in (select name from res_location);
/*update emirates in location table*/
UPDATE res_location iw
SET    emirate_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_country_state iv ON trim(lower(iv.name)) = trim(lower(iwvs.emirate))
WHERE  trim(lower(iw.name)) = trim(lower(iwvs.listing_location))
and emirate_id=1;
										 
/* inserted new sub location with location id 1*/
insert into res_sub_location(name,location_id,create_uid,create_date,write_uid,write_date)
select distinct lt.sub_location,1,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from listing_temp lt
where trim(lower(lt.sub_location)) not in (select trim(lower(name)) from res_sub_location);
/*update emirates in location table*/
UPDATE res_sub_location iw
SET    location_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.listing_location))
WHERE  trim(lower(iw.name)) = trim(lower(iwvs.sub_location))
and location_id=1;

/*update location*/
UPDATE listing_listing iw
SET    location_id = iv.id
FROM   listing_temp  iwvs
JOIN   res_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.listing_location))
WHERE  iw.ref_name = iwvs.reference;

/*update sub location*/
UPDATE listing_listing iw
SET    sub_location_id= iv.id
FROM   listing_temp  iwvs
JOIN   res_sub_location iv ON trim(lower(iv.name)) = trim(lower(iwvs.sub_location))
WHERE  iw.ref_name = iwvs.reference;										 

/* update cheque*/															  
UPDATE listing_listing iw
SET    no_of_cheques = iv.id
FROM   listing_temp  iwvs
JOIN   number_of_cheque iv ON trim(lower(iv.name)) = trim(lower(iwvs.cheques))
WHERE  iw.ref_name = iwvs.reference;

/* update property_status*/																
select distinct property_status from listing_temp 
where trim(lower(property_status)) not in (select trim(lower(name)) from listing_property_status); 

INSERT INTO public.listing_property_status(
	name, create_uid, create_date, write_uid, write_date)
	select distinct lt.property_status,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from listing_temp lt
where trim(lower(lt.property_status)) not in (select trim(lower(name)) from listing_property_status);
														  
/*update property_status*/
UPDATE listing_listing iw
SET    property_status_id= iv.id
FROM   listing_temp  iwvs
JOIN   listing_property_status iv ON trim(lower(iv.name)) = trim(lower(iwvs.property_status))
WHERE  iw.ref_name = iwvs.reference;

/* update listing source*/																
select distinct source_of_listing from listing_temp 
where trim(lower(source_of_listing)) not in (select trim(lower(name)) from source_master);
														 
INSERT INTO public.source_master(
	name, create_uid, create_date, write_uid, write_date)
	select distinct lt.source_of_listing,1,CURRENT_TIMESTAMP,1,CURRENT_TIMESTAMP from listing_temp lt
where trim(lower(lt.source_of_listing)) not in (select trim(lower(name)) from source_master);	

/*update listing source*/
UPDATE listing_listing iw
SET    listing_source_id= iv.id
FROM   listing_temp  iwvs
JOIN   source_master iv ON trim(lower(iv.name)) = trim(lower(iwvs.source_of_listing))
WHERE  iw.ref_name = iwvs.reference;

/*update managed status*/
UPDATE listing_listing iw
SET    managed_status_id= iv.id
FROM   listing_temp  iwvs
JOIN   listing_managed_status iv ON trim(lower(iv.name)) = trim(lower(iwvs.managed_status))
WHERE  iw.ref_name = iwvs.reference;

/*update users*/
UPDATE listing_listing iw
SET    create_uid = iv.id, list_write_uid=iv.id, write_uid=iv.id
FROM   listing_temp  iwvs
JOIN   (select rp.name,ru.id,ru.company_id
from res_partner rp
join res_users ru
on ru.partner_id=rp.id) iv ON trim(lower(iv.name)) = trim(lower(iwvs.created_by)) and iv.company_id = iwvs.company_id
WHERE  iw.ref_name = iwvs.reference;

INSERT INTO crm_notes(listing_id,name,create_uid,create_date,write_uid,write_date)
SELECT rp.id,ct.notes,rp.list_write_uid,CURRENT_TIMESTAMP,rp.list_write_uid,CURRENT_TIMESTAMP FROM listing_temp as ct
join listing_listing rp
on rp.ref_name=ct.reference
where ct.notes is not null;

update listing_listing set create_uid = 9, write_uid = 9, list_write_uid = 9 where create_uid is null and company_id = 3;

	update listing_listing set agent_id = 5 where agent_id is null and company_id = 3;