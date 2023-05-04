from odoo import fields, models, api

class DocumentManagement(models.Model):
	_name = 'analytics.document.management'

	# title = fields.Text(string="Title")
	new_template = fields.Selection([('Listing','Listing'),('Lead','Lead'),('Deal','Deal'),('Contact','Contact')])