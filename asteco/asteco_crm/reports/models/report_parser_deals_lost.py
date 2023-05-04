from odoo import fields, models, api, _
from datetime import datetime,timedelta
import locale

class PrintDealsLostReport(models.AbstractModel):
	_name = 'report.asteco_crm.deals_lost_pdf'
	
	@api.model
	def get_report_values(self, docids, data=None):
		statements_of_deals_lost_template = {
			'get_statement_details': self._get_statement_details(data),
			'data': data,
		}
		return statements_of_deals_lost_template


	def _get_statement_details(self, data):
		result = []		
		domain = [('create_date', '<=', data['end_date']), ('create_date', '>=', data['start_date']),('stage_id','=','Converted to Deal')]
		
		# domain(('deal_status','=','Lost'))
		opportunity_ids = self.env['lead.opportunity'].search(domain)
		for opportunity in opportunity_ids:
			if opportunity.deal_id.deal_status == 'Lost':
				current_date = datetime.now()
				d1 = current_date
				d2 = datetime.strptime(opportunity.create_date,'%Y-%m-%d %H:%M:%S')
				difference = d1-d2
				days = difference.days
				if days==0:
					days = 1
				single_statement = {
				'deal_ref':opportunity.deal_id.name,
				'associated_lead_ref':opportunity.lead_id.name,
				'date_assigned':opportunity.deal_id.create_date,
				'days_worked_on':days,
				'viewings':opportunity.lead_id.viewing_count,
				'stage_of_loss':opportunity.stage_id.name,
				'reason_for_loss':opportunity.deal_id.deal_loss_reason.name,	
				}
				result.append(single_statement)
		return result