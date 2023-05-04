import pytz

from odoo import fields, models, api
import calendar
from datetime import datetime, timedelta, date, time


class Reports(models.TransientModel):
	_name = 'analytics.reports'
	# _inherit = ['listing.listing']
	def _time_zone(self):
		user_tz = self.env.user.tz or "Asia/Dubai"
		display_date_result = datetime.now(pytz.timezone(user_tz))
		return display_date_result.strftime("%d-%m-%Y %H:%M %S")

	name = fields.Char(default="Reports")

	# date_filter = fields.Datetime()
	report_type = fields.Selection([('deal_report','Deal Report'),('listing_report','Listing Report'),('agent_performance_report', 'Agent Performance Reports'),('commission_received_report','Commission Received Report'), ('leads_lost_report','Leads Lost Report'),('deals_lost_report','Deals Lost Report'),('leads_and_deals_report','Leads And Deals Report'), ('asteco_and_non_asteco_report','Asteco and Non-Asteco Stock')])
	# ('agent_performance_report', 'Agent Performance Reports'),
	# date_start = fields.Datetime(default=lambda *a: datetime.now().replace(day=1, ))
	date_start = fields.Datetime()
	# date_end = fields.Datetime(default=lambda *a: datetime.today().date().replace(
	# 	day=calendar.monthrange(datetime.today().date().year, datetime.today().date().month)[1]))
	date_end = fields.Datetime()

	deal_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')])
	list_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')], string="Listing Type")
	agent = fields.Many2one('hr.employee')
	# team = fields.Selection([('all', 'All'), ('separate', 'Separate')])
	# property_type = fields.Selection(
		# [('all', 'All'), ('managed', 'Managed'), ('exclusive', 'Exclusive'), ('open_market', 'Open Market')])
	# stock_type = fields.Selection([('all', 'All'),('asteco_stock','Asteco'),('open_market', 'Open Market')])
	stock_type = fields.Selection([('all', 'All'),('asteco_stock', 'Asteco Stock'), ('non_asteco', 'Non-Asteco')],string='Property Type')
	listing_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')],string = "Listing Type")
	company = fields.Many2one('res.company',string="Company")
	date_filter = fields.Selection([('Today','Today'),('Yesterday','Yesterday'),('Last 7 Days','Last 7 Days'),('Last 30 Days','Last 30 Days'),('This Month','This Month'),('Last Month','Last Month'),('Custom Range','Custom Range')], default='Today')

	# Date Filter
	@api.onchange('date_filter')
	def _onchange_date_filter(self):
		today = date.today()

		if self.date_filter == 'Today':
			day = today
			self.date_end = datetime.now()

		elif self.date_filter == 'Yesterday':
			day = today - timedelta(days = 1)
			self.date_end = day.strftime('%Y-%m-%d 23:59:59')

		elif self.date_filter == 'Last 7 Days':
			day = today - timedelta(days = 7)
			self.date_end = datetime.now()

		elif self.date_filter == 'Last 30 Days':
			day = today - timedelta(days = 30)
			self.date_end = datetime.now()

		elif self.date_filter == 'This Month':
			day = datetime.now().replace(day = 1)
			self.date_end = datetime.now()

		elif self.date_filter == 'Last Month':
			first = today.replace(day = 1)
			lastMonth = first - timedelta(days=1)
			day = lastMonth.replace(day = 1)
			self.date_end = lastMonth.strftime('%Y-%m-%d 23:59:59')
		else:
			return
		if day:
			self.date_start = datetime.combine(day, time())
			# self.date_start = day.strftime('%Y-%m-%d 23:59:59')
			# self.date_end = datetime.now()


# <<<<<<<<<<<<<<<<<<<<<<<<<<< HEAD
# 	# team = fields.Selection([('all', 'All'), ('separate', 'Separate')])
# 	# property_type = fields.Selection(
# 		# [('all', 'All'), ('managed', 'Managed'), ('exclusive', 'Exclusive'), ('open_market', 'Open Market')])
# 	# stock_type = fields.Selection([('all', 'All'),('asteco_stock','Asteco'),('open_market', 'Open Market')])
# 	stock_type = fields.Selection([('all', 'All'),('asteco_stock', 'Asteco Stock'), ('non_asteco', 'Non-Asteco')],string='Property Type')
# 	listing_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')],string = "Listing Type")
# 	company = fields.Many2one('res.company',string="Company")
# 	# @api.onchange('report_type')
# 	# def _onchange_report_type(self):
# 	# 	if self.report_type == 'deal_report':
# 	# @api.multi
#  #    def get_id(self):
#  #    	return self.env.user.employee_ids.id
        
# 	@api.multi
# 	def print_report(self):
# 		# data = {
# 		# 	'start_date':self.date_start,
# 		# 	'end_date':self.date_end,
# 		# }
# 		if self.report_type == 'asteco_and_non_asteco_report':
# 			data={
# 				'start_date':self.date_start,
# 				'end_date':self.date_end,
# 				'stock_type':self.stock_type,
# 				'listing_type':self.listing_type,
# 				'company':self.company.id,
# 				'agent':self.agent.id,

# 			}
# 			return self.env.ref('asteco_crm.report_deal_number_pdf').report_action(self,data)

# 		# if self.report_type == 'deal_report':
# 		# 	return self.env.ref('asteco_crm.report_deal_pdf').report_action(self,data)
# 		# # elif self.report_type == 'listing_report':
# 		# 	return self.env.ref('asteco_crm.deal_report_pdf').report_action(self)
# 		if self.report_type == 'leads_lost_report':
# =======>>>>>>>>>>>>>>>>>>>>>>>>
	team = fields.Many2one('asteco.sale.team')
	property_type = fields.Many2one('listing.managed.status')
	company = fields.Many2one('res.company')

	# property_type = fields.Selection(
		# [('all', 'All'), ('managed', 'Managed'), ('exclusive', 'Exclusive'), ('open_market', 'Open Market')])

	@api.multi
	def _get_user_type(self):
		if self.env.user.has_group('asteco_crm.group_director') or self.env.user.has_group(
				'asteco_crm.group_coordinator') or \
				self.env.user.has_group('asteco_crm.group_super_user') or self.env.user.has_group(
			'asteco_crm.group_super_admin'):
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
		if user_type == 'all':
			users_id = self.env.user.id
			employees_id = self.env['hr.employee'].sudo().search([('user_id', '=', users_id)])
			# sales_manager_id = self.env.ref('asteco_crm.sales_manager')
			sales_manager_id = self.env.ref('asteco_crm.work_manager')
			sales_manager_id += self.env.ref('asteco_crm.agent_broker')
			domain = [('emp_user_type', 'in', sales_manager_id.ids)]
			return self.env['hr.employee'].search(domain)
		elif user_type == 'sales':
			user_id = self.env.user.id
			employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)])
			if employee_id:
				employee_ids = self.env['hr.employee'].sudo().search([('parent_id', 'in', employee_id.ids)])
				if employee_ids:
					employee_ids += self.env['hr.employee'].sudo().search(
						[('parent_id', 'in', employee_ids.ids)])
				return employee_ids
		elif user_type == 'work_manager':
			user_work_manager = self.env.user.id
			employee_work_manager_id = self.env['hr.employee'].sudo().search([('user_id', '=', user_work_manager)])
			if employee_work_manager_id:
				agent_work_manager = employee_work_manager_id + self.env['hr.employee'].sudo().search([
					('parent_id', '=', employee_work_manager_id.id)])
				return agent_work_manager
		elif user_type == 'agent':
			user_agent = self.env.user.id
			employee_agent = self.env['hr.employee'].search([('user_id', '=', user_agent)])
			return employee_agent
		else:
			return False

	@api.onchange('report_type')
	def _get_agents(self):
		user_type = self._get_user_type()
		users_id = self.env.user.id
		employees_id = self.env['hr.employee'].sudo().search([('user_id', '=', users_id)])
		agent_ids = self._get_user_agents()
		self.team = employees_id.team_id.id
		return {'domain':{'agent':[('id', 'in', agent_ids.ids)],'team':[('id', '=',employees_id.team_id.id)]}}

	@api.multi
	def print_report(self):
		if self.report_type == 'deal_report':
			data = {
				'start_date': self.date_start,
				'end_date': self.date_end,
				'deal_type': self.deal_type,
				'agent': self.agent.id,
				'team': self.team.id,
				'property_type': self.property_type.id,
			}
			if self.agent:
				data['agent_name'] = self.agent.name
			if self.team:
				data['team_name'] = self.team.name
			if self.property_type:
				data['property_name'] = self.property_type.name
			return self.env.ref('asteco_crm.report_deal_pdf').report_action(self,data)
		elif self.report_type == 'commission_received_report':
			data = {
				'date_from' : self.date_start,
				'date_to' : self.date_end,
			}
			return self.env.ref('asteco_crm.report_deal_commission_pdf').report_action(self,data)

		elif self.report_type == 'listing_report':
			data = {
			'list_type': self.list_type,
			}
			return self.env.ref('asteco_crm.report_list_preview').report_action(self,data)

		elif self.report_type == 'agent_performance_report':
			data = {

			'date_start' : self.date_start,
			'date_end' : self.date_end,
			'company' : self.company.id,
			}
			if self.company:
				data['company_name'] = self.company.name
			return self.env.ref('asteco_crm.agent_performance_preview').report_action(self, data)
		elif self.report_type == 'deal_report':
			data = {
				'start_date': self.date_start,
				'end_date': self.date_end,
			}
			return self.env.ref('asteco_crm.report_deal_pdf').report_action(self, data)
		elif self.report_type == 'leads_lost_report':
			data = {
				'start_date': self.date_start,
				'end_date': self.date_end,
			}
			return self.env.ref('asteco_crm.report_leads_lost_pdf').report_action(self,data)
		elif self.report_type == 'deals_lost_report':
			data = {
				'start_date': self.date_start,
				'end_date': self.date_end,
			}
			return self.env.ref('asteco_crm.report_deals_lost_pdf').report_action(self,data)
		elif self.report_type == 'asteco_and_non_asteco_report':
			data={
				'start_date':self.date_start,
				'end_date':self.date_end,
				'stock_type':self.stock_type,
				'listing_type':self.listing_type,
				'company':self.company.id,
				'agent':self.agent.id,
			}
			if self.agent:
				data['agent_name'] = self.agent.name
			if self.company:
				data['company_name'] = self.company.name
			if data['stock_type'] == 'all':
				data['stock'] = 'All'
			elif data['stock_type'] == 'asteco_stock':
				data['stock'] = 'Asteco'
			elif data['stock_type'] == 'non_asteco':
				data['stock'] = 'Non-Asteco'
			return self.env.ref('asteco_crm.report_deal_number_pdf').report_action(self,data)
		elif self.report_type == 'leads_and_deals_report':
			data = {
			'date_start' : self.date_start,
			'date_end' : self.date_end,
			'company' : self.company.id,
			'agent': self.agent.id,
			'team': self.team.id,
			}
			if self.company:
				data['company_name'] = self.company.name
			return self.env.ref('asteco_crm.leads_and_deals_preview').report_action(self,data)
		return False

	@api.multi
	def cancel(self):
		return

