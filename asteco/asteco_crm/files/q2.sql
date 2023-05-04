select * from res_country_code where country_code = '971';
update res_partner set isd_code_id = 235 where isd_code_id is null;
update listing_listing set isd_code_id = 235 where isd_code_id is null;
update atk_lead_lead set isd_code_id = 235 where isd_code_id is null;



select distinct emirate from sample_data_lead;

update sample_data_lead set emirate = 552 where emirate = 'Umm Al Quwain';
update sample_data_lead set emirate = 550 where emirate = 'Ras Al Khaimah';


select name from res_country_state where country_id = 2;

insert into res_country_state(country_id, name, code) values (2,'Al Ain','AA');
select * from res_country_state where name = 'Al Ain';

update sample_data_lead set emirate = 681 where emirate = 'Al Ain';





select distinct location, emirate from sample_data_lead;


insert into res_location(name, emirate_id)
select distinct location,CAST(emirate AS INTEGER) from sample_data_lead where not isnumeric(location) and emirate not in ('FALSE','');








insert into res_location(name, emirate_id)
select distinct location, emirate from sample_data_lead;

update sample_data_lead set emirate = '548' where emirate = '';


insert into res_location(name, emirate_id)
select distinct location,CAST(emirate AS INTEGER) from sample_data_lead where not isnumeric(location) and emirate not in ('FALSE','','681');
update sample_data_lead set location = res_location.id from res_location where lower(res_location.name) = lower(sample_data_lead.location);


select sub_location from sample_data_lead where not isnumeric(sub_location);

insert into res_sub_location(name, location_id)
select distinct sub_location,CAST(location AS INTEGER) from sample_data_lead where not isnumeric(sub_location) and isnumeric(location);

update sample_data_lead set sub_location = res_sub_location.id from res_sub_location where lower(res_sub_location.name) = lower(sample_data_lead.sub_location);


INSERT INTO atk_lead_requirement(category_id, emirate_id, location_id, sub_location_id, bed_id, lead_id)
SELECT (case when isnumeric(category) then CAST(sdl.category AS INTEGER) end), (case when isnumeric(emirate) then CAST(sdl.emirate AS INTEGER) end),
 (case when isnumeric(location) then CAST(sdl.location AS INTEGER) end), (case when isnumeric(sub_location) then CAST(sdl.sub_location AS INTEGER) end),
(case when isnumeric(max_beds) then CAST(sdl.max_beds AS INTEGER) end), al.id FROM sample_data_lead as sdl join atk_lead_lead as al on sdl.ref = al.name;
