# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
import calendar

from odoo import fields, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import release
from datetime import datetime

class WebSettingsDashboard(http.Controller):

    @http.route('/ast/web_settings_dashboard/data', type='json', auth='user')
    def web_settings_dashboard_data(self, **kw):
        date_start = datetime.today().date()
        date_start = date_start.strftime("%Y-%m-%d 00:00:00")
        date_ends = datetime.today().date()
        date_end = date_ends.strftime("%Y-%m-%d 11:59:59")
        first_day = datetime.today().date().replace(day=1, )
        first_day = first_day.strftime("%Y-%m-%d 00:00:00")
        last_day = datetime.today().date().replace(
            day=calendar.monthrange(datetime.today().date().year, datetime.today().date().month)[1])
        last_day = last_day.strftime("%Y-%m-%d 11:59:59")
        new_leads = 0
        new_deals = 0
        network_leads = 0
        pool_leads = 0
        deal_progress = 0
        lead_progress = 0
        deal_closed = 0
        lead_closed = 0
        user = request.env.user.name
        # print("kkkkk    user     kkkkk",user)
        company_obj = request.env.user.company_ids.ids
        lead_obj = request.env['atk.lead.lead'].search([])
        deal_obj = request.env['deal.deal'].search([])
        lead_today_obj = lead_obj.search([('create_date', '<=', date_end),('create_date', '>=', date_start)])
        lead_pool_obj = lead_obj.search([('pool_status','=','Lead Pool')])
        network_pool_obj = lead_obj.search([('pool_status','=','Network Pool')])
        deal_today_obj = deal_obj.search([('create_date', '<=', date_end), ('create_date', '>=', date_start)])
        deal_progress_obj = deal_obj.search([('deal_status', '=', 'In Progress')])
        lead_progress_obj = lead_obj.search([('state','=','work_Progress')])
        deal_closed_obj = deal_obj.search([('deal_status', '=', 'Lost')])
        lead_closed_obj = lead_obj.search([('state', '=', 'closed')])
        # ('create_date', '<=', date_end),('create_date', '>=', first_day)
        agent_team = request.env.user.employee_ids.team_id.id
        user_type = request.env.user.employee_ids.emp_user_type.name
        deal_commission_obj = deal_obj.search([('create_date', '>=', first_day), ('create_date', '<=', last_day)])
        action_obj = request.env['action.action'].search([('company_id', 'in', company_obj)])

        commission_earned = 0
        commission_dict = {}
        largest_commission = 0
        team_name = ""
        commission_largest = 0
        second_largest = 0
        third_largest = 0
        name_agent = ""
        second_agent = ""
        third_agent = ""
        lead_no = 0
        deal_no = 0
        oldest_lead = 0
        oldest_deal = 0

        # for action in action_obj:
        #     action_user = action.agents_ids
        #     print("////////////",action_user)
        #     for users in action_user:
        #         print(";;;;;;;;;;;;",users.name)
        #         if user in users.name:
        #             if date_start < action.stop_datetime:
        #                 action_type = action.action_type
        #                 contact_id = action.contacts_ids.ref_name
        #                 listing_id = action.listing_id.ref_name
        #                 lead_id = action.lead_id.name
        #                 start_date = action.start_datetime
        #                 stop_date = action.stop_datetime
        #                 print(">>>>>>>>>>>>>>>",start_date)
        #                 print("aaaaaaaaaa", stop_date)
        #                 print("sssssssssssssss", contact_id)
        #                 print("aqqqqqqqqqqqq", listing_id)
        #                 print("eeeeeeeeee", lead_id)
        # for lead in lead_obj:
        #     lead_user = lead.agent_id
        #     if lead.future_action_date:
        #         future_action_date = lead.future_action_date
        #         lead_ref = lead.name
        #         # print("LLLLLLLLLLLLLLL", future_action_date)
        #         # print("ttttttttttttt",lead_ref)
        #     if lead.close_date_opportunity:
        #         close_date_opportunity = lead.close_date_opportunity
        #         lead_ref = lead.name
        #         # print("rrrrrrrrrrrrr", close_date_opportunity)
        #         # print("yyyyyyyyyyyy", lead_ref)

        if user_type == "Super Admin (IT)":
            for deal in deal_commission_obj:
                if deal.lead_agent.team_id.name:
                    if deal.lead_agent.team_id.name in commission_dict.keys():
                        commission_dict[deal.lead_agent.team_id.name]['commission'] += deal.gross_commission
                    else:
                        commission_dict[deal.lead_agent.team_id.name] = {'commission' : deal.gross_commission}

            for key in commission_dict:
                if largest_commission <= commission_dict[key]['commission']:
                    largest_commission = commission_dict[key]['commission']
                    team_name = key
        else:
            for deal in deal_commission_obj:
                if deal.lead_agent.team_id.id == agent_team:
                    commission_earned += deal.gross_commission
                    team_name = deal.lead_agent.team_id.name

        deal_curent_month_ids = request.env['agent.performance'].search([])
        for commissions in deal_curent_month_ids:
            current_month_commission = commissions.deals_yearly_ids
            for commission in current_month_commission:
                if commission.agent_id.name:
                    yearly_commission = commission.agent_id.team_id.name
                    # for commission_yr in yearly_commission:
                    if yearly_commission == team_name:
                        commission_month = commission.current_month
                        agent = commission.agent_id
                        if commission_largest <= commission_month:
                            third_largest = second_largest
                            third_agent = second_agent
                            second_largest = commission_largest
                            second_agent = name_agent
                            commission_largest = commission_month
                            name_agent = agent.name
                        elif second_largest < commission_month and commission_largest > commission_month:
                            third_largest = second_largest
                            third_agent = second_agent
                            second_largest = commission_month
                            second_agent = agent.name
                        elif third_largest > commission_month and second_largest < commission_month and commission_largest < commission_month:
                            third_largest = commission_month
                            third_agent = agent.name

        for lead in lead_today_obj:
            if lead:
                if lead.company_id.id in lead.env.user.company_ids.ids:
                    new_leads = new_leads+1

        for lead in lead_pool_obj:
            if lead:
                if lead.company_id.id in lead.env.user.company_ids.ids:
                    pool_leads = pool_leads+1

        for lead in network_pool_obj:
            if lead:
                if lead.company_id.id in lead.env.user.company_ids.ids:
                    network_leads = network_leads+1

        for deal in deal_today_obj:
            if deal:
                if deal.company_id.id in deal.env.user.company_ids.ids:
                    new_deals = new_deals+1

        for lead in lead_progress_obj:
            create_date = lead.create_date
            create_date = datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S')
            date = create_date.date()
            dates_no = (date_ends - date).days
            if lead:
                if lead.company_id.id in lead.env.user.company_ids.ids:
                    lead_progress = lead_progress + 1
                    if dates_no > 14:
                        lead_no = lead_no + 1
                    if oldest_lead <= dates_no:
                        oldest_lead = dates_no
                        lead_ref = lead.name
        for deal in deal_progress_obj:
            create_date = deal.create_date
            create_date = datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S')
            dates = create_date.date()
            dates_no = (date_ends - dates).days
            if deal:
                if deal.company_id.id in deal.env.user.company_ids.ids:
                    deal_progress = deal_progress + 1
                    if dates_no > 14:
                        deal_no = deal_no + 1
                    if oldest_deal <= dates_no:
                        oldest_deal = dates_no
                        deal_ref = deal.name

        for deal in deal_closed_obj:
            if deal:
                if deal.company_id.id in deal.env.user.company_ids.ids:
                    deal_closed = deal_closed+1

        for lead in lead_closed_obj:
            if lead:
                if lead.company_id.id in lead.env.user.company_ids.ids:
                    lead_closed = lead_closed+1



        return {
            'actions': {
                # 'action_type': action_type,'contact_id':contact_id,'listing_id':listing_id,'lead_id':lead_id,
                # 'start_date':start_date,'stop_date':stop_date
            },
            'leads': {
                'new_leads': new_leads, 'pool_leads':pool_leads, 'network_leads':network_leads

            },
            'lead_deal': {
                'new_leads': new_leads,'new_deals':new_deals, 'deal_progress':deal_progress,
                'lead_progress':lead_progress, 'deal_closed':deal_closed, 'lead_closed':lead_closed
            },
            'agent_status': {
                'largest_commission': largest_commission, 'team_name':team_name,
                'commission_largest':commission_largest, 'name_agent':name_agent, 'second_largest':second_largest,
                'second_agent':second_agent, 'third_largest':third_largest, 'third_agent':third_agent
            },
            'holding_time': {
                'lead_no': lead_no, 'deal_no':deal_no, 'oldest_lead':oldest_lead, 'oldest_deal':oldest_deal
            }
        }
