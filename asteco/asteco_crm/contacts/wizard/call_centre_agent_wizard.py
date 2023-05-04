from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
import re


class callCentreAgentWizard(models.TransientModel):
	_name = "call.centre.agent.wizard"

	phone = fields.Char("Phone")
	email = fields.Char("Email")
	name = fields.Char(default="Call Centre Agents")

	isd_code_id = fields.Many2one('res.country.code', "IDD",required=True, default = lambda self:self.env['res.country.code'].search([('country_code','=','971')], limit=1).id)
	contact_id = fields.Many2one('res.partner', string="Contact")
	country_id = fields.Many2one('res.country', string="Country", default = lambda self:self.env['res.country'].search([('phone_code','=','971')], limit=1).id)
	contact_ids =fields.Many2many('res.partner')
	listing_ids = fields.Many2many('listing.listing')
	lead_ids = fields.Many2many('atk.lead.lead')

	is_contacts = fields.Boolean(default=False)
	is_listing = fields.Boolean(default=False)
	is_leads = fields.Boolean(default=False)

	@api.onchange('country_id')
	def onchange_country_id(self):
		self.isd_code_id = self.env['res.country.code'].search([('country_code','=',self.country_id.phone_code)], limit=1).id

	@api.multi
	def search_contacts(self):
		self.clear_search_results()
		self.validate_phone_and_email()
		
		if self.phone == False and self.email == False:
			raise Warning("Please provide Mobile number or Email address!")
		domain = []
		if self.phone:
			domain.append(('mobile','=',self.phone))
			domain.append(('isd_code_id','=',self.isd_code_id.id))
		if self.email:
			domain.append(('email','=',self.email))
		contact_id = self.env['res.partner'].search(domain, limit=1)
		if contact_id:
			self.contact_id = contact_id.id
			self.phone = contact_id.mobile
			self.email = contact_id.email
			listing_ids = self.env['listing.listing'].search([('customer_id','=',contact_id.id)]).ids
			lead_ids = self.env['atk.lead.lead'].search([('contact_id','=',contact_id.id)]).ids

			if contact_id:
				self.contact_ids = contact_id.ids
				self.is_contacts = True
			else:
				self.listing_ids = False
				self.is_listing = False
			if listing_ids:
				self.listing_ids = listing_ids
				self.is_listing = True
			else:
				self.listing_ids = False
				self.is_listing = False
			if lead_ids:
				self.lead_ids = lead_ids
				self.is_leads = True
			else:
				self.lead_ids = False
				self.is_leads = False
			return {
				"type": "ir.actions.do_nothing",
			}
		else:
			raise Warning("No contact found!!!")

	# @api.multi
	# def add_new_contact(self):
	# 	view_id = self.env.ref('asteco_crm.atk_contacts_view_form')
	# 	return {
	# 		'name':'Create Contact',
	# 		'type': 'ir.actions.act_window',
	# 		'res_model': 'res.partner',
	# 		'view_type': 'form',
	# 		'view_mode': 'form',
	# 		'target':'new',
	# 		'views': [[view_id.id, 'form']],
	# 		'context':{'default_is_contact':True, 'default_isd_code_id':self.isd_code_id.id, 'default_mobile':self.phone, 'default_email':self.email},
	# 	}

	@api.multi
	def add_new_lead(self):
		self.validate_phone_and_email()
		domain = []
		if self.phone:
			domain.append(('mobile','=',self.phone))
			domain.append(('isd_code_id','=',self.isd_code_id.id))
		if self.email:
			domain.append(('email','=',self.email))

		if domain:
			contact_id = self.env['res.partner'].search(domain, limit=1)
			if contact_id:
				view_id = self.env.ref('asteco_crm.atk_lead_lead_view_form')
				return {
					'name':'Create Lead',
					'type': 'ir.actions.act_window',
					'res_model': 'atk.lead.lead',
					'view_type': 'form',
					'view_mode': 'form',
					# 'target':'new',
					'views': [[view_id.id, 'form']],
					'context':{'default_contact_id':contact_id.id},
				}
			else:
				country = self.isd_code_id.country_id
				view_id = self.env.ref('asteco_crm.atk_contacts_view_form')
				return {
					'name':'Create Contact',
					'type': 'ir.actions.act_window',
					'res_model': 'res.partner',
					'view_type': 'form',
					'view_mode': 'form',
					# 'target':'new',
					'views': [[view_id.id, 'form']],
					'context':{'default_is_contact':True, 'default_country_id':country, 'default_mobile':self.phone, 'default_email':self.email},
				}
		else:
			country = self.isd_code_id.country_id
			view_id = self.env.ref('asteco_crm.atk_lead_lead_view_form')
			return {
				'name':'Create Lead',
				'type': 'ir.actions.act_window',
				'res_model': 'atk.lead.lead',
				'view_type': 'form',
				'view_mode': 'form',
				# 'target':'new',
				'views': [[view_id.id, 'form']],
				'context':{'default_country_id':country},

				}


	@api.multi
	def clear_search_data(self):
		self.phone = self.email = False
		self.isd_code_id = self.env['res.country.code'].search([('country_code','=','971')], limit=1).id
		self.clear_search_results()
		return {
			"type": "ir.actions.do_nothing",
		}

	@api.multi
	def clear_search_results(self):
		self.contact_id = self.country_id = self.contact_ids = False
		self.listing_ids = self.lead_ids = self.is_contacts = self.is_listing = self.is_leads = False

	@api.multi
	def clear_phone(self):
		self.phone = False
		return {
			"type": "ir.actions.do_nothing",
		}

	@api.multi
	def clear_email(self):
		self.email = False
		return {
			"type": "ir.actions.do_nothing",
		}
	@api.multi
	def validate_phone_and_email(self):
		if self.phone:
			if len(self.phone) < 7 or len(self.phone) > 12:
				raise ValidationError("Please enter a valid mobile number!!!")
		if self.email:
			match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
			if match == None:
				raise ValidationError('Not a valid E-mail ID')

	# @api.constrains('phone')
	# def _check_mobile(self):
	# 	for record in self:
	# 		if record.phone:
	# 			if len(record.phone) < 7 or len(record.phone) > 12:
	# 				raise ValidationError("Please enter a valid mobile number!!!")
	# 		else:
	# 			raise ValidationError("Please enter mobile number!!!")

	# @api.onchange('email')
	# def validate_mail(self):s
	# 	if self.email:
	# 		match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
	# 		if match == None:
	# 			raise ValidationError('Not a valid E-mail ID')

		# view_id = self.env.ref('asteco_crm.call_centre_agent_form')
		# return {
		# 	'type': 'ir.actions.act_window',
		# 	'res_model': 'call.centre.agent.wizard',
		# 	'view_type': 'form',
		# 	'view_mode': 'form',
		# 	'target': 'new',
		# 	'views': [[view_id.id, 'form']],
		# }


