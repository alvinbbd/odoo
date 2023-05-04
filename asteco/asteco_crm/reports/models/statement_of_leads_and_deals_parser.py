from odoo import fields, models, api, _
from datetime import datetime,timedelta
import locale

class PrintLeadsAndDeals(models.AbstractModel):
	_name = 'report.asteco_crm.leads_and_deals_summery'
	
	@api.model
	def get_report_values(self, docids, data=None):
		statements_of_leads_and_deals2template = {
			'get_statement_details': self._get_statement_details(data),
			'data': data,
		}
		return statements_of_leads_and_deals2template

	def _get_statement_details(self, data):
		result = []

		domain = [('create_date','<=', data['date_end']), ('create_date', '>=', data['date_start'])]
		# domain1 = [('create_date','<=', data['date_end']), ('create_date', '>=', data['date_start'])]


		opertunity_report_ids = self.env['lead.opportunity'].search(domain)
		leads_from_leads = self.env['atk.lead.lead'].search(domain)
		deals_closed = self.env['crm.temporary.receipt'].search(domain)

		if data['agent']:
			domain.append(('lead_agent','=',data['agent']))
		if data['team']:
			domain.append(('lead_agent.team_id', '=', data['team']))
		report_from_deal = self.env['deal.deal'].search(domain)
		
		number_of_leads = 0
		qualified_leads = 0
		qwon = 0
		qlost = 0
		vwon = 0
		vlost = 0
		cdwon = 0
		cdlost = 0
		nwon = 0
		nlost = 0
		cewon = 0
		celost = 0
		viewings_leads = 0
		number_of_deals_converted = 0
		number_of_deals_closed = 0
		commision_earned = 0
		number_of_negotiation = 0

		for leads in leads_from_leads:
			if leads.company_id.id == data['company']:
				number_of_leads = number_of_leads + 1

		for opertunity in opertunity_report_ids:
			if opertunity.company_id.id == data['company']:
				if opertunity.stage_id.name == 'Qualified':
					qualified_leads = qualified_leads + 1
					if opertunity.stage_id.name == opertunity.state:
						qwon = qwon + 1
					elif opertunity.state == 'Lost':
						qlost = qlost + 1

				elif opertunity.stage_id.name == 'Viewings':
					viewings_leads = viewings_leads + 1
					if opertunity.stage_id.name == opertunity.state:
						vwon = vwon + 1
					elif opertunity.state == 'Lost':
						vlost = vlost + 1

				elif opertunity.stage_id.name == 'Converted to Deal':
					number_of_deals_converted = number_of_deals_converted + 1
					if opertunity.stage_id.name == opertunity.state:
						cdwon = cdwon + 1
					elif opertunity.state == 'Lost':
						cdlost = cdlost + 1

				elif opertunity.stage_id.name == 'Negotiation':
					number_of_negotiation = number_of_negotiation + 1
					if opertunity.stage_id.name == opertunity.state:
						nwon = nwon + 1
					elif opertunity.state == 'Lost':
						nlost = nlost + 1

		for closed_deal in deals_closed:
			if closed_deal.company_id.id == data['company']:
				number_of_deals_closed = number_of_deals_closed + 1	

		for deal in report_from_deal:
			if deal.company_id.id == data['company']:
				if deal.deal_status == 'Deposit Received':
					cewon = cewon + 1
				if deal.deal_status == 'Lost':
					celost = celost + 1

		dict_lead_and_deals = {
			'number_of_leads' : number_of_leads,
			'qualified_leads' : qualified_leads,
			'qwon' : qwon,
			'qlost' : qlost,
			'viewings_leads' : viewings_leads,
			'vwon' : vwon,
			'vlost' : vlost,
			'number_of_deals_converted' : number_of_deals_converted,
			'cdwon' : cdwon,
			'cdlost' : cdlost,
			'number_of_negotiation' : number_of_negotiation,
			'nwon' : nwon,
			'nlost' : nlost,
			'number_of_deals_closed' : number_of_deals_closed,
			'cewon' : cewon,
			'celost' : celost,
		}
		return dict_lead_and_deals