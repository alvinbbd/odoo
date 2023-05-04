from odoo import fields, models, api

class AuditTrail(models.Model):
	_name = 'analytics.audit.trail'

	# title = fields.Text(string="Title")

class MailMessage(models.Model):
	_inherit = "mail.message"

	model_name = fields.Char(string="Module Name")
	record_name = fields.Char(string="Reference")
	data = fields.Text("Data")
	body = fields.Html('Update Type', default='', sanitize_style=True, strip_classes=True)
	date = fields.Datetime('Datetime', default=fields.Datetime.now)

	@api.model
	def create(self, vals):
		res = super(MailMessage, self).create(vals)
		if res.model != False and res.res_id != False:
			model_id = self.env[res.model]
			ir_model_id = self.env['ir.model'].sudo().search([('model','=',res.model)])
			for line in res.sudo().tracking_value_ids:
				old_val = line.old_value_char if line.old_value_char else "nil"
				new_val = line.new_value_char if line.new_value_char else "nil"
				field = self.env['ir.model.fields'].sudo().search([('name','=',line.field),('model_id','=',ir_model_id.id)]).field_description
				if old_val == 'nil':
					body_data = str(field) + " : " + str(new_val) + "\n"
				else:
					body_data = str(field) + " : " + str(old_val) + " -> " + str(new_val) + "\n"
				if res.data:
					res.data += body_data
				else:
					res.data = body_data
			res.model_name = ir_model_id.name
			if res.res_id:
				record_id = model_id.sudo().search([('id','=',res.res_id)])
				if res.model == 'listing.listing':
					res.record_name = record_id.ref_name
				elif res.model == 'res.partner':
					res.record_name = record_id.ref_name
				elif res.model == 'atk.lead.lead':
					res.record_name = record_id.name
				elif res.model == 'lead.opportunity':
					res.record_name = record_id.id
				elif res.model == 'deal.deal':
					res.record_name = record_id.name
				elif res.model == 'crm.proforma.invoice':
					res.record_name = record_id.name
				elif res.model == 'crm.temporary.receipt':
					res.record_name = record_id.name
				elif res.model == 'crm.portal':
					res.record_name = record_id.name
				elif res.model == 'res.users':
					res.record_name = record_id.name + ", " + record_id.login
				elif res.model == 'res.company':
					res.record_name = record_id.name + ", " + record_id.code
				elif res.model == 'lead.rotation':
					res.record_name = record_id.name
				elif res.model == 'auto.action':
					res.record_name = record_id.ref
				elif res.model == 'listing.enquiry':
					res.record_name = record_id.name
				elif res.model == 'source.master':
					res.record_name = record_id.name
				elif res.model == 'res.location':
					res.record_name = record_id.name
				elif res.model == 'res.sub.location':
					res.record_name = record_id.name
				else:
					res.record_name = record_id.id
				
				for record in self.search([('res_id','=',res.res_id),('record_name','=',False)]):
					record.record_name = res.record_name

		return res