from odoo import fields, models, api


class ResCountryCode(models.Model):
	_name = 'res.country.code'
	_rec_name = 'country_code'

	country_id = fields.Integer(string="Country Id")
	country_name = fields.Char(string="Country Name")
	country_code = fields.Char(string="Country Code")

	@api.model
	def _create_country_code(self):
		if not self.search([]).ids:
			for country in self.env['res.country'].search([]):
				self.create({
						'country_id':country.id,
						'country_name':country.name,
						'country_code':country.phone_code,
					})
	



	# @api.multi
	# def name_get(self):
	# 	result = []
	# 	for code in self:
	# 		name = str(code.country_code)
	# 		result.append((code.id, name))
	# 	return result