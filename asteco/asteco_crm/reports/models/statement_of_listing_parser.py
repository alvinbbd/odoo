from odoo import fields, models, api, _
from datetime import datetime,timedelta
import locale

class PrintListingInNewState(models.AbstractModel):
	_name = 'report.asteco_crm.listing_report_summery'
	
	@api.model
	def get_report_values(self, docids, data=None):
		statements_of_listing2template = {
			'get_statement_details': self._get_statement_details(data),
			'data': data,
			'name' : 'TEDT',
		}
		return statements_of_listing2template

	def _get_statement_details(self, data):
		result = []		
		domain = []
		if data['list_type']:
			domain = [('listing_type','=',data['list_type'])]
		list_report_ids = self.env['listing.listing'].search(domain)
		if list_report_ids:
			for listing in list_report_ids:
				single_statement = {
					'ref':listing.ref_name,
					'listing_type':listing.listing_type,
					'customer_id':listing.customer_id.name,
					'listing_status':listing.listing_status,
					'category_id':listing.category_id.name,
					'emirate_id':listing.emirate_id.name,
					'location_id':listing.location_id.name,
					'sub_location_id':listing.sub_location_id.name,
					'agent_id':listing.agent_id.name,
				}
				result.append(single_statement)
			return result
		return False		
