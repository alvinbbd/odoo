from odoo import fields, models, api, _
from datetime import datetime,timedelta
import locale

class PrintLeadsLostReport(models.AbstractModel):
	_name = 'report.asteco_crm.leads_lost_pdf'
	
	@api.model
	def get_report_values(self, docids, data=None):
		statements_of_leads_lost_template = {
			'get_statement_details': self._get_statement_details(data),
			'data': data,
		}
		return statements_of_leads_lost_template


	def _get_statement_details(self, data):
		result = []		
		domain = [('create_date', '<=', data['end_date']), ('create_date', '>=', data['start_date']),('state','=','Lost')]
		opportunity_ids = self.env['lead.opportunity'].search(domain)
		for opportunity in opportunity_ids:
			current_date = datetime.now()
			d1 = current_date
			d2 = datetime.strptime(opportunity.create_date,'%Y-%m-%d %H:%M:%S')
			difference = d1-d2
			days = difference.days
			if days==0:
				days = 1
			single_statement = {
				'ref':opportunity.lead_id.name,
				'date_assigned':opportunity.lead_id.create_date,
				'days_worked_on':days,
				'viewings':opportunity.lead_id.viewing_count,
				'stage_of_loss':opportunity.stage_id.name,
				'reason_for_loss':opportunity.lead_id.loss_reason.name,	
			}
			result.append(single_statement)
		return result