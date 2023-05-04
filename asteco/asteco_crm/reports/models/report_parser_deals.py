from odoo import fields, models, api, _
from datetime import datetime, timedelta
import calendar



class PrintDealsReportParser(models.AbstractModel):
    _name = 'report.asteco_crm.deal_report_pdf'

    @api.model
    def get_report_values(self, docids, data=None):

        deal_summary_details = {
            'deal_summary': self._get_deal_details(data),
            'data': data,
        }
        return deal_summary_details




    def _get_deal_details(self, data):
        deal_summary_list = []
        domain = [('create_date', '<=', data['end_date']), ('create_date', '>=', data['start_date'])]
        # user_id = self.env.user.employee_ids.id
        # child_ids = user_id.child_ids.ids

        if data['deal_type']:
            domain.append(('listing_type','=',data['deal_type']))
        if data['agent']:
            domain.append(('lead_agent','=',data['agent']))
        if data['property_type']:
            domain.append(('list_managed_status_id','=',data['property_type']))
        if data['team']:
            domain.append(('lead_agent.team_id', '=', data['team']))
        deal_ids = self.env['deal.deal'].sudo().search(domain)
        for deal in deal_ids:
            deal_summary_list.append({
                    'agent':deal.lead_agent.name or '',
                    'manager': deal.lead_agent.parent_id.name or '',
                    'team': deal.lead_agent.team_id.name or '',
                    'commission': deal.total_earned_commission_amount,
            })
        return deal_summary_list

