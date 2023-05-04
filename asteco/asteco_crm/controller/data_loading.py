from odoo import http
from odoo.http import request
import xlrd
import re
import werkzeug
from datetime import datetime

class DataLoading(http.Controller):

	@http.route(['/ast/contact/data/loading'], type='http', auth="public", website=True)
	def astDataLoading(self, **kw):
		sample_contact_obj = request.env["sample.data.contact"]
		# for record in sample_contact_obj.search([]):
		# 	record.unlink()
		book = xlrd.open_workbook("/opt/odoo/odoo-11.0/Asteco/asteco_crm/files/Contacts.xlsx")
		# book = xlrd.open_workbook("/opt/odoo/data_bkp/Contacts.xlsx")
		sh = book.sheet_by_index(0)
		row_count = sh.nrows
		i = 1
		while i < row_count:
			print("=========================>> ", i)
			sample_contact_obj.create({
				'ref': sh.cell_value(rowx=i, colx=0),
				'name': str(sh.cell_value(rowx=i, colx=2)) + " " + str(sh.cell_value(rowx=i, colx=3)),
				'mobile': sh.cell_value(rowx=i, colx=15),
				'email': sh.cell_value(rowx=i, colx=16),
				'title': sh.cell_value(rowx=i, colx=22),
				'assigned_to': sh.cell_value(rowx=i, colx=24),
				'updated': sh.cell_value(rowx=i, colx=25),
				'created_date': sh.cell_value(rowx=i, colx=42),
				'created_by': sh.cell_value(rowx=i, colx=43),
			})
			i += 1

		user_obj = request.env['res.users']
		# contact_obj = request.env['res.partner']
		# state_id = request.env['res.country.state'].search([('name','=','Dubai')], limit=1)
		# isd_code_id = request.env['res.country.code'].search([('country_id','=',state_id.country_id.id)])
		# source = request.env['source.master'].search([('name','=','Other')], limit=1)
		
		# titles = {
		# 	'Mr':'mr',
		# 	'Ms':'ms',
		# }

		# user_type = request.env['res.user.type'].search([('name','=','Agent Call Center')])
		c = 0
		for record in sample_contact_obj.search([]):
			user = user_obj.search([('name','=',record.created_by)])
			if not user:
				print("==========================count : ", c)
				c += 1
				user = user_obj.create({
						'name':record.created_by,
						'login':str(record.created_by) + "@asteco.com",
						'user_status':'active',
						'company_id':request.env.user.company_id.id,
						'agent_status':'available',
					})
			record.uid = user.id
		# count = 1
		# count = 0
		

		# start_time = datetime.now()
		# request.env.cr.execute("select * from sample_data_contact")
		# contacts = request.env.cr.dictfetchall()
		# for contact in contacts:
		# 	count += 1
		# 	print("=======================count : ", count)

		# 	email = contact['email']
		# 	match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
		# 	if match == None:
		# 		email = "contact" + str(count) + "@asteco.com"
		# 	if count == 50:
		# 		break
		# 	contact = contact_obj.create({
		# 			'is_contact':True,
		# 			'head':'individual',
		# 			'title':"mr",
		# 			'name':"Test Contact",
		# 			'isd_code_id':1,
		# 			'mobile':contact['mobile'],
		# 			'email':email,
		# 			'source':1,
		# 			'country_id':1,
		# 			'city_id':1,
		# 			'company_id':1,
		# 		})	
		# print("\n\n\n\n\n=============================Started : ", start_time)
		# print("=============================Completed : ", datetime.now())


		# for record in sample_contact_obj.search([],limit=1):
		# 	pass

		# 	# if record.title in titles.keys():
		# 	# 	title = titles[record.title]
		# 	# else:
		# 	# 	title = 'mr'

		# 	# mobile = "000000000" if record.mobile in ["- -",""," ",False] else record.mobile
		# 	# # if len(mobile) > 14:
		# 	# # 	l = len(mobile) - 14
		# 	# # 	mobile = mobile[:-l]
		# 	# if len(mobile) < 7 or len(mobile) > 15:
		# 	# 	mobile = "000000000"

		# 	# mobile = record.mobile

		# 	# rule = re.compile(r'^(?:\+?44)?[07]\d{9,13}$')

		# 	# if not rule.search(mobile):
		# 	# if len(mobile) < 7 or len(mobile) > 15:
		# 		# mobile = "000000000"+str(record.id)
			

		# 	print("=============================After mobile & Before Email : ", datetime.now())
		# 	# email = "contact" + str(record.id) + "@asteco.com" if record.email in ["- -",""," ",False] else record.email
		# 	# email = record.email
		# 	# email = email.lower()
		# 	# if '@' not in email:
		# 	# 	email += "@asteco.com"

		# 	# match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
		# 	# if match == None:
		# 		# email = "contact" + str(record.id) + "@asteco.com"

		# 	print("=============================After email : ", datetime.now())
		# 	# print("======================mobile : ", mobile)
		# 	# print("======================email : ", email)
		# 	# print("======================", count)
		# 	# count += 1

		# 	contact = contact_obj.create({
		# 			'is_contact':True,
		# 			'head':'individual',
		# 			'title':"mr",
		# 			'name':"Test Contact",
		# 			'isd_code_id':1,
		# 			'mobile':record.mobile,
		# 			'email':record.email,
		# 			'source':1,
		# 			'country_id':1,
		# 			'city_id':1,
		# 			'company_id':1,
		# 		})
			# contact.ref_name = record.ref
		# print("\n\n\n\n\n=============================Started : ", start_time)
		# print("=============================Completed : ", datetime.now())

		# return werkzeug.utils.redirect("/ast/lead/data/loading")
		return "Contacts data uploaded successfully."


	@http.route(['/ast/lead/data/loading'], type='http', auth="public", website=True)
	def astLeadDataLoading(self, **kw):
		sample_lead_obj = request.env["sample.data.lead"]
		# for record in sample_lead_obj.search([]):
		# 	record.unlink()
		book = xlrd.open_workbook("/opt/odoo/odoo-11.0/Asteco/asteco_crm/files/Leads.xlsx")
		# book = xlrd.open_workbook("/opt/odoo/data_bkp/Leads.xlsx")
		sh = book.sheet_by_index(0)
		row_count = sh.nrows
		i = 1
		while i < row_count:
			print("========================", i)
			sample_lead_obj.create({
				'ref':sh.cell_value(rowx=i, colx=0),
				'type':str(sh.cell_value(rowx=i, colx=1)),
				'status':str(sh.cell_value(rowx=i, colx=2)),
				'sub_status':str(sh.cell_value(rowx=i, colx=3)),
				'priority':str(sh.cell_value(rowx=i, colx=4)),
				'hot':str(sh.cell_value(rowx=i, colx=5)),
				'contact_name':str(sh.cell_value(rowx=i, colx=6)) + " " + str(sh.cell_value(rowx=i, colx=8)),
				'mobile':str(sh.cell_value(rowx=i, colx=9)),
				'phone':str(sh.cell_value(rowx=i, colx=10)),
				'email':str(sh.cell_value(rowx=i, colx=11)),
				'category':str(sh.cell_value(rowx=i, colx=12)),
				'emirate':str(sh.cell_value(rowx=i, colx=13)),
				'location':str(sh.cell_value(rowx=i, colx=14)),
				'sub_location':str(sh.cell_value(rowx=i, colx=15)),
				'min_beds':str(sh.cell_value(rowx=i, colx=18)),
				'max_beds':str(sh.cell_value(rowx=i, colx=19)),
				'source':str(sh.cell_value(rowx=i, colx=28)),
				'agent1':str(sh.cell_value(rowx=i, colx=29)),
				'created_by':str(sh.cell_value(rowx=i, colx=34)),
				'is_phone_lead':str(sh.cell_value(rowx=i, colx=36)),
				'enquiry_date':str(sh.cell_value(rowx=i, colx=37)),
				'ate_added':str(sh.cell_value(rowx=i, colx=38)),
				'date_updated':str(sh.cell_value(rowx=i, colx=39)),
				'notes':str(sh.cell_value(rowx=i, colx=46)),
			})
			i += 1

		return "Success"

		lead_obj = request.env['atk.lead.lead']
		customer_obj = request.env['res.partner']
		employee_obj = request.env['hr.employee']
		state_id = request.env['res.country.state'].search([('name','=','Dubai')], limit=1)
		isd_code_id = request.env['res.country.code'].search([('country_id','=',state_id.country_id.id)])
		category_obj = request.env['listing.category']
		location_obj = request.env['res.location']
		sub_location_obj = request.env['res.sub.location']
		bed_obj = request.env['listing.bed']
		user_obj = request.env['res.users']

		lead_status_dict = {
			'Open' : 'new',
			'Closed' : 'closed',
		}

		count = 1

		st = datetime.now()
		print("==========================start_time1 : ", datetime.now())
		for record in sample_lead_obj.search([]):

			print("========================", count)
			count += 1

			source = request.env['source.master'].search([('name','=',record.source)],limit=1)
			if not source:
				source = request.env['source.master'].search([('name','=','Other')], limit=1)

			email = "contact" + str(record.id) + "@asteco.com" if record.email in [False,"","''","' '"] else record.email
			email = email.lower()
			if '@' not in email:
				email += "@asteco.com"

			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
			if match == None:
				email = "contact" + str(record.id) + "@asteco.com"

			mobile = "000000000" if record.mobile in ["- -",""," ",False] else record.mobile
			if len(mobile) > 14:
				l = len(mobile) - 14
				mobile = mobile[:-l]
			if len(mobile) < 7 or len(mobile) > 15:
				mobile = "000000000"

			contact_id = customer_obj.search([('name','=',record.contact_name),('email','=',email)])
			if not contact_id:
				contact_id = customer_obj.create({
					'is_contact':True,
					'head':'individual',
					'title':'mr',
					'name':record.contact_name,
					'isd_code_id':isd_code_id.id,
					'mobile':mobile,
					'email':email,
					'source':source.id,
					'country_id':state_id.country_id.id,
					'city_id':state_id.id,
					'company_id':request.env.user.company_id.id,
				})

			if record.status in lead_status_dict.keys():
				status = lead_status_dict[record.status]
			else:
				status = 'new'

			category_id = category_obj.search([('name','=',record.category)])
			if not category_id:
				category_id = category_obj.search([('name','=','Apartment')])
			location_id = location_obj.search([('name','=',record.location)])
			sub_location_id = sub_location_obj.search([('name','=',record.sub_location)])

			if not sub_location_id:
				sub_location_id = sub_location_obj.browse(1)
				location_id = sub_location_id.location_id

			user_type = request.env['res.user.type'].search([('name','=','Agent Broker')])
			user_id = request.env['res.users'].search([('name','=',record.agent1)], limit=1)
			if not user_id:
				user_id = user_obj.create({
						'name':record.agent1,
						'login':str(record.agent1) + "@asteco.com",
						'user_type':user_type.id,
						'user_status':'active',
						'company_id':request.env.user.company_id.id,
						'agent_status':'available',
					})
			agent_id = employee_obj.search([('name','=',record.agent1),('user_id','=',user_id.id)])

		print("\n\n==========================start_time : ", st)
		print("==========================start_time2 : ", datetime.now())
			# bed_id = False
			# if '.0' in record.max_beds:
			# 	max_bed = record.max_beds[:-2]
			# 	bed_id = bed_obj.search([('name','=',str(max_bed)+" Bed")])

			# lead_id = lead_obj.create({
			# 	'status' : status,
			# 	'lead_type' : 'tenant',
			# 	'contact_id' : contact_id.id,
			# 	'isd_code_id' : contact_id.isd_code_id.id,
			# 	'customer_mobile' : contact_id.mobile,
			# 	'customer_email_id' : contact_id.email,
			# 	'auto_assign' : False,
			# 	'lead_source_id' : source.id,
			# 	'sub_status_id' : False,
			# 	'is_hot_lead' : 'yes' if record.hot == 'Hot Lead' else 'no',
			# 	'lead_req_ids' : [(0,0,{
			# 		'category_id' : category_id.id,
			# 		'emirate_id' : state_id.id,
			# 		'location_id' : location_id.id,
			# 		'sub_location_id' : sub_location_id.id,
			# 		'bed_id' : bed_id.id if bed_id else False,
			# 		'fitted_id' : 1 if not bed_id else False,
			# 	})],
			# 	'agent_id' : agent_id.id, 
			# 	'priority' : 'normal',
			# 	'company_id' : request.env.user.company_id.id,
			# })

			# lead_id.name = record.ref

			# notes

		# return werkzeug.utils.redirect("/ast/listing/data/loading")
		return 'Leads data uploaded successfully.'

	@http.route(['/ast/listing/data/loading'], type='http', auth="public", website=True)
	def astListingLoading(self, **kw):
		sample_listing_obj = request.env["sample.data.listing"]
		# for record in sample_listing_obj.search([]):
		# 	record.unlink()
		for j in range(1,3):
			book = xlrd.open_workbook("/opt/odoo/odoo-11.0/Asteco/asteco_crm/files/Listings"+str(j)+".xlsx")
			# book = xlrd.open_workbook("/opt/odoo/data_bkp/Listings"+str(i)+".xlsx")
			sh = book.sheet_by_index(0)
			row_count = sh.nrows
			print("=============================row count : ", row_count)
			i = 1
			while i < row_count:
				print("========================= i : ", i)
				ref = str(sh.cell_value(rowx=i, colx=4))
				if len(ref) == 0:
					i += 1
					continue
				sample_listing_obj.create({
					'status' : sh.cell_value(rowx=i, colx=0),
					'managed' : sh.cell_value(rowx=i, colx=1),
					'exclusive' : sh.cell_value(rowx=i, colx=2),
					'shared' : sh.cell_value(rowx=i, colx=3),
					'reference' : sh.cell_value(rowx=i, colx=4),
					'unit' : sh.cell_value(rowx=i, colx=5),
					'category' : sh.cell_value(rowx=i, colx=6),
					'emirate' : sh.cell_value(rowx=i, colx=7),
					'location' : sh.cell_value(rowx=i, colx=8),
					'sub_location' : sh.cell_value(rowx=i, colx=9),
					'beds' : sh.cell_value(rowx=i, colx=10),
					'bua' : sh.cell_value(rowx=i, colx=11),
					'price' : sh.cell_value(rowx=i, colx=12),
					'description' : sh.cell_value(rowx=i, colx=13),
					'agent' : sh.cell_value(rowx=i, colx=14),
					'owner_name' : sh.cell_value(rowx=i, colx=15),
					'owner_email': sh.cell_value(rowx=i, colx=16),
					'owner_mobile' : sh.cell_value(rowx=i, colx=17),
					'types' : sh.cell_value(rowx=i, colx=18),
					'baths' : sh.cell_value(rowx=i, colx=19),
					'street' : sh.cell_value(rowx=i, colx=20),
					'floor' : sh.cell_value(rowx=i, colx=21),
					'dewa' : sh.cell_value(rowx=i, colx=22),
					'photos' : sh.cell_value(rowx=i, colx=23),
					'cheques' : sh.cell_value(rowx=i, colx=24),
					'fitted' : sh.cell_value(rowx=i, colx=25),
					'property_status' : sh.cell_value(rowx=i, colx=26),
					'listing_souce' : sh.cell_value(rowx=i, colx=27),
					'portals' : sh.cell_value(rowx=i, colx=28),
					'date_available' : sh.cell_value(rowx=i, colx=29),
					'remind' : sh.cell_value(rowx=i, colx=30),
					'furnished' : sh.cell_value(rowx=i, colx=31),
					'featured' : sh.cell_value(rowx=i, colx=32),
					'maintenance_fee' : sh.cell_value(rowx=i, colx=33),
					'ast_str' : sh.cell_value(rowx=i, colx=34),
					'amount' : sh.cell_value(rowx=i, colx=35),
					'tenanted' : sh.cell_value(rowx=i, colx=36),
					'plot_size' : sh.cell_value(rowx=i, colx=37),
					'title' : sh.cell_value(rowx=i, colx=38),
					'view' : sh.cell_value(rowx=i, colx=39),
					'commission' : sh.cell_value(rowx=i, colx=40),
					'deposit' : sh.cell_value(rowx=i, colx=41),
					'price_per_sqft' : sh.cell_value(rowx=i, colx=42),
					'listed' : sh.cell_value(rowx=i, colx=43),
					'updated' : sh.cell_value(rowx=i, colx=44),
					'created_by' : sh.cell_value(rowx=i, colx=45),
					'update_by' : sh.cell_value(rowx=i, colx=46),
					'key_location' : sh.cell_value(rowx=i, colx=47),
					'developer_unit' : sh.cell_value(rowx=i, colx=48),
					'rera_permit_no' : sh.cell_value(rowx=i, colx=49),
					'dtcm_permit_no' : sh.cell_value(rowx=i, colx=50),
					'notes' : sh.cell_value(rowx=i, colx=51),
					'tenant' : sh.cell_value(rowx=i, colx=52),
					'last_published_on' : sh.cell_value(rowx=i, colx=53),
					})
				i += 1

			print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Total : ", i)
		return "Success"

		# 	listing_obj = request.env['listing.listing']
		# 	category_obj = request.env['listing.category']
		# 	sub_location_obj = request.env['res.sub.location']
		# 	bed_obj = request.env['listing.bed']
		# 	fitted_obj = request.env['listing.fitted']
		# 	bath_obj = request.env['listing.bath']
		# 	employee_obj = request.env['hr.employee']
		# 	user_obj = request.env['res.users']
		# 	user_type_obj = request.env['res.user.type']
		# 	customer_obj = request.env['res.partner']
		# 	isd_code_obj = request.env['res.country.code']
		# 	property_status_obj = request.env['listing.property.status']
		# 	visibility_obj = request.env['listing.visibility']
		# 	managed_status_obj = request.env['listing.managed.status']
		# 	cheques_obj = request.env['number.of.cheque']
		# 	notes_obj = request.env['crm.notes']
		# 	source_obj = request.env['source.master']
		# 	source = source_obj.search([('name','=','Other')], limit=1)
		# 	state_id = request.env['res.country.state'].search([('name','=','Dubai')], limit=1)

		# 	start = datetime.now()

		# 	count = 1
		# 	for record in sample_listing_obj.search([]):
		# 		if listing_obj.search([('ref_name','=',record.reference)]):
		# 			continue

		# 		category = category_obj.search([('name','=',record.category)])
				
		# 		sub_location_id = sub_location_obj.search([('name','=',record.sub_location)])
		# 		if not sub_location_id:
		# 			sub_location_id = sub_location_obj.browse(1)

		# 		bed = record.beds[:-2] if '.0' in record.beds else record.beds
		# 		bed_id = bed_obj.search([('name','=',str(bed)+" Bed")])

		# 		fitted = record.fitted[:-2] if '.0' in record.fitted else record.fitted
		# 		fitted_id = fitted_obj.search([('name','=',str(fitted))])

		# 		bath = record.baths[:-2] if '.0' in record.baths else record.baths
		# 		bath_id = bath_obj.search([('name','=',str(bath))])

		# 		cheques = record.cheques[:-2] if '.0' in record.cheques else record.cheques
		# 		cheque_id = cheques_obj.search([('name','=',str(cheques)+" Cheque")])

		# 		agent_id = employee_obj.search([('name','=',record.agent)], limit=1)
		# 		if not agent_id:
		# 			user_id = user_obj.create({
		# 					'name' : record.agent,
		# 					'login' : str(record.agent)+"@asteco.com",
		# 					'user_type' : user_type_obj.search([('name','=','Agent Broker')]).id,
		# 					'user_status' : 'active',
		# 					'agent_status' : 'available',
		# 				})
		# 			agent_id = employee_obj.search([('id','=',user_id.id)], limit=1)

		# 		if record.owner_email == '- -':
		# 			owner_email = "contact"+str(record.id)+"@asteco.com"
		# 		else:
		# 			owner_email = record.owner_email
		# 		owner_email = owner_email.lower()
		# 		if '@' not in owner_email:
		# 			owner_email += "@asteco.com"

		# 		match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', owner_email)
		# 		if match == None:
		# 			owner_email = "contact" + str(record.id) + "@asteco.com"

		# 		if record.owner_mobile == '- -':
		# 			owner_mobile = "0000000000"
		# 		else:
		# 			owner_mobile = record.owner_mobile

		# 		if len(owner_mobile) > 14:
		# 			l = len(owner_mobile) - 14
		# 			owner_mobile = owner_mobile[:-l]
		# 		if len(owner_mobile) < 7 or len(owner_mobile) > 15:
		# 			owner_mobile = "000000000"

		# 		print("=================time :", datetime.now())

		# 		contact_id = customer_obj.search([('name','=',record.owner_name)], limit=1)
		# 		if not contact_id:
		# 			contact_id = customer_obj.create({
		# 				'is_contact':True,
		# 				'head':'individual',
		# 				'title':'mr',
		# 				'name':record.owner_name,
		# 				'isd_code_id':isd_code_obj.search([('country_id','=',state_id.country_id.id)]).id,
		# 				'mobile':owner_mobile,
		# 				'email':owner_email,
		# 				'source':source.id,
		# 				'country_id':state_id.country_id.id,
		# 				'city_id':state_id.id,
		# 				'company_id':request.env.user.company_id.id,
		# 			})

		# 		property_status_id = property_status_obj.search([('name','=',record.property_status)])
		# 		if not property_status_id:
		# 			property_status_id = property_status_obj.search([('name','=','Available')])

		# 		source_id = source_obj.search([('name','=',record.listing_souce)])

		# 		bua_sqf = record.bua[:-2] if '.0' in record.bua else record.bua
		# 		if bua_sqf == '0':
		# 			bua_sqf = 1

		# 		commission = record.commission
		# 		if re.search('[a-zA-Z]', commission):
		# 			commission = 0

		# 		deposit = record.deposit[:-2] if '.0' in record.deposit else record.deposit
		# 		if re.search('[a-zA-Z]', deposit):
		# 			deposit = 0

		# 		price = record.price[:-2] if '.0' in record.price else record.price
		# 		if float(price) <= 0.0:
		# 			price = 1
				
		# 		contact_mail = contact_id.email
		# 		match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', contact_mail)
		# 		if match == None:
		# 			contact_mail = "contact" + str(contact_id.id) + "@test.com"

		# 		contact_mobile = contact_id.mobile
		# 		if len(contact_mobile) < 7 or len(contact_mobile) > 15:
		# 			contact_mobile = "000000000"
		# 		print("==================================count : ", count)
		# 		count += 1
		# 		listing_id = listing_obj.create({
		# 				'listing_status' : record.status,
		# 				'customer_id' : contact_id.id,
		# 				'listing_type' : 'Rental' if '-R-' in record.reference else 'Sale',
		# 				'isd_code_id' : contact_id.isd_code_id.id,
		# 				'customer_mobile' : contact_mobile,
		# 				'customer_email_id' : contact_mail,
		# 				'price' : price,
		# 				'deposit_amount' : deposit,
		# 				'property_status_id' : property_status_id.id,
		# 				'listing_region' : 'Local',
		# 				'visibility_id' : visibility_obj.search([('name','=','Network')]).id,
		# 				'unit' : record.unit[:-2] if '.0' in record.unit else record.unit,
		# 				'listing_detail_type' : record.types,
		# 				'agent_id' : agent_id.id,
		# 				'listing_source_id' : source_id.id if source_id else source.id,
		# 				'managed_status_id' : managed_status_obj.search([('name','=','Managed')]).id,
		# 				'emirate_id' : sub_location_id.location_id.emirate_id.id,
		# 				'location_id' : sub_location_id.location_id.id,
		# 				'sub_location_id' : sub_location_id.id,
		# 				'category_id' : category.id,
		# 				'bed_id' : bed_id.id if bed_id else False,
		# 				'fitted_id' : fitted_id.id if fitted_id else False,
		# 				'bath_id' : bath_id.id if bath_id else False,
		# 				'build_up_area_sqf' : bua_sqf,
		# 				'build_up_area_sqm' : float(bua_sqf) / 10.764,
		# 				'name' : record.title,
		# 				'description' : record.description,
		# 				'no_of_cheques' : cheque_id.id if cheque_id else 1,
		# 				'furnished_id' : 'no' if record.furnished == 'Unfurnished' else False,
		# 				'property_view' : record.view,
		# 				'is_featured' : True if record.featured == 'Yes' else False,
		# 				'regulatory_permit' : record.rera_permit_no[:-2] if '.0' in record.rera_permit_no else record.rera_permit_no,
		# 				'key_location' : record.key_location,
		# 				'commission_amount' : commission,
		# 				'street' : record.street[:-2] if '.0' in record.street else record.street,
		# 				'floor' : record.floor[:-2] if '.0' in record.floor else record.floor,
		# 				'is_property_tenanted' : False if record.tenanted == 'No' else True,
		# 				'plot_area' : record.plot_size[:-2] if '.0' in record.plot_size else record.plot_size,
		# 				# 'portal_ids' : ,
		# 			})

		# 		listing_id.ref_name = record.reference
				
		# 		notes = record.notes
		# 		notes_obj.create({
		# 				'listing_id':listing_id.id,
		# 				'name':notes,
		# 			})

		# print("====================Start Time : ", start)
		# print("====================End Time : ", datetime.now())

		# return "Listings data uploaded successfully."


		