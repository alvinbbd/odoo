from odoo import fields, models, api, _
from datetime import datetime, timedelta
import calendar
import locale

class DealNumberReport(models.AbstractModel):
	_name='report.asteco_crm.deal_number_report_pdf'

	@api.model
	def get_report_values(self, docids, data=None):
		deal_number_details = {
		'deal_summary': self._get_number_details(data),
		'data': data,
		}
		return deal_number_details	

	def _get_number_details(self,data):
		domain = [('create_date','<=', data['end_date']), ('create_date', '>=', data['start_date'])]
		if data['company']:
			domain.append(('company_id','=',data['company']))
		if data['agent']:
			domain.append(('lead_agent','=',data['agent']))
		if data['listing_type']:
			domain.append(('listing_type','=',data['listing_type']))
		if data['stock_type']:
			if data['stock_type'] == 'asteco_stock':
				domain.append(('listing_id.managed_status_id','in',[self.env.ref('asteco_crm.managed_status_1').id,self.env.ref('asteco_crm.managed_status_2').id]))
			elif data['stock_type'] == 'non_asteco':
				domain.append(('listing_id.managed_status_id','=',[self.env.ref('asteco_crm.managed_status_3').id]))
		deal_ids = self.env['deal.deal'].search(domain)
		company_dict = {}
		for deal in deal_ids:
			if deal.listing_id.managed_status_id.name in ['Managed', 'Exclusive']:
				stock = "Asteco Stock"
			else:
				stock = "Non-Asteco Stock"

			if deal.company_id.id in company_dict.keys():
				if stock in company_dict[deal.company_id.id]['data']:
					if deal.listing_type in company_dict[deal.company_id.id]['data'][stock]:
						company_dict[deal.company_id.id]['data'][stock][deal.listing_type] += 1
					else:
						company_dict[deal.company_id.id]['data'][stock][deal.listing_type] = 1
				else:
					company_dict[deal.company_id.id]['data'][stock] = {
							deal.listing_type : 1,
						}
			else:
				company_dict[deal.company_id.id] = {
					'name' : deal.company_id.name,
					'data' : {
						stock : { deal.listing_type : 1
						}
					}
				}
		return company_dict