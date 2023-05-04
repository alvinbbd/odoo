from odoo import fields, models, api

class ResEmployee(models.Model):
    _inherit = 'hr.employee'

    # def _compute_current_score(self):
    #     for agent in self:
    #         lead_ids = self.env['atk.lead.lead'].search([('agent_id', '=', agent.id)])
    #         points = 0
    #         for lead in lead_ids:
    #             points = points + lead.points
    #         agent.current_score = points
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    name_employee = fields.Char('Name', related="user_id.name")
    company_id = fields.Many2one('res.company', string='Company', related="user_id.company_id")
    emp_user_type = fields.Many2one('res.user.type', string="User Type",related="user_id.user_type")
    emp_user_status = fields.Selection([('active','Active'),('blocked','Blocked'),('deactivated','Deactivated')],string="User Status", related="user_id.user_status")
    emp_agent_status = fields.Selection([('away','Away'),('available','Available')], string="Agent Status", related="user_id.agent_status")
    manage_rota = fields.Selection([('yes','Yes'),('no','No')], default="no")
    team_id = fields.Many2one("asteco.sale.team", string="Team", related="user_id.team_id")
    parent_id = fields.Many2one(related="user_id.parent_is")
    job_id = fields.Many2one(related="user_id.job_title", store=True)
    department_id = fields.Many2one(related="user_id.department_id")
    lang = fields.Selection([('Arabic','Arabic'),('Russian','Russian'),('Chinese','Chinese'),('French','French'),('German','German'),('Spanish','Spanish')], string="Additional Language", related="user_id.lang")
    # current_score = fields.Integer('Current Score', compute=_compute_current_score)
    # agent_performance_id = fields.Many2one('agent.performance')

    agent_performance_summary = fields.Many2one('agent.performance')
    current_points = fields.Float(compute="_compute_agent_points")
    confidence_score = fields.Integer(string="Confidence Score")
    work_phone = fields.Char(related="user_id.mobile")

    def _compute_agent_points(self):
        for record in self:
            self.env.cr.execute("""SELECT sum(points)
                                   FROM agent_confidence_score where agent_id = %s
                             """,(record.id,))
            record.current_points = self.env.cr.fetchone()[0]

    agent_performance_summary = fields.Many2one('agent.performance')
    current_points = fields.Float(compute="_compute_agent_points")
    confidence_score = fields.Integer(string="Confidence Score")

    def _compute_agent_points(self):
        for record in self:
            self.env.cr.execute("""SELECT sum(points)
                                   FROM agent_confidence_score where agent_id = %s
                             """,(record.id,))
            record.current_points = self.env.cr.fetchone()[0]


    # @api.multi
    # @api.onchange('parent_id')
    # def set_asteco_team(self):
    #     team_id = False
    #     if self.parent_id:
    #         if self.parent_id.team_id:
    #             team_id = self.parent_id.team_id.id
    #         if not team_id and self.parent_id.user_id and self.parent_id.user_id.team_id:
    #             team_id = self.parent_id.user_id.team_id.id
    #         if not team_id and self.parent_id.parent_id and self.parent_id.parent_id.team_id:
    #             team_id = self.parent_id.parent_id.team_id.id
    #         if not team_id and self.parent_id.parent_id and self.parent_id.parent_id.user_id and self.parent_id.parent_id.user_id.team_id:
    #             team_id = self.parent_id.parent_id.user_id.team_id.id
    #     self.team_id = team_id

    @api.model
    def create(self, vals):
        res = super(ResEmployee, self).create(vals)
        res.confidence_score = 100
        self.env['action.field.value'].create({
                'name':res.name,
                'value':res.id,
                'field_id':self.env['ir.model.fields'].search([('model_id','=',self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1).id),('name','=','agent_id')]).id
            })
        return res

# class ResUserType(models.Model):
#     _name = 'res.user.type'

#     name = fields.Char(string="User Type")

class HrJob(models.Model):
    _inherit = "hr.job"

    @api.model
    def create(self, vals):
        res = super(HrJob, self).create(vals)
        res.company_id = False
        return res

class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.model
    def create(self, vals):
        res = super(HrDepartment, self).create(vals)
        res.company_id = False
        return res


class AstecoSaleTeam(models.Model):
    _name = "asteco.sale.team"

    name = fields.Char("Team Name")
    member_ids = fields.One2many("hr.employee","team_id")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self:self.env.user.company_id.id)