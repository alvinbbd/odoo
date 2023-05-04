from odoo import fields, models, api
from odoo.exceptions import Warning


class ResUsers(models.Model):
	_inherit = 'res.users'
	
	def _get_user_domain(self):
		type_ids = self.env['res.user.type'].search([('name','in',['Agent Broker','Agent Call Center','Super User','Super Admin (IT)'])]).ids
		return [('emp_user_type','not in',type_ids)]

	def _get_team_domain(self):
		team_ids = self.env['asteco.sale.team'].search([('company_id','in',self.env.user.company_ids.ids)])
		return [('id','in',team_ids.ids)]

	def _get_company_team(self):
		team_ids = self.env['asteco.sale.team'].search([('company_id','=',self.env.user.company_id.id)]).ids
		return [('id','in',team_ids)]

	@api.model
	def _get_company(self):
		return self.env.user.company_id

	name = fields.Char(required=True, translate=True,track_visibility="onchange")
	login = fields.Char(required=True, help="Used to log into the system",track_visibility="onchange")
	login_date = fields.Datetime(related='log_ids.create_date', string='Latest connection',track_visibility="onchange")
	company_id = fields.Many2one('res.company', string='Company', required=True, default=_get_company,
								 help='The company this user is currently working for.',
								 context={'user_preference': True},track_visibility="onchange")
	user_status = fields.Selection([('active','Active'),('blocked','Blocked'),('deactivated','Deactivated')],string="User Status",default='active',track_visibility="onchange")
	agent_status = fields.Selection([('away','Away'),('available','Available')],track_visibility="onchange", string="Agent Status", default="available")
	parent_is = fields.Many2one("hr.employee", string="Parent is", domain=_get_user_domain,track_visibility="onchange")
	job_title = fields.Many2one("hr.job", string="Job Title",track_visibility="onchange")
	team_id = fields.Many2one("asteco.sale.team", "Team", domain = _get_company_team,track_visibility="onchange")
	manage_rota = fields.Selection([('yes','Yes'),('no','No')], default="no")
	mobile = fields.Char(string="Phone(Mobile)",track_visibility="onchange")
	phone_office = fields.Char(string="Phone(Office)",track_visibility="onchange")
	rera_brn = fields.Char(string="RERA BRN",track_visibility="onchange")
	address = fields.Text(track_visibility="onchange")
	is_agent= fields.Boolean(deault=False)
	is_rota= fields.Boolean(deault=False)
	is_super_admin_it_main = fields.Boolean(default=False)

	department_id = fields.Many2one('hr.department', string="Department",track_visibility="onchange")

	is_rera = fields.Boolean(default=False)
	approval_required = fields.Selection([('yes','Yes'),('no','No')], default='no',track_visibility="onchange", string="Approval Required to Publish")
	email_otp = fields.Boolean("Email OTP",track_visibility="onchange")
	sms_otp = fields.Boolean("SMS OTP",track_visibility="onchange")

	imap = fields.Char("IMAP",track_visibility="onchange")
	inbound_smtp_settings = fields.Char(track_visibility="onchange")
	outbound_smtp_settings = fields.Char(track_visibility="onchange")
	email = fields.Char(track_visibility="onchange")
	email_password = fields.Char(default='',track_visibility="onchange", copy=False, help="Keep empty if you don't want the user to be able to connect on the system.")

	user_type = fields.Many2one('res.user.type', string="User Type",track_visibility="onchange")
	lang = fields.Selection([('Arabic','Arabic'),('Russian','Russian'),('Chinese','Chinese'),('French','French'),('German','German'),('Spanish','Spanish')],track_visibility="onchange", string="Additional Language")
	# team_id = fields.Many2one("asteco.sale.team", "Team")

	bank_payment_details=fields.Html(string="Bank Payment Details")

	active= fields.Boolean(groups='asteco_crm.group_super_admin')
	signature = fields.Html(track_visibility="onchange")

	@api.model
	def create(self, vals):
		if 'user_type' in vals and vals['user_type']:
			type_id = self.env['res.user.type'].browse(vals['user_type'])
			for group in type_id.group_ids:
				vals['in_group_' + str(group.id)] = True
		res = super(ResUsers, self).create(vals)
		res.imap = res.company_id.imap_server
		if res.is_super_admin_it_main == True:
			group_id = self.env.ref('asteco_crm.group_super_admin_main')
			res.groups_id += group_id
		return res

	@api.multi
	def write(self, vals):
		if 'user_type' in vals:
			type_ids = self.env['res.user.type'].search([])
			for type in type_ids:
				for group in type.group_ids:
					vals['in_group_' + str(group.id)] = False
			if vals['user_type']:
				type_id = self.env['res.user.type'].browse(vals['user_type'])
				for group in type_id.group_ids:
					vals['in_group_' + str(group.id)] = True
		if 'agent_status' in vals:
			rota_ids = self.env['lead.rotation'].search([('agent_id','in',self.employee_ids.ids)])
			if rota_ids:
				if vals['agent_status'] == 'available':
					for rota in rota_ids:
						rota.agent_status = True
				else:
					for rota in rota_ids:
						rota.agent_status = False
		if 'is_super_admin_it_main' in vals:
			group_id = self.env.ref('asteco_crm.group_super_admin_main')
			if vals['is_super_admin_it_main'] == True:
				self.groups_id += group_id
			else:
				for group in self.groups_id:
					if group.id == group_id.id:
						self.groups_id -= group_id
		return super(ResUsers, self).write(vals)


	@api.onchange('user_type')
	def onchange_user_type(self):
		if self.user_type.name in ['Work Manager','Co-ordinator','Sales Manager','Agent Broker']:
			self.is_rera = True
		else:
			self.is_rera = False

		if self.user_type.name in ['Work Manager','Sales Manager','Agent Broker','Agent Call Center']:
			self.is_agent=True
		else:
			self.is_agent=False

		if self.user_type.name in ['Agent Broker']:
			self.is_rota=True
		else:
			self.is_rota=False
		


	@api.multi
	def raise_warning(self, msg):
		if msg:
			raise Warning(msg)
		return

	@api.multi
	def check_is_a_child(self, assign_id):
		# assign_emp_id = self.env['hr.employee'].browse(assign_id)
		# if self.has_group('asteco_crm.group_sales_manager'):
		# 	if self.team_id:
		# 		if assign_id not in self.team_id.member_ids.ids:
		# 			raise Warning("You can't assign this agent!!! Please contact Co-Ordinator.")
		# elif self.has_group('asteco_crm.group_work_manager'):
		# 	if assign_emp_id.parent_id.id not in self.employee_ids.ids:
		# 		raise Warning("You can't assign this agent!!! Please contact Co-Ordinator.")
		# elif self.has_group('asteco_crm.group_agent_broker'):
		# 	raise Warning("You can't assign this agent!!! Please contact Co-Ordinator.")
		# else:
		# 	pass
		pass
		return True

class ResUserType(models.Model):
	_name = 'res.user.type'

	name = fields.Char(string="User Type")
	group_ids = fields.Many2many("res.groups", string="Groups")