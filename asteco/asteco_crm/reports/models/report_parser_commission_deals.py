from odoo import fields, models, api, _
from datetime import datetime, timedelta
import calendar



class PrintDealsReportParser(models.AbstractModel):
    _name = 'report.asteco_crm.deal_commission_report_pdf'

    @api.model
    def get_report_values(self, docids, data=None):

        deal_commission_summary_details = {
            'deal_commission_summary': self._get_deal_commission_details(data),
            'data': data,
        }
        return deal_commission_summary_details

    def _get_deal_commission_details(self, data):

        deal_commission_summary_list = []

        domain = [('create_date', '<=', data['date_to']), ('create_date', '>=', data['date_from'])]
        rec = self.env.ref('asteco_crm.agent_performance_report')
        deal_ids = rec.deals_yearly_ids
        for deal in deal_ids:
            deal_commission_summary_list.append({
                'agent' : deal.agent_id.name,
                'current_month' : deal.current_month,
                'q1' : deal.quarter_1,
                'q2' : deal.quarter_2,
                'q3': deal.quarter_3,
                'q4': deal.quarter_4,
                'half_yearly': deal.half_yearly,
                'yearly' : deal.yearly

            })
        return deal_commission_summary_list

