from odoo import fields, models, api
import datetime


class AutomatedAction(models.Model):
	_name = 'auto.action'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_description = "Automated Action"

	@api.multi
	def _get_fields_domain(self):
		model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id)]).ids
		return [('id','in',field_ids)]

	@api.multi
	def _get_date_fields_domain(self):
		model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id), ('ttype','in',['datetime','date'])]).ids
		return [('id','in',field_ids)]
	
	ref = fields.Char(string="Reference #",track_visibility="onchange")
	name = fields.Char(string="Rule Name", required=True,track_visibility="onchange")
	module = fields.Selection([('Contacts','Contacts'),('Deals','Deals'),('Leads','Leads'),('Listings','Listings')],track_visibility="onchange", required=True, default='Leads')
	description = fields.Text(string="Description",track_visibility="onchange")
	status = fields.Selection([('Active','Active'),('Inactive','Inactive')], string="Status", default="Active",track_visibility="onchange")

	trigger = fields.Selection([('Check Value','Check Value'), ('is Created','is Created'),('on Change of Field Values','on Change of Field Values'),('is Created or Updated','is Created or Updated'),('is not Updated','is not Updated')], string="Trigger", default='Check Value',track_visibility="onchange")
		
	trigger_timing_interval = fields.Integer()
	trigger_type = fields.Selection([('Day(s)','Day(s)'),('Hour(s)','Hour(s)'),('Month(s)','Month(s)')], default="Day(s)")
	after_date = fields.Many2one('ir.model.fields', domain=_get_fields_domain)
	
	field_next = fields.Many2one('ir.model.fields', string="Field", domain=_get_fields_domain)
	operator_next = fields.Selection([('Any Changes','Any Changes'),('Specific Change','Specific Change')], string="On")
	field_value_next = fields.Char(string="Value Changes To")

	action_timing = fields.Selection([('Immediatly','Immediately'),('Custom','Custom')],track_visibility="onchange", string="Action Timing", default="Immediatly")
	interval = fields.Integer(track_visibility="onchange")
	interval_type = fields.Selection([('Day(s)','Day(s)'),('Hour(s)','Hour(s)'),('Minute(s)','Minute(s)'),('Month(s)','Month(s)')], default="Hour(s)",track_visibility="onchange")
	interval_timing = fields.Selection([('After','After'),('Before','Before')], default="After")
	conditional_field = fields.Many2one('ir.model.fields', domain=_get_date_fields_domain)

	action = fields.Selection([('Send an Email','Send an Email'), ('Update Record','Update Record'), ('Send Email and Update Record','Send Email and Update Record')],track_visibility="onchange", string="Action", default="Send an Email")
	recipients = fields.Many2many('email.recipients', string="Recipients",track_visibility="onchange")
	
	# task_title = fields.Char(string="Task Title")
	# priority = fields.Selection([('Low','Low'),('Medium','Medium'),('High','High')], string="Priority")
	# due_days = fields.Integer(string="No. of Days Due")

	update_field_lines = fields.One2many('action.update.line','action_id',string="")
	criteria_field_lines = fields.One2many('action.criteria.line','action_id',string="")
	company_id = fields.Many2one('res.company', string='Company')

	@api.onchange('module')
	def fields_custom_domain(self):
		for record in self:
			model_id = False
			date_field_ids = []
			field_ids = []
			if record.module == 'Leads':
				model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
				field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id)]).ids
				date_field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('ttype','in',['date','datetime'])]).ids
			return {'domain':{'field_nd':[('id','in',field_ids)], 'field':[('id','in',field_ids)], 'field_next':[('id','in',field_ids)], 'conditional_field':[('id','in',date_field_ids)], 'after_date':[('id','in',date_field_ids)], 'update_field':[('id','in',field_ids)], 'update_field_next':[('id','in',field_ids)]}}

	@api.multi
	def name_get(self):
		result = []
		for action in self:
			name = str(action.ref)
			result.append((action.id, name))
		return result

	@api.model
	def create(self, vals):
		res = super(AutomatedAction, self).create(vals)
		code = self.env.user.company_id.code if self.env.user.company_id.code else ""
		res.ref = code + self.env['ir.sequence'].next_by_code('auto.action')
		return res

class AutoActionScheduler(models.Model):
	_name = 'auto.action.scheduler'

	module = fields.Many2one('ir.model')
	object_id = fields.Integer()
	rule_id = fields.Many2one('auto.action')
	schedule_time = fields.Datetime()
	is_active = fields.Boolean(default=True)
	seq = fields.Char()
	company_id = fields.Many2one('res.company', string='Company')

	@api.model
	def _automated_action_delete(self):
		for task in self.search([('is_active','=',False)]):
			task.unlink()

	@api.model
	def _automated_action(self):
		for task in self.search([('schedule_time','<=',datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")),('is_active','=',True)]):
			task.is_active = False
			record_id = self.env[task.module.model].browse(task.object_id)			
			rule_id = task.rule_id
			agent_id = record_id.agent_id
			flag = 0

			for line in rule_id.criteria_field_lines:
				if line.field.name not in ['state','pool_status','future_action_date','create_date']:
					continue
				field_value = (record_id.mapped(line.field.name))[0]
				if line.field.name in ['state','pool_status'] and line.operator == 'Contains':
					if field_value != line.field_value.value:
						flag = 1
				elif line.field.name in ['future_action_date'] and line.operator == 'Greater than' and line.field_value.name == 'Current Date':
					if field_value and datetime.datetime.strptime(field_value,'%Y-%m-%d %H:%M:%S') > datetime.datetime.now():
						flag = 1
				elif line.field.name == 'create_date' and line.date_field != False:
					if line.operator == 'Greater than' and field_value <= line.date_field:
						flag = 1
				else:
					flag = 1
			if flag == 0:
				if rule_id.action == 'Send an Email':
					self.send_mail(rule_id,record_id)
				else:
					if rule_id.action == 'Send Email and Update Record':
						self.send_mail(rule_id,record_id)

					for line in rule_id.update_field_lines:
						if line.name.name == 'state':
							record_id.state = line.field_value.value
						elif line.name.name == 'pool_status':
							record_id.pool_status = line.field_value.value
						elif line.name.name == 'agent_id':
							if line.field_value.value:
								emp_id = self.env['hr.employee'].search([('id','=',int(line.field_value.value))], limit=1)
								if emp_id:
									record_id.agent_id = emp_id.id
								else:
									record_id.agent_id = False
							else:
								record_id.agent_id = False
						elif line.name.name == 'agent_confidence_score' and agent_id:
							if line.field_value:
								self.env['agent.lead.score'].create({
										'agent_id':agent_id.id,
										'lead_id':record_id.id,
										'score':int(line.field_value.value),
									})

	@api.multi
	def send_mail(self, rule_id, lead_id):
		email_to = ""
		for recipient in rule_id.recipients:
			if recipient.name == 'Agent' and lead_id.agent_id:
				email_to += lead_id.agent_id.user_id.email + ","
			elif recipient.name == 'Contact':
				email_to += lead_id.customer_email_id + ","
			elif recipient.name == 'Co-ordinator':
				if lead_id.agent_id.user_id.user_type.id == self.env.ref('asteco_crm.sales_manager').id:
					if lead_id.agent_id.parent_id:
						email_to += lead_id.agent_id.parent_id.user_id.email + ","
				elif lead_id.agent_id.user_id.user_type.id == self.env.ref('asteco_crm.work_manager').id:
					if lead_id.agent_id.parent_id:
						if lead_id.agent_id.parent_id.parent_id:
							email_to += lead_id.agent_id.parent_id.parent_id.user_id.email + ","
				elif lead_id.agent_id.user_id.user_type.id == self.env.ref('asteco_crm.agent_broker').id:
					if lead_id.agent_id.parent_id:
						if lead_id.agent_id.parent_id.parent_id:
							if lead_id.agent_id.parent_id.parent_id.parent_id:
								email_to += lead_id.agent_id.parent_id.parent_id.parent_id.user_id.email + ","
			elif recipient.name == 'Manager':
				if lead_id.agent_id.parent_id:
					email_to += lead_id.agent_id.parent_id.user_id.email + ","
		msg = "This is just a test mail from automated actions. Lead Reference : "+str(lead_id.name)+". Thank you."
		if email_to:
			mail = self.env['mail.mail'].create({
					'subject':'Automated Action',
					'email_from':self.env.user.company_id.email,
					'email_to':email_to,
					'body_html':msg,
				})
			mail.send()
		return


class IrModelFields(models.Model):
	_inherit = "ir.model.fields"

	@api.multi
	def name_get(self):
		result = []
		for field in self:
			name = str(field.field_description)
			result.append((field.id, name))
		return result

class EmailRecipients(models.Model):
	_name = 'email.recipients'

	name = fields.Char()

class ActionUpdateLine(models.Model):
	_name = 'action.update.line'

	@api.multi
	def _get_fields_domain(self):
		model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','in',['agent_confidence_score','agent_id','pool_status','state'])]).ids
		return [('id','in',field_ids)]

	name = fields.Many2one('ir.model.fields', string="Update Field", required=True, domain=_get_fields_domain)
	field_value = fields.Many2one('action.field.value', string="Change To",domain=[('id','in',[])])
	action_id = fields.Many2one('auto.action')

	@api.onchange('name')
	def onchange_name(self):
		ids = self.env['action.field.value'].search([('field_id','=',self.name.id)]).ids
		return {'domain':{'field_value':[('id','in',ids)]}}

class ActionFieldValue(models.Model):
	_name = 'action.field.value'

	name = fields.Char()
	value = fields.Char()
	field_id = fields.Many2one('ir.model.fields')


	@api.model
	def update_field_values(self):
		for record in self.search([]):
			record.unlink()
		model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_id = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','agent_confidence_score')])
		for i in range(-5,6):
			self.create({
					'name':str(i),
					'value':str(i),
					'field_id':field_id.id,
				})
		field_id_2 = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','state')])
		self.create({
				'name':'New',
				'value':'new',
				'field_id':field_id_2.id,
			})
		self.create({
				'name':'Work In Progress',
				'value':'work_Progress',
				'field_id':field_id_2.id,
			})
		self.create({
				'name':'Closed',
				'value':'success',
				'field_id':field_id_2.id,
			})
		field_id_3 = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','pool_status')])
		self.create({
				'name':'Agent Assigned',
				'value':'Agent Assigned',
				'field_id':field_id_3.id,
			})
		self.create({
				'name':'Lead Pool',
				'value':'Lead Pool',
				'field_id':field_id_3.id,
			})
		self.create({
				'name':'Network Pool',
				'value':'Network Pool',
				'field_id':field_id_3.id,
			})
		field_id_4 = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','agent_id')])
		for employee in self.env['hr.employee'].search([]):
			self.create({
				'name':employee.name,
				'value':employee.id,
				'field_id':field_id_4.id,
			})
		field_id_5 = self.env['ir.model.fields'].search([('model_id','=',model_id.id),('name','=','future_action_date')])
		self.create({
				'name':'Current Date',
				'value':'Current Date',
				'field_id':field_id_5.id,
			})

class ActionCriteriaLine(models.Model):
	_name = 'action.criteria.line'

	@api.multi
	def _get_fields_domain(self):
		model_id = self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1)
		field_ids = self.env['ir.model.fields'].search([('model_id','=',model_id.id)]).ids
		return [('id','in',field_ids)] 

	field = fields.Many2one('ir.model.fields', string="Field", required=True, domain=_get_fields_domain)
	operator = fields.Selection([('Contains','Contains'),('Does Not Contain','Does Not Contain'),('Greater than','Greater than')], string="Operator", default='Contains')
	field_value = fields.Many2one('action.field.value', string="Value",domain=[('id','in',[])])
	action_id = fields.Many2one('auto.action')
	date_field = fields.Datetime(string="Select Date")
	is_created_on = fields.Boolean(default=False)

	@api.onchange('field')
	def onchange_name(self):
		if self.field.name == 'create_date':
			self.is_created_on = True
		else:
			self.is_created_on = False
			ids = self.env['action.field.value'].search([('field_id','=',self.field.id)]).ids
			return {'domain':{'field_value':[('id','in',ids)]}}

