###### CONTACTS #####


INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,type,country_id,email,
mobile,is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,contact_type,head,title,ref_name,
city_id,source,isd_code_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)
SELECT sdc.name,1,sdc.name,'en_US',
'TRUE','TRUE','FALSE','FALSE','contact',2,sdc.email,
sdc.mobile,'FALSE',0,'TRUE',sdc.uid, CURRENT_TIMESTAMP,
1,CURRENT_TIMESTAMP,0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message','private','individual','mr',sdc.ref,
548,1,235,'FALSE','FALSE','FALSE','TRUE' FROM sample_data_contact as sdc;



create temp table temp_table as 
select u.id,rp.name from res_users as u join res_partner as rp on u.partner_id = rp.id
join sample_data_contact on sample_data_contact.created_by = rp.name;

select * from temp_table;


update res_partner set create_uid = x.id from res_partner as rp
right join sample_data_contact on rp.name = sample_data_contact.name
right join (select u.id,rp.name from res_users as u join temp_table as rp on u.partner_id = rp.id)x 
on x.name = sample_data_contact.created_by;


###### LEADS #####


INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,type,country_id,email,
mobile,is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,contact_type,head,title,
city_id,source,isd_code_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)
SELECT sdl.contact_name,1,sdl.contact_name,'en_US',
'TRUE','TRUE','FALSE','FALSE','contact',2,sdl.email,
sdl.mobile,'FALSE',0,'TRUE',1, CURRENT_TIMESTAMP,
1,CURRENT_TIMESTAMP,0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message','private','individual','mr',
548,1,235,'FALSE','FALSE','FALSE','FALSE' FROM sample_data_lead as sdl 
WHERE NOT EXISTS (
SELECT 1 FROM res_partner WHERE name = sdl.contact_name and email = sdl.email);


INSERT INTO res_partner(name,company_id,display_name,lang,
active,customer,supplier,employee,country_id,contact_type,
is_company,color,partner_share,create_uid,create_date,
write_uid,write_date,message_bounce,opt_out,calendar_last_notif_ack,
invoice_warn,sale_warn,
city_id,is_vip,is_link_to_contact,is_notify_agent,is_contact)
SELECT sdl.agent1,1,sdl.agent1,'en_US',
'TRUE','FALSE','FALSE','TRUE',2,'contact',
'FALSE',0,'TRUE',1, CURRENT_TIMESTAMP,
1,CURRENT_TIMESTAMP,0,'FALSE',CURRENT_TIMESTAMP,
'no-message','no-message',
548,'FALSE','FALSE','FALSE','FALSE' FROM sample_data_lead as sdl
WHERE NOT EXISTS (
SELECT 1 FROM res_partner WHERE name = sdl.agent1 and is_contact = 'FALSE');


INSERT INTO res_users(partner_id,user_type,user_status, agent_status,login,company_id,notification_type)
SELECT rp.id,1,'active','available',CONCAT(rp.name,CAST(rp.id AS text),'@test.com'),1,'email'
FROM res_partner as rp 
WHERE rp.is_contact = 'FALSE' and NOT EXISTS (
SELECT 1 FROM res_users WHERE partner_id = rp.id);

insert into resource_resource(name,active,company_id,resource_type,user_id,time_efficiency,calendar_id)
select rp.name,'TRUE',1,'user',u.id,100,1 from res_users as u join res_partner as rp on u.partner_id = rp.id;

INSERT INTO hr_employee(name,resource_id)
SELECT rr.name,rr.id from resource_resource as rr where NOT EXISTS (
SELECT 1 FROM hr_employee WHERE name = rr.name);





update sample_data_lead set type = '' where type = '0.0' or type = 'Landlord+Seller' or type = 'Not Specified';
update sample_data_lead set type = 'land_lord' where type = 'Landlord';
update sample_data_lead set type = lower(type);

update sample_data_lead set sub_status = lead_sub_status.id from lead_sub_status where lower(lead_sub_status.name) = lower(sample_data_lead.sub_status);
update sample_data_lead set sub_status = 5 where sub_status = 'Needs time';
update sample_data_lead set sub_status = '' where sub_status not in ('8','2','6','4','5','3','1');

update sample_data_lead set priority = lower(priority);

update sample_data_lead set hot = 'yes' where hot = 'Hot Lead';

update sample_data_lead set contact_name = res_partner.id from res_partner where res_partner.name = sample_data_lead.contact_name;

update sample_data_lead set mobile = replace(mobile,'.0','');

update sample_data_lead set category = listing_category.id from listing_category where listing_category.name = sample_data_lead.category;

update sample_data_lead set category = 16 where category = 'Townhouse';
update sample_data_lead set category = 25 where category = 'Staff Accommodation';
update sample_data_lead set category = '' where category = '0.0';


update sample_data_lead set emirate = res_country_state.id from res_country_state where res_country_state.name = sample_data_lead.emirate;

update sample_data_lead set location = res_location.id from res_location where lower(res_location.name) = lower(sample_data_lead.location);

update sample_data_lead set sub_location = res_sub_location.id from res_sub_location where lower(res_sub_location.name) = lower(sample_data_lead.sub_location);

update sample_data_lead set max_beds = replace(max_beds,'.0','');
update sample_data_lead set max_beds = concat(max_beds,' Bed');

update sample_data_lead set max_beds = listing_bed.id from listing_bed where listing_bed.name = sample_data_lead.max_beds;
update sample_data_lead set max_beds = '' where max_beds in ('0 Bed',' Bed','16 Bed');

update sample_data_lead set source = source_master.id from source_master where lower(source_master.name) = lower(sample_data_lead.source);
update sample_data_lead set source = 44 where source = 'Google ';
update sample_data_lead set source = 79 where source in ('Gulfpropertyportal.com','RC Referral','getthat.com',' Not Specified','OA Referral','Cityscape','Concierge And Security','Al Ayam','Concierge and Security','EDM- Propertyfinder.ae','Project website','Getthat.com','Paid Social Media Campaign','Google Ads','Online Chat');

update sample_data_lead set agent1 = hr_employee.id from hr_employee where lower(hr_employee.name) = lower(sample_data_lead.agent1);

update sample_data_lead set created_by = res_partner.id from res_partner where lower(res_partner.name) = lower(sample_data_lead.created_by);

update sample_data_lead set created_by = res_users.id from res_users where CAST(res_users.partner_id AS text) = sample_data_lead.created_by;



INSERT INTO atk_lead_lead(state, name, lead_type, contact_id, 
    auto_assign, lead_source_id, sub_status_id,
    is_hot_lead, agent_id, priority, user_uid, company_id)
SELECT 'new', sdl.ref, sdl.type, CAST(sdl.contact_name AS INTEGER),
    'FALSE', CAST(sdl.source AS INTEGER), CAST(sdl.sub_status AS INTEGER),
    sdl.hot, CAST(sdl.agent1 AS INTEGER), sdl.priority, 1, 1 FROM sample_data_lead as sdl;


CREATE OR REPLACE FUNCTION isnumeric(text) RETURNS BOOLEAN AS $$
DECLARE x NUMERIC;
BEGIN
x = $1::NUMERIC;
RETURN TRUE;
EXCEPTION WHEN others THEN
RETURN FALSE;
END;
$$
STRICT
LANGUAGE plpgsql IMMUTABLE;


INSERT INTO atk_lead_requirement(category_id, emirate_id, location_id, sub_location_id, bed_id, lead_id)
SELECT (case when isnumeric(category) then CAST(sdl.category AS INTEGER) end), (case when isnumeric(emirate) then CAST(sdl.emirate AS INTEGER) end),
 (case when isnumeric(location) then CAST(sdl.location AS INTEGER) end), (case when isnumeric(sub_location) then CAST(sdl.sub_location AS INTEGER) end),
(case when isnumeric(max_beds) then CAST(sdl.max_beds AS INTEGER) end) al.id FROM sample_data_lead as sdl join atk_lead_lead as al on sample_data_lead.ref = atk_lead_lead.name);

INSERT INTO atk_lead_requirement(category_id, emirate_id, location_id, sub_location_id, bed_id, lead_id)
SELECT (case when isnumeric(category) then CAST(sdl.category AS INTEGER) end), (case when isnumeric(emirate) then CAST(sdl.emirate AS INTEGER) end),
 (case when isnumeric(location) then CAST(sdl.location AS INTEGER) end), (case when isnumeric(sub_location) then CAST(sdl.sub_location AS INTEGER) end),
(case when isnumeric(max_beds) then CAST(sdl.max_beds AS INTEGER) end), al.id FROM sample_data_lead as sdl join atk_lead_lead as al on sdl.ref = al.name;


update sample_data_lead set category = 'NULL' where category = '0';





#########LISTING########

update sample_data_listing set status = 'Requested to Publish' where status = 'Waiting Approval';

update sample_data_listing set category = listing_category.id from listing_category where listing_category.name = sample_data_listing.category;
update sample_data_listing set category = 16 where category = 'Townhouse';
update sample_data_listing set category = 25 where category = 'Staff Accommodation';

update sample_data_listing set emirate = res_country_state.id from res_country_state where res_country_state.name = sample_data_listing.emirate;

update sample_data_listing set location = res_location.id from res_location where lower(res_location.name) = lower(sample_data_listing.location);

update sample_data_listing set sub_location = res_sub_location.id from res_sub_location where lower(res_sub_location.name) = lower(sample_data_listing.sub_location);

update sample_data_listing set beds = replace(beds,'.0','');
update sample_data_listing set beds = concat(beds,' Bed');
update sample_data_listing set beds = listing_bed.id from listing_bed where listing_bed.name = sample_data_listing.beds;

update sample_data_listing set bua = replace(bua,'.0','');
update sample_data_listing set price = replace(price,'.0','');


/////

update sample_data_listing set agent = hr_employee.id from hr_employee where lower(hr_employee.name) = lower(sample_data_listing.agent);

update sample_data_listing set owner_name = res_partner.id from res_partner where res_partner.name = sample_data_listing.owner_name;

update sample_data_listing set owner_mobile = replace(owner_mobile,'.0','');

update sample_data_listing set baths = replace(baths,'.0','');
update sample_data_listing set baths = listing_bath.id from listing_bath where listing_bath.name = sample_data_listing.baths;

update sample_data_listing set street = replace(street,'.0','');

update sample_data_listing set floor = replace(floor,'.0','');

update sample_data_listing set cheques = replace(cheques,'.0','');
update sample_data_listing set cheques = concat(cheques,' Cheque');
update sample_data_listing set cheques = number_of_cheque.id from number_of_cheque where number_of_cheque.name = sample_data_listing.cheques;

update sample_data_listing set fitted = listing_fitted.id from listing_fitted where listing_fitted.name = sample_data_listing.fitted;
update sample_data_listing set fitted = '' where fitted = '- -';

update sample_data_listing set property_status = listing_property_status.id from listing_property_status where listing_property_status.name = sample_data_listing.property_status;
update sample_data_listing set property_status = '' where property_status in ('--','Moved in');

update sample_data_listing set listing_souce = source_master.id from source_master where lower(source_master.name) = lower(sample_data_listing.listing_souce);
update sample_data_listing set listing_souce = '' where listing_souce in (' Not Specified','0.0','OA Referral','Cityscape');

update sample_data_listing set furnished = 'yes' where furnished = 'Furnished';
update sample_data_listing set furnished = 'no' where furnished = 'Unfurnished';
update sample_data_listing set furnished = '' where furnished in ('Not Specified','Partly Furnished');

update sample_data_listing set featured = 'TRUE' where featured = 'Yes';
update sample_data_listing set featured = 'FALSE' where featured = 'No';

update sample_data_listing set tenanted = 'TRUE' where tenanted = 'Yes';
update sample_data_listing set tenanted = 'FALSE' where tenanted = 'No';

update sample_data_listing set plot_size = replace(plot_size,'.0','');

update sample_data_listing set rera_permit_no = replace(rera_permit_no,'.0','');

update sample_data_listing set baths = '' where baths in ('0','10','7','9','8','12','11');

INSERT INTO listing_listing(ref_name, listing_status, customer_id, listing_type, price,
    deposit_amount, property_status_id, listing_region, unit,
    listing_detail_type, agent_id, listing_source_id, emirate_id,
    location_id, sub_location_id, category_id, bed_id, fitted_id, bath_id,
    build_up_area_sqf, name, description, no_of_cheques, furnished_id,
    property_view, is_featured, regulatory_permit, key_location, commission_amount, street,
    floor, is_property_tenanted, company_id, active)
SELECT sdl.reference, sdl.status, (case when isnumeric(owner_name) then CAST(sdl.owner_name AS INTEGER) end), 'Rental', (case when isnumeric(amount) then CAST(sdl.amount AS FLOAT) end),
    (case when isnumeric(deposit) then CAST(sdl.deposit AS FLOAT) end), (case when isnumeric(property_status) then CAST(sdl.property_status AS INTEGER) end), 'Local', sdl.unit,
    sdl.types, (case when isnumeric(agent) then CAST(sdl.agent AS INTEGER) end), (case when isnumeric(listing_souce) then CAST(sdl.listing_souce AS INTEGER) end), (case when isnumeric(emirate) then CAST(sdl.emirate AS INTEGER) end),
    (case when isnumeric(location) then CAST(sdl.location AS INTEGER) end), (case when isnumeric(sub_location) then CAST(sdl.sub_location AS INTEGER) end), (case when isnumeric(category) then CAST(sdl.category AS INTEGER) end), (case when isnumeric(beds) then CAST(sdl.beds AS INTEGER) end), (case when isnumeric(fitted) then CAST(sdl.fitted AS INTEGER) end), (case when isnumeric(baths) then CAST(sdl.baths AS INTEGER) end),
    (case when isnumeric(bua) then CAST(sdl.bua AS FLOAT) end), sdl.title, sdl.description, (case when isnumeric(cheques) then CAST(sdl.cheques AS INTEGER) end), sdl.furnished,
    sdl.view, (case when isnumeric(featured) then CAST(sdl.featured AS BOOLEAN) end), sdl.rera_permit_no, sdl.key_location, (case when isnumeric(commission) then CAST(sdl.commission AS FLOAT) end), sdl.street,
    sdl.floor, (case when isnumeric(tenanted) then CAST(sdl.tenanted AS BOOLEAN) end), 1, 'TRUE'
FROM sample_data_listing as sdl;
















