from odoo import http
from odoo.http import request
import werkzeug
import xlrd
from datetime import datetime

from odoo.addons.portal.controllers.web import Home

class Website(Home):

	@http.route('/', type='http', auth="none")
	def index(self, s_action=None, db=None, **kw):
		return http.local_redirect('/web', query=request.params, keep_hash=True)

class Main(http.Controller):

	@http.route(['/update/leadrotation/flag'], type='http', auth="public", website=True)
	def update_lead_rotation_flag(self, **kw):
		for record in request.env['lead.rotation'].search([]):
			if record.last_assingned_date == False and record.agent_id.user_id.login_date:
				record.last_assingned_date = record.agent_id.user_id.login_date
		return "success"

	@http.route(['/network/to/withincompany'], type='http', auth="public", website=True)
	def networktowithincompany(self, **kw):
		request.env.cr.execute("""update listing_listing set visibility_id = 2 where visibility_id = 1;""")
		return "success"

	@http.route(['/delete/offered/unit'], type='http', auth="public", website=True)
	def delete_offered_unit(self, **kw):	
		for record in request.env['lead.offered.unit'].search([]):
			record.unlink()
		return "success"

	@http.route(['/delete/deal'], type='http', auth="public", website=True)
	def delete_deal_deal(self, **kw):	
		for record in request.env['deal.deal'].search([]):
			record.unlink()
		return "success"

	@http.route(['/delete/proforma/invoice'], type='http', auth="public", website=True)
	def delete_proforma_invoice(self, **kw):	
		for record in request.env['crm.proforma.invoice'].search([]):
			record.unlink()
		return "success"

	@http.route(['/delete/auto/action'], type='http', auth="public", website=True)
	def delete_auto_action(self, **kw):
		for record in request.env['auto.action.scheduler'].search([]):
			record.unlink()
		return "success"

	@http.route(['/inactive/auto/action'], type='http', auth="public", website=True)
	def inactive_auto_action(self, **kw):
		for record in request.env['auto.action.scheduler'].search([]):
			record.is_active = False
		return "success"

	# Temporary method
	@http.route(['/delete/wrong/data'], type='http', auth="public", website=True)
	def delete_wrong_data(self, **kw):

		listing_id = request.env['listing.listing'].search([('id','=',2)])
		if listing_id:
			listing_id.is_office = True

		c = 1
		for record in request.env['listing.bed'].search([]):
			record.name = str(c)
			c += 1

		bath_id = request.env['listing.bath'].search([('name','=','3')])
		if bath_id:
			bath_id.unlink()

		pf_id = request.env['listing.price.frequency'].search([('name','=','Per Yea')])
		if pf_id:
			pf_id.unlink()

		lps_id = request.env['listing.property.status'].search([('name','=','Availab')])
		if lps_id:
			lps_id.unlink()

		v_id = request.env['listing.visibility'].search([('name','=','Network')], limit=1)
		if v_id:
			v_id.unlink()
		return "success"

	@http.route(['/remove/location/locs'], type='http', auth="public", website=True)
	def remove_location_locs(self, **kw):
		for location in request.env['res.location'].search([('name','in',['Location 1','Location 2'])]):
			location.unlink()
		return "success"

	@http.route(['/update/lead/sustatus'], type='http', auth="public", website=True)
	def update_lead_substatus(self, **kw):
		for record in request.env['lead.sub.status'].search([]):
			record.unlink()
		return "success"
		# status_list = ['In progress','Called no reply','Follow up','Needs more info','Need time','Client to revert',
		# 			   'Looks see','Client not reachable','Qualified','Lead Lost','New']
		# for item in status_list:
		# 	request.env['lead.sub.status'].create({
		# 			'name':str(item),
		# 		})

	@http.route(['/testController'], type='http', auth="public", website=True)
	def test_controller(self):
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",http.request.env.user.name)
		actual = []
		for emp in http.request.env.user.employee_ids:
			print(">>>>>>>>>>>>> sales manager emp :", emp.name)
			for child in emp.child_ids:
				print(">>>>>>>>>>>>> work manager emp:", child.name)
				actual += child.child_ids.ids
				for grandchild in child.child_ids:
					print(">>>>>>>>>>>>> agent broker emp:", grandchild.name)
		print(">>>>>>>>>>>>>>>> actual : ", actual)
		# result = grandchild.id for grandchild in [child for child in [employee for employee in user.employee_ids]]

		result = [child.child_ids for child in [emp.child_ids for emp in http.request.env.user.employee_ids]]

		print("<<<<<<<<<<<<<<<<<result ", result)
		for xxx in result:
			for abc in xxx:
				print("--------------------------",abc)

	@http.route(['/delete-sub-status-lead'], type='http', auth="public", website=True)
	def delete_substatus(self):
		substatus = ['Not Yet Contacted','Viewings','Negotiation','Converted to Deal']
		sub_ids = request.env['lead.sub.status'].search([('name','in',substatus)])
		for sub in sub_ids:
			sub.unlink()

	@http.route(['/change-listing-visibility'], type='http', auth="public", website=True)
	def change_visibility(self):
		visibility_ids = request.env['listing.visibility'].sudo().search([('name', '=', 'Public')])
		for visible in visibility_ids:
			visible.name = "Within Company"
		contact_ids = request.env['res.partner'].search([('contact_type', '=', 'public')])
		for contact in contact_ids:
			contact.contact_type = 'within_company'


	@http.route(['/asteco/<string:model>/<int:ids>'], type='http', auth="public", website=True)
	def method_img(self,model,ids=None):
		if model:
			obj = request.env[model].search([('id', '=', ids)])
			if obj:
				return werkzeug.utils.redirect(request.env['website'].image_url(obj, 'name'))
			else :
				return 

	@http.route(['/update/escalation/field'], type='http', auth="public", website=True)
	def update_escalation_field(self, **kw):
		self = request.env['action.field.value']
		for record in self.search([]):
			record.unlink()
		model_id = request.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_id = request.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','agent_confidence_score')])
		for i in range(-5,6):
			self.create({
					'name':str(i),
					'value':str(i),
					'field_id':field_id.id,
				})
		field_id_2 = request.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','state')])
		self.create({
				'name':'New',
				'value':'new',
				'field_id':field_id_2.id,
			})
		self.create({
				'name':'Work In Progress',
				'value':'work_Progress',
				'field_id':field_id_2.id,
			})
		self.create({
				'name':'Closed',
				'value':'success',
				'field_id':field_id_2.id,
			})
		field_id_3 = request.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','pool_status')])
		self.create({
				'name':'Agent Assigned',
				'value':'Agent Assigned',
				'field_id':field_id_3.id,
			})
		self.create({
				'name':'Lead Pool',
				'value':'Lead Pool',
				'field_id':field_id_3.id,
			})
		self.create({
				'name':'Network Pool',
				'value':'Network Pool',
				'field_id':field_id_3.id,
			})
		field_id_4 = request.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','agent_id')])
		for employee in request.env['hr.employee'].search([]):
			self.create({
				'name':employee.name,
				'value':employee.id,
				'field_id':field_id_4.id,
			})
		field_id_5 = request.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','future_action_date')])
		self.create({
				'name':'Current Date',
				'value':'Current Date',
				'field_id':field_id_5.id,
			})
		return "success"

	@http.route(['/update/confidence/score'], type='http', auth="public", website=True)
	def update_confidence_score(self, **kw):
		for employee in request.env['hr.employee'].search([]):
			employee.confidence_score = 100
		return "success"


	@http.route(['/lead/add/idd'], type='http', auth="public", website=True)
	def lead_add_idd(self, **kw):
		country_code = request.env['res.country.code'].search([('country_code','=','971')]).id
		for lead in request.env['atk.lead.lead'].search([]):
			if not lead.isd_code_id:
				lead.isd_code_id = country_code

	@http.route(['/listing/change/code/prefix'], type='http', auth="public", website=True)
	def company_change_prefix(self, **kw):
		seq_id = request.env['ir.sequence'].search([])
		for seqs in seq_id:
			if seqs.prefix == "AST-R-":
				seqs.prefix = "-R-"
			elif seqs.prefix == "AST-S-":
				seqs.prefix = "-S-"
			elif seqs.prefix == "AST-L-":
				seqs.prefix="-L-"
			elif seqs.prefix == "AST-D-":
				seqs.prefix = "-D-"

	# This Controller is to remove the strings after the / - to format the languages as in the propspace 
	@http.route(['/language/change'], type='http', auth="public", website=True)
	def change_language(self, **kw):
		lan_id = request.env['res.lang'].search([])
		variable = '/'
		for language in lan_id:
			# print(" Before language name= ",language.name)
			language.name = language.name.split(variable,1)[0]
			# print(" After language name= ",language.name)
		return 'success'

	# To change the field ref into ref_name in server (Listing)
	@http.route(['/listing/change/ref'], type='http', auth="public", website=True)
	def change_listing_name(self, **kw):
		list_id = request.env['listing.listing'].search([])
		for lists in list_id:
			lists.ref_name = lists.ref
		return 'success'

	# To change the field ref into name in server (Leads)
	@http.route(['/leads/change/ref'], type='http', auth="public", website=True)
	def change_listing_name(self, **kw):
		lead_id = request.env['atk.lead.lead'].search([])
		for lead in lead_id:
			lead.name = lead.ref
		return 'success'

	# To change the field ref into name in server (Contacts)
	@http.route(['/contacts/change/ref'], type='http', auth="public", website=True)
	def change_contact_references(self, **kw):
		for contact in request.env['res.partner'].search([]):
			if contact.ref:
				contact.ref_name = contact.ref
		return 'success'

	# Private into Within Company ---- in listing.visibility table
	@http.route(['/listing/change/visibility/private'], type='http', auth="public", website=True)
	def change_contact_references(self, **kw):
		for visibility in request.env['listing.visibility'].search([]):
			if visibility.name == 'Public':
				visibility.name = 'Within Company'
		return 'success'
	# BUA conversion for listing
	@http.route(['/listing/bua/conversion'], type='http', auth="public", website=True)
	def bua_conversion(self, **kw):
		list_id = request.env['listing.listing'].search([])
		c = 0
		d = 0
		price = 0
		for list in list_id:
			d = d + 1
			if list.build_up_area_sqf > 0.0 and list.build_up_area_sqm == 0.0:
				c = c+1
				if list.price == 0:
					price = price+1
					list.price = 0.01
					list.build_up_area_sqm = list.build_up_area_sqf / 10.764
		return 'ok'

	@http.route(['/private/to/withincompany'], type='http', auth="public", website=True)
	def privatetowithincompany(self, **kw):
		for contact_type in request.env['res.partner'].search([]):
			if contact_type.contact_type == 'private':
				contact_type.contact_type = 'within_company'
		return 'success'

class DealLoading(http.Controller):

	@http.route(['/deal/data/loading'], type='http', auth="public", website=True)
	def deal_data_loading(self, **kw):
		master_obj = request.env["deal.temp"]
		request.env.cr.execute("truncate table deal_temp;")
		path = str(request.env['res.company'].sudo().browse(1).watermark)
		book = xlrd.open_workbook(path)
		sh = book.sheet_by_index(0)
		row_count = sh.nrows
		i = 0
		while i < row_count:
			master_obj.create({
				'reference' : sh.cell_value(rowx=i, colx=0),
				'listing_ref' : sh.cell_value(rowx=i, colx=1),
				'status' : sh.cell_value(rowx=i, colx=2),
				'sub_status' : sh.cell_value(rowx=i, colx=3),
				'contact_listing' : sh.cell_value(rowx=i, colx=4),
				'mobile' : sh.cell_value(rowx=i, colx=5),
				'email' : sh.cell_value(rowx=i, colx=6),
				'listing_type' : sh.cell_value(rowx=i, colx=7),
				'price' : sh.cell_value(rowx=i, colx=8),
				'listing_category' : sh.cell_value(rowx=i, colx=9),
				'available_from' : sh.cell_value(rowx=i, colx=10),
				'listing_unit' : sh.cell_value(rowx=i, colx=11),
				'lead_ref' : sh.cell_value(rowx=i, colx=12),
				'contact_lead' : sh.cell_value(rowx=i, colx=13),
				'lead_type' : sh.cell_value(rowx=i, colx=14),
				'assigned_to' : sh.cell_value(rowx=i, colx=15),
				'lead_source' : sh.cell_value(rowx=i, colx=16),
				'created_by' : sh.cell_value(rowx=i, colx=17),
				'transaction_type' : sh.cell_value(rowx=i, colx=18),
				'deal_price_aed' : sh.cell_value(rowx=i, colx=19),
				'deposit_aed' : sh.cell_value(rowx=i, colx=20),
				'estimated_deal_date' : sh.cell_value(rowx=i, colx=21),
				'actual_deal_date' : sh.cell_value(rowx=i, colx=22),
				'cheques' : sh.cell_value(rowx=i, colx=23),
				'tenancy_contract_start_date' : sh.cell_value(rowx=i, colx=24),
				'tenancy_renewal_date' : sh.cell_value(rowx=i, colx=25),
				'finance_type' : sh.cell_value(rowx=i, colx=26),
				'buyer_type' : sh.cell_value(rowx=i, colx=27),
				'gross_commission_aed' : sh.cell_value(rowx=i, colx=28),
				'inclusive_of_vat_yes_or_no' : sh.cell_value(rowx=i, colx=29),
				'total_gross_commission_aed' : sh.cell_value(rowx=i, colx=30),
				'split_with_external_referral' : sh.cell_value(rowx=i, colx=31),
				'split_with_internal' : sh.cell_value(rowx=i, colx=32),
				'split_with_etwork' : sh.cell_value(rowx=i, colx=33),
				'total_earned_commission_aed' : sh.cell_value(rowx=i, colx=34),
				'emirate_or_city' : sh.cell_value(rowx=i, colx=35),
				'location_or_roject' : sh.cell_value(rowx=i, colx=36),
				'sub_location_or_building' : sh.cell_value(rowx=i, colx=37),
				'bed' : sh.cell_value(rowx=i, colx=38),
				'bath' : sh.cell_value(rowx=i, colx=39),
				'floor' : sh.cell_value(rowx=i, colx=40),
				'street' : sh.cell_value(rowx=i, colx=41),
				'build_up_area_sqft' : sh.cell_value(rowx=i, colx=42),
				'unit' : sh.cell_value(rowx=i, colx=43),
				'type' : sh.cell_value(rowx=i, colx=44),
				'view' : sh.cell_value(rowx=i, colx=45),
				'parking' : sh.cell_value(rowx=i, colx=46),
				'managed_status' : sh.cell_value(rowx=i, colx=47),
				'created_date_and_time' : sh.cell_value(rowx=i, colx=48),
				'last_updated_date_and_time' : sh.cell_value(rowx=i, colx=49),
				'last_updated_by' : sh.cell_value(rowx=i, colx=50),
				'notes' : sh.cell_value(rowx=i, colx=51),
			})
			i += 1
		return "Success"

	@http.route(['/update/deal/data/date'], type='http', auth="public", website=True)
	def update_deal_data_date(self, **kw):
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.estimated_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.estimated_date = False
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.actual_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.actual_date = False
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.tenancy_contract_start_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.tenancy_contract_start_date = False
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.tenancy_renewal_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.tenancy_renewal_date = False
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.create_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.create_date = False
		for temp in request.env['deal.deal'].search([], limit=3735, order="id desc"):
			data = temp.write_date
			if data:
				if int(data[:4]) < 2000 or int(data[:4]) > 2025:
					temp.write_date = False
		return "Done"

	@http.route(['/update/deal/data/cheq'], type='http', auth="public", website=True)
	def update_deal_data_cheq(self, **kw):
		count = 1
		for rec in request.env['deal.temp'].search([]):
			cheq = rec.cheques
			if '.0' in cheq:
				cheq_id = request.env['number.of.cheque'].search([('name','=',cheq.split('.0')[0]+' Cheque')])
				if cheq_id:
					request.env.cr.execute("update deal_deal set cheque_id = %s where name = %s",[cheq_id.id,rec.reference])
					count += 1
		return "Done"

	# To Set Geotag unit
	@http.route(['/listing/set/geotag'], type='http', auth="public", website=True)
	def set_geotag_in_listing(self, **kw):
		for listing in request.env['listing.listing'].search([]):
			if listing.sub_location_id and not listing.unit_geo_tag:
				listing.onchange_sub_location_id()
		return 'success'	

# To set Property Use Type in listing.category, according to the Category
	@http.route(['/listing/category/set/property_use_type'], type='http', auth="public", website=True)
	def set_property_use_type_in_listing_category(self, **kw):
		for category in request.env['listing.category'].search([]):
			if category.name and category.name in ['Office','Retail','Hotel Apartment','Warehouse','Land Commercial','Labour Camp','Commercial Full Building','Hotel','Land Mixed Use','Compound','Commercial Villa','Factory','Commercial Full Floor','Commercial Half Floor','Show Room','Shop','Buisness Centre','Land Industrial','Open Yard']:
				category.property_use_type = 'Commercial'
			elif category.name and category.name in ['Apartment','Villa','Residential Building','Multiple Sale Units','Land Residential','Penthouse','Duplex','Loft Apartment','Town House','Half Floor','Full Floor','Bungalow','Staff Accomodation','Multiple Rental Units','Residential Full Floor','Residential Half Floor']:
				category.property_use_type = 'Residential'
		return 'success'