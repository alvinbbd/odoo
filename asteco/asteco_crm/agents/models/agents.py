import calendar

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from datetime import datetime, timedelta


class AgentPerformance(models.Model):
    _name = 'agent.performance'


    deals_monthly_ids = fields.One2many("deal.deal","agent_performance_id", string="Commission (Monthly)", readonly=True)
    deals_yearly_ids = fields.One2many("commission.yearly", "deals_commission_id", string="Commission (Yearly)", readonly=True)
    leads_confidence_detailed = fields.One2many("atk.lead.lead", "agent_performance_id", string="Agent Confidence Score (Detailed)", readonly=True)
    agent_confidence_score_detail = fields.One2many("agent.lead.score", "agents_score_detailed", readonly=True)
    agent_score_summary = fields.One2many('hr.employee', 'agent_performance_summary', readonly=True)
    company_total = fields.Float(compute="_get_company_total")
    agent_total = fields.Float(compute="_get_agent_total")
    name = fields.Char()
    curr_sales_period_mnth = fields.Char(compute="_get_curr_mnth")
    curr_sales_period_yr = fields.Char(compute="_get_curr_sales_period_yr")
    agent_id = fields.Many2one("hr.employee", store=True)
    add_points = fields.Integer('Add Points', store=True)
    document = fields.Binary(string='Document Upload', attachment=True, store=True)
    agent_update_score = fields.One2many("agent.lead.score", "agent_score_update", readonly=True)
    date_start = fields.Datetime()
    date_end = fields.Datetime()
    date_from = fields.Datetime()
    date_to = fields.Datetime()
    agent_filter_id = fields.Many2one('hr.employee', store=False)
    agent_ids = fields.Many2one('hr.employee', store=False)
    filename = fields.Char('File Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)




    @api.multi
    def _get_curr_mnth(self):
        self.curr_sales_period_mnth = datetime.now().strftime("%b-%Y")

    @api.multi
    def _get_curr_sales_period_yr(self):
        self.curr_sales_period_yr = "Jan - " + str(datetime.now().year) + " to " + "Dec - " + str(datetime.now().year)

    @api.depends('deals_monthly_ids')
    def _get_company_total(self):
        for record in self:
            for deal in record.deals_monthly_ids:
                record.company_total = record.company_total + deal.total_company_earnings

    @api.depends('deals_monthly_ids')
    def _get_agent_total(self):
        for record in self:
            for deal in record.deals_monthly_ids:
                record.agent_total = record.agent_total + deal.total_earned_commission_amount

    @api.multi
    def _get_user_type(self):
        if self.env.user.has_group('asteco_crm.group_director') or self.env.user.has_group('asteco_crm.group_coordinator') or \
                self.env.user.has_group('asteco_crm.group_super_user') or self.env.user.has_group('asteco_crm.group_super_admin'):
            return 'all'
        elif self.env.user.has_group('asteco_crm.group_sales_manager'):
            return 'sales'
        elif self.env.user.has_group('asteco_crm.group_work_manager'):
            return 'work_manager'
        elif self.env.user.has_group('asteco_crm.group_agent_broker'):
            return 'agent'
        else:
            return False

    @api.multi
    def _get_user_agents(self):
        user_type = self._get_user_type()
        company_id = self.env.user.company_id.id
        if user_type == 'all':
            # sales_manager_id = self.env.ref('asteco_crm.sales_manager')
            sales_manager_id = self.env.ref('asteco_crm.work_manager')
            sales_manager_id += self.env.ref('asteco_crm.agent_broker')
            domain = [('emp_user_type', 'in', sales_manager_id.ids),('company_id','=', company_id)]
            return self.env['hr.employee'].search(domain)
        elif user_type == 'sales':
            user_id = self.env.user.id
            employee_id = self.env['hr.employee'].sudo().search([('user_id','=', user_id)])
            if employee_id:
                employee_ids = self.env['hr.employee'].sudo().search([('parent_id', 'in', employee_id.ids)])
                if employee_ids:
                    employee_ids += self.env['hr.employee'].sudo().search([('parent_id', 'in', employee_ids.ids), ('company_id', '=', company_id)])
                return employee_ids
        elif user_type == 'work_manager':
            user_work_manager = self.env.user.id
            employee_work_manager_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_work_manager)])
            if employee_work_manager_id:
                agent_work_manager = employee_work_manager_id + self.env['hr.employee'].sudo().search([
                    ('parent_id', '=', employee_work_manager_id.id), ('company_id','=', company_id)])
                return agent_work_manager
        elif user_type == 'agent':
            user_agent = self.env.user.id
            employee_agent = self.env['hr.employee'].search([('user_id', '=', user_agent),
                                                             ('company_id','=', company_id)])
            return employee_agent
        else:
            return False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AgentPerformance, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        user_type = self._get_user_type()
        agent_ids = self._get_user_agents()

        first_day = datetime.today().date().replace(day=1, )
        first_day = first_day.strftime("%Y-%m-%d 00:00:00")
        last_day = datetime.today().date().replace(
            day=calendar.monthrange(datetime.today().date().year, datetime.today().date().month)[1])
        last_day = last_day.strftime("%Y-%m-%d 11:59:59")
        rec = self.env.ref('asteco_crm.agent_performance_report')
        yearl_vals = {}
        deal_id = self.env['deal.deal']

        if agent_ids:
            #Monthly Commission
            deal_curent_month_ids = deal_id.search([('create_date', '<=', last_day), ('create_date', '>=', first_day)])
            rec.deals_monthly_ids = [(6, 0, deal_curent_month_ids.ids)]

            # Yearly commission
            deals_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-01-01"),
                                                  ('create_date', '<=', str(datetime.today().year) + "-12-31")])

            for deal in deals_ids:
                if deal.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal.shared_with_id.id]['yearly'] = int(yearl_vals[deal.shared_with_id.id]['yearly']) + int(deal.total_earned_commission_amount)
                else:
                    yearl_vals[deal.shared_with_id.id] = {
                        'agent_id': deal.shared_with_id.id,
                        'yearly': deal.total_earned_commission_amount,
                        'current': 0.00,
                        'half': 0.00,
                        'q1': 0.00,
                        'q2': 0.00,
                        'q3': 0.00,
                        'q4': 0.00,
                    }

            for deal_current_mnth in deal_curent_month_ids:
                if deal_current_mnth.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_current_mnth.shared_with_id.id]['current'] = int(
                        yearl_vals[deal_current_mnth.shared_with_id.id]['current']) + int(
                        deal_current_mnth.total_earned_commission_amount)
                else:
                    yearl_vals[deal_current_mnth.shared_with_id.id] = {
                        'agent_id': deal_current_mnth.shared_with_id.id,
                        'current': deal_current_mnth.total_earned_commission_amount,
                    }

            #Half Yearly
            deals_half_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-01-01"),
                                                           ('create_date', '<=', str(datetime.today().year) + "-06-30")])

            for deal_half in deals_half_ids:
                if deal_half.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_half.shared_with_id.id]['half'] = int(
                        yearl_vals[deal_half.shared_with_id.id]['half']) + int(
                        deal_half.total_earned_commission_amount)
                else:
                    yearl_vals[deal_half.shared_with_id.id] = {
                        'agent_id': deal_half.shared_with_id.id,
                        'half': deal_half.total_earned_commission_amount,
                    }

            # Q1
            deals_q1_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-01-01"),
                                                         ('create_date', '<=', str(datetime.today().year) + "-03-31")])

            for deal_q1 in deals_q1_ids:
                if deal_q1.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_q1.shared_with_id.id]['q1'] = int(
                        yearl_vals[deal_q1.shared_with_id.id]['q1']) + int(
                        deal_q1.total_earned_commission_amount)
                else:
                    yearl_vals[deal_q1.shared_with_id.id] = {
                        'agent_id': deal_q1.shared_with_id.id,
                        'q1': deal_q1.total_earned_commission_amount,
                    }
            # Q2
            deals_q2_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-04-01"),
                                                         ('create_date', '<=', str(datetime.today().year) + "-06-30")])

            for deal_q2 in deals_q2_ids:
                if deal_q2.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_q2.shared_with_id.id]['q2'] = int(
                        yearl_vals[deal_q2.shared_with_id.id]['q2']) + int(
                        deal_q2.total_earned_commission_amount)
                else:
                    yearl_vals[deal_q2.shared_with_id.id] = {
                        'agent_id': deal_q2.shared_with_id.id,
                        'q2': deal_q2.total_earned_commission_amount,
                    }

            # Q3
            deals_q3_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-07-01"),
                                                         ('create_date', '<=', str(datetime.today().year) + "-09-30")])

            for deal_q3 in deals_q3_ids:
                if deal_q3.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_q3.shared_with_id.id]['q3'] = int(
                        yearl_vals[deal_q3.shared_with_id.id]['q3']) + int(
                        deal_q3.total_earned_commission_amount)
                else:
                    yearl_vals[deal_q3.shared_with_id.id] = {
                        'agent_id': deal_q3.shared_with_id.id,
                        'q3': deal_q3.total_earned_commission_amount,
                    }

            # Q4
            deals_q4_ids = deal_id.search([('create_date', '>=', str(datetime.today().year) + "-10-01"),
                                                         ('create_date', '<=', str(datetime.today().year) + "-12-31")])

            for deal_q4 in deals_q4_ids:
                if deal_q4.shared_with_id.id in yearl_vals.keys():
                    yearl_vals[deal_q4.shared_with_id.id]['q4'] = int(yearl_vals[deal_q4.shared_with_id.id]['q4']) + int(
                        deal_q4.total_earned_commission_amount)
                else:
                    yearl_vals[deal_q4.shared_with_id.id] = {
                        'agent_id': deal_q4.shared_with_id.id,
                        'q4': deal_q4.total_earned_commission_amount,
                    }

            rec.deals_yearly_ids = False
            for key in yearl_vals:
                comm_id = self.env['commission.yearly'].create({
                    'agent_id': yearl_vals[key]['agent_id'],
                    'yearly': yearl_vals[key]['yearly'],
                    'half_yearly': yearl_vals[key]['half'],
                    'current_month': yearl_vals[key]['current'],
                    'quarter_1' : yearl_vals[key]['q1'],
                    'quarter_2': yearl_vals[key]['q2'],
                    'quarter_3': yearl_vals[key]['q3'],
                    'quarter_4': yearl_vals[key]['q4'],
                    'deals_commission_id': rec.id,
                })

            leads_ids = self.env['atk.lead.lead'].search([('agent_id', 'in', agent_ids.ids)])
            rec.leads_confidence_detailed = [(6, 0, leads_ids.ids)]
            rec.agent_score_summary = [(6, 0, agent_ids.ids)]
            agent_score_ids = self.env['agent.lead.score'].search([('agent_id', 'in', agent_ids.ids)])
            rec.agent_confidence_score_detail = [(6, 0, agent_score_ids.ids)]
            return res

    @api.model
    def create(self, vals):
        res = super(AgentPerformance, self).create(vals)
        res.name = 'Agent Performance'
        return res

    @api.multi
    def submit(self):
        res = self.env['agent.lead.score'].create({
            'agent_id': self.agent_id.id,
            'score': self.add_points,
            'document': self.document,
            'filename': self.filename,
        })
        self.agent_id = False
        self.add_points = False
        self.document = False

        self.agent_update_score += res


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            result.append((record.id, name))
        return result

    @api.onchange('agent_filter_id', 'date_start', 'date_end')
    def _onchange_agent(self):
        agent_ids = self._get_user_agents()
        self.agent_confidence_score_detail = False
        if self.agent_filter_id:
            agents_score_ids = self.env['agent.lead.score'].search([('agent_id', '=', self.agent_filter_id.id),
                                                                    ('create_date', '>=', self.date_start), ('create_date', '<=', self.date_end)])
            self.agent_confidence_score_detail = [(6, 0, agents_score_ids.ids)]
        elif agent_ids:
            agent_score_ids = self.env['agent.lead.score'].search([('agent_id', 'in', agent_ids.ids)])
            self.agent_confidence_score_detail = [(6, 0, agent_score_ids.ids)]

    @api.onchange('agent_ids')
    def _onchange_agent_summary(self):
        agent_ids = self._get_user_agents()
        self.agent_score_summary = False
        if self.agent_ids:
            agent_scores_ids = self.env['hr.employee'].search([('id', '=', self.agent_ids.id)])
            self.agent_score_summary = [(6, 0, agent_scores_ids.ids)]
        elif self.date_from:
            agent_date_filter_ids = self.env['hr.employee'].search([('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])
            self.agent_score_summary = [(6, 0, agent_date_filter_ids.ids)]
        elif agent_ids:
            agents_scores_ids = self.env['hr.employee'].search([('id', 'in', agent_ids.ids)])
            self.agent_score_summary = [(6, 0, agents_scores_ids.ids)]





class CommissionYearly(models.Model):
    _name = 'commission.yearly'
    deals_commission_id = fields.Many2one('agent.performance')

    deal_id = fields.Many2one('deal.deal', String="Deal ID")
    agent_id = fields.Many2one("hr.employee", string="Agent")
    current_month = fields.Float("Current Month")
    quarter_1 = fields.Float("Quarter 1")
    quarter_2 = fields.Float("Quarter 2")
    quarter_3 = fields.Float("Quarter 3")
    quarter_4 = fields.Float("Quarter 4")
    half_yearly = fields.Float("Half Yearly")
    yearly = fields.Float("Yearly")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


# class AgentConfidenceScoreDetailed(models.Model):
#     _name = 'agent.confidence.score'
#
#     agent_performance_detailed = fields.Many2one('agent.performance')
#
#     lead_id = fields.Many2one('atk.lead.lead', string="Reference #")
#     date = fields.Datetime(string="Date")
#     agent_id = fields.Many2one('hr.employee', string="Agent Broker")
#     points = fields.Integer(string="Points")


# class AgentConfidenceScoreSummary(models.Model):
#     _name = 'agent.score.summary'
#
#     confidence_score_summary = fields.Many2one('agent.performance')
#
#     manager = fields.Many2one("hr.employee", string="manager")
#     agent_broker = fields.Many2one("hr.employee", string="Agents")
#     current_score = fields.Char()


class AgentLeadScore(models.Model): # Stores lead wise score of agents
    _name = 'agent.lead.score'

    slno = fields.Integer("No.", compute="_sequence_ref")
    agent_id = fields.Many2one('hr.employee', required=1)
    lead_id = fields.Many2one('atk.lead.lead')
    score = fields.Integer()
    document = fields.Binary(attachment=True, readonly=True)
    agents_score_detailed = fields.Many2one('agent.performance')
    agent_score_update = fields.Many2one('agent.performance')
    date_and_time = fields.Datetime(default=datetime.now(), required=True)
    filename = fields.Char('File Name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


    @api.model
    def create(self, vals):
        res = super(AgentLeadScore, self).create(vals)
        if res.agent_id and res.score:
            res.agent_id.confidence_score += res.score
        return res

    @api.depends('agent_score_update.agent_update_score', 'agent_score_update.agent_update_score.agent_id')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.agent_score_update.agent_update_score:
                no += 1
                l.slno = no



