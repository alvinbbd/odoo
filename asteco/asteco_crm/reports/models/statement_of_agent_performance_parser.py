from odoo import fields, models, api, _
from datetime import datetime, timedelta
import locale


class PrintAgentPerformancePreview(models.AbstractModel):
    _name = 'report.asteco_crm.agent_performance_summery'

    @api.model
    def get_report_values(self, docids, data=None):
        statements_of_agent_performance2template = {
            'get_statement_details': self._get_statement_details(data),
            'data': data,
        }
        return statements_of_agent_performance2template

    def _get_statement_details(self, data):
        result = []
        performance_dict = {}
        # number_of_leads = 0
        # qualified_leads = 0
        # viewings_leads = 0
        # number_of_deals_converted = 0
        # number_of_deals_closed = 0
        # commision_earned = 0
        domain = [('create_date', '<=', data['date_end']), ('create_date', '>=', data['date_start'])]

        opertunity_report_ids = self.env['lead.opportunity'].search(domain)

        report_from_deal = self.env['deal.deal'].search(domain)
        leads_of_agent = self.env['atk.lead.lead'].search(domain)

        deals_closed = self.env['crm.temporary.receipt'].search(domain)

        agents_in_users = self.env['hr.employee'].search([])
        for agent in agents_in_users:
            number_of_leads = 0
            qualified_leads = 0
            viewings_leads = 0
            negotiation_leads = 0
            number_of_deals_converted = 0
            number_of_deals_closed = 0
            commision_earned = 0
            if agent.company_id.id == data['company']:

                if opertunity_report_ids:
                    for lead in leads_of_agent:
                        if lead.agent_id == agent:
                            number_of_leads = number_of_leads + 1

                    for opertunity in opertunity_report_ids:
                        if opertunity.assign_id == agent:

                            # number_of_leads = number_of_leads + 1

                            if opertunity.stage_id.name == 'Qualified':
                                qualified_leads = qualified_leads + 1

                            elif opertunity.stage_id.name == 'Viewings':
                                viewings_leads = viewings_leads + 1

                            elif opertunity.stage_id.name == 'Negotiation':
                                negotiation_leads = negotiation_leads + 1

                            elif opertunity.stage_id.name == 'Converted to Deal':
                                number_of_deals_converted = number_of_deals_converted + 1

                    # elif opertunity.state == 'Lost':
                    # 	number_of_deals_closed = number_of_deals_closed + 1
                    for closed_deal in deals_closed:
                        if closed_deal.agent_id == agent:
                            number_of_deals_closed = number_of_deals_closed + 1

                    for deal in report_from_deal:
                        if deal.lead_agent == agent:
                            commision_earned = commision_earned + deal.gross_commission
                    performance_dict = {
                        'agent_name': agent.name,
                        'manager': agent.parent_id.name,
                        'number_of_leads': number_of_leads,
                        'qualified_leads': qualified_leads,
                        'viewings_leads': viewings_leads,
                        'negotiation_leads': negotiation_leads,
                        'number_of_deals_converted': number_of_deals_converted,
                        'number_of_deals_closed': number_of_deals_closed,
                        'commision_earned': commision_earned,
                    }
                if performance_dict:
                    result.append(performance_dict)
        return result