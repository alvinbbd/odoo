from odoo import models, fields, api
from datetime import  datetime, timedelta


class ATKLeadRotation(models.Model):
    _name = "lead.rotation"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Asteco Lead Rotation"
    _order = "id asc"

    def _set_agent_domain(self):
        user_types = self.env.ref('asteco_crm.agent_broker')
        user_types += self.env.ref('asteco_crm.work_manager')
        user_types += self.env.ref('asteco_crm.sales_manager')
        user_types += self.env.ref('asteco_crm.coordinator')
        emp_ids = self.env['hr.employee'].search([('emp_user_type','in',user_types.ids)]).ids
        return [('id','in',emp_ids)]

    def _default_country(self):
        return self.env['res.country'].search([('name','=','United Arab Emirates')])

    def _get_emirates(self):
        ids = self.env['res.country.state'].search([('country_id','=',self.env['res.country'].search([('name','=','United Arab Emirates')],limit=1).id)]).ids
        return [('id','in',ids)]

    name = fields.Char()
    agent_id = fields.Many2one("hr.employee", "Agent",required=True,domain=_set_agent_domain,track_visibility="onchange")
    team_id = fields.Many2one("asteco.sale.team", related="agent_id.team_id", string="Team", readonly="1",track_visibility="onchange")
    manager_id = fields.Many2one('hr.employee', related="agent_id.parent_id", readonly="1",track_visibility="onchange")
    lead_type = fields.Selection(
        [('Any','Any'), ('land_lord', 'Land Lord'), ('tenant', 'Tenant'), ('buyer', 'Buyer'), ('seller', 'Seller'),
         ('investor', 'Investor'), ('agent', 'Agent')],track_visibility="onchange")
    commercial_residential = fields.Selection([('Any','Any'), ("commercial","Commercial"), ('residential', 'Residential')], string='Commercial /Residential')
    emirate_id = fields.Many2one("res.country.state", string='Emirate/City', domain=_get_emirates,track_visibility="onchange")
    emirate_any_null = fields.Selection([('any','Any'),('null','Null')], "Emirate Any/ Null")
    country_id = fields.Many2one("res.country", string="Country", default=_default_country)
    location_id = fields.Many2one('res.location', string="Location /Project",track_visibility="onchange")
    location_any_null = fields.Selection([('any', 'Any'), ('null', 'Null')], "Location Any/ Null")
    sub_location_id = fields.Many2one('res.sub.location', string="Sub-Location /Building",track_visibility="onchange")
    sub_location_any_null = fields.Selection([('any', 'Any'), ('null', 'Null')], "Sub-Location Any/ Null")
    # additional_languages = fields.Many2one('res.lang', string="Additional Languages")
    additional_languages = fields.Selection([('Arabic','Arabic'),('Russian','Russian'),('Chinese','Chinese'),('French','French'),('German','German'),('Spanish','Spanish')], string="Additional Language", related="agent_id.lang")
    agent_status = fields.Boolean('Available', default=True)
    last_assingned_date = fields.Datetime("Last Assigned Flag", store=True)
    leads_count = fields.Integer()

    rule_id = fields.Many2one('lead.rotation')
    lead_rotation_ids = fields.One2many('lead.rotation','rule_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('lead.rotation'))

    @api.onchange('agent_id')
    def onchange_agent(self):
        self.lead_rotation_ids = False
        rules = self.search([('agent_id','=',self.agent_id.id)]).ids
        self.lead_rotation_ids = rules

    @api.onchange('emirate_id')
    def onchange_emirate(self):
        if self.emirate_id != False:
            self.emirate_any_null = False
        ids = self.env['res.location'].search([('emirate_id','=',self.emirate_id.id)]).ids
        return {'domain':{'location_id':[('id','in',ids)]}}

    @api.onchange('emirate_any_null')
    def onchange_emirate_any_null(self):
        if self.emirate_any_null in ['any','null']:
            self.emirate_id = False


    @api.onchange('location_id')
    def onchange_location(self):
        if self.location_id != False:
            self.location_any_null = False
        ids = self.env['res.sub.location'].search([('location_id','=',self.location_id.id)]).ids
        return {'domain':{'sub_location_id':[('id','in',ids)]}}

    @api.onchange('location_any_null')
    def onchange_location_any_null(self):
        if self.location_any_null in ['any','null']:
            self.location_id = False


    @api.onchange('sub_location_id')
    def onchange_sublocation(self):
        if self.sub_location_id != False:
            self.sub_location_any_null = False

    @api.onchange('sub_location_any_null')
    def onchange_sublocation_any_null(self):
        if self.sub_location_any_null in ['any','null']:
            self.sub_location_id = False

    @api.constrains('lead_type','commercial_residential','emirate_id','location_id','sub_location_id','agent_id')
    def _check_duplicate_rule(self):
        for record in self:
            rule_ids = False
            rule_ids = self.env['lead.rotation'].search([('id','!=',record.id), ('agent_id','=',record.agent_id.id), ('lead_type','=',record.lead_type),('commercial_residential','=',record.commercial_residential),('emirate_id','=',record.emirate_id.id),('location_id','=',record.location_id.id),('sub_location_id','=',record.sub_location_id.id)])
            if rule_ids:
                raise Warning("Duplicate rule exist!!!")
   
    @api.model
    def create(self, vals):
        hr_id = self.env['hr.employee'].browse(vals['agent_id'])
        if hr_id.user_id.agent_status == 'available':
            vals['agent_status'] = True
        else:
            vals['agent_status'] = False
        res = super(ATKLeadRotation, self).create(vals)
        code = self.env.user.company_id.code if self.env.user.company_id.code else ""
        res.name = code + self.env['ir.sequence'].next_by_code('atk.lead.rotation')
        if res.agent_id.user_id.login_date:
            res.last_assingned_date = res.agent_id.user_id.login_date
        return res


class LeadAssigingHistory(models.Model):
    _name = "lead.assign.history"
    _order = "id desc"

    agent_id = fields.Many2one("hr.employee", string="Agent")
    lead_id = fields.Many2one("atk.lead.lead", "Lead")
    assign_time = fields.Datetime("Assign Time")
    lead_rot_id = fields.Many2one("lead.rotation",string="Lead Rotation") #field created to store the value from lead.py
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    auto_assign = fields.Selection([('Y','Y'), ('N', 'N')],string="Auto Assign (Y/N)")

    @api.model
    def create(self, vals):
        res = super(LeadAssigingHistory, self).create(vals)
        if res.lead_rot_id:
            res.lead_rot_id.last_assingned_date = res.assign_time
            res.lead_rot_id.leads_count += 1
            # res.lead_rot_id.last_assingned_date = datetime.now() # setting the time (now) into this field
        return res


class UsersLog(models.Model):
    _inherit = 'res.users.log'

    @api.model
    def create(self, vals):
        res = super(UsersLog, self).create(vals)
        emp_id = self.env['hr.employee'].search([('user_id','=',res.create_uid.id)])
        if emp_id:
            lead_rota_ids = self.env['lead.rotation'].search([('agent_id','=',emp_id.id)])
            for lead_rota in lead_rota_ids:
                if not lead_rota.last_assingned_date:
                    lead_rota.last_assingned_date = res.write_date
        return res

class HREmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, vals):
        res = super(HREmployee, self).create(vals)
        if res.emp_user_type.id in [self.env.ref('asteco_crm.coordinator').id, self.env.ref('asteco_crm.sales_manager').id]:
            self.env['lead.rotation'].create({
                'agent_id' : res.id,
                'lead_type': 'Any',
                'emirate_any_null' : 'any',
                'location_any_null' : 'any',
                'sub_location_any_null' : 'any',
                'commercial_residential': 'Any',
            })
        return res

