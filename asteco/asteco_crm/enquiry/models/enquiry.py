from odoo import fields, models, api
from odoo.exceptions import Warning

class ListingEnquiry(models.Model):
	_name = 'listing.enquiry'
	_description = "Enquiry"

	name = fields.Char(string="Ref #")
	contact_name = fields.Char(string="Contact Name", required=True)
	email = fields.Char(string="Email", required=True)
	mobile = fields.Char(string="Mobile", required=True)
	prefered_date = fields.Date(string="Prefered Date")
	comments = fields.Text(string="Comments")
	status = fields.Selection([('Draft','Draft'),('Converted to Lead','Converted to Lead'),('Rejected','Rejected')], default="Draft")
	listing_id = fields.Many2one('listing.listing', string="Listing Ref#", required=True)
	lead_id = fields.Many2one('atk.lead.lead', string="Lead Ref#")

	@api.model
	def create(self, vals):
		res = super(ListingEnquiry, self).create(vals)
		res.name = str(self.env.user.company_id.code) + str(self.env['ir.sequence'].sudo().next_by_code('listing.enquiry'))
		return res

	@api.multi
	def confirm_enquiry(self):
		contact_id = self.env['res.partner'].search([('email','=',self.email)])
		source = self.env['source.master'].search([('name','=','Web Enquiry')]).id
		if not contact_id:
			contact_id = self.env['res.partner'].sudo().create({
					'name':self.contact_name,
					'mobile':self.mobile,
					'email':self.email,
					'source':source,
					'active':True,
					'is_contact':True,
				})
		listing_id = self.listing_id
		if listing_id.listing_type == 'Rental':
			lead_type = 'tenant'
		else:
			lead_type = 'buyer'
		lead_ids = self.env['atk.lead.lead'].search([('contact_id','=',contact_id.id),('lead_type','=',lead_type)])
		for lead in  lead_ids:
			for unit in lead.lead_offered_unit_ids:
				if unit.listing_id.id == listing_id.id:
					raise Warning('Lead exist!!!')
		property_req = {
				'category_id':listing_id.category_id.id,
				'emirate_id':listing_id.emirate_id.id,
				'location_id':listing_id.location_id.id,
				'sub_location_id':listing_id.sub_location_id.id,
				'bed_id':listing_id.bed_id.id,
				'fitted_id':listing_id.fitted_id.id,
			}
		lead_id = self.env['atk.lead.lead'].create({
				'contact_id':contact_id.id,
				'lead_type':lead_type,
				'lead_source_id':self.env['source.master'].search([('name','=','Website')], limit=1).id,
				'isd_code_id':self.env['res.country.code'].search([('country_id', '=', self.env['res.country'].search([('name', '=', 'United Arab Emirates')]).id)], limit=1).id,
				'matching_listing':[(6, 0, [listing_id.id])],
				'is_matching_listing':True,
				'lead_req_ids':[(0,0,property_req)],
			})
		offered_unit_id = self.env['lead.offered.unit'].create({
				'listing_id':listing_id.id,
				'category_id':listing_id.category_id.id,
				'emirate_id':listing_id.emirate_id.id,
				'location_id':listing_id.location_id.id,
				'sub_location_id':listing_id.sub_location_id.id,
				'agent_id':listing_id.agent_id.id,
				'status':'Pending',
				'lead_id':lead_id.id,
			})
		self.status = 'Converted to Lead'
		self.lead_id = lead_id.id
		return

	@api.multi
	def reject_enquiry(self):
		self.status = 'Rejected'