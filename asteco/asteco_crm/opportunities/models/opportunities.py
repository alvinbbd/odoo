from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Opportunities(models.Model):
    _name = 'lead.opportunity'
    _description = 'Opportunity'

    @api.multi
    def _get_default_state(self):
        state_id = self.env['opportunity.stage'].search([('name', '=', 'Qualified')], limit=1)
        return state_id.id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['opportunity.stage'].search([])
        return stage_ids

    def _get_substatus_domain(self):
        status_ids = self.env['lead.sub.status'].search(
            [('name', 'in', ['Qualified', 'Viewings', 'Negotiation', 'Coverted to Deal'])]).ids
        return [('id', 'in', status_ids)]

    
    deal_confidence_level = fields.Char(string="Deal Confidence Level (%)", related="deal_id.deal_confidence_level")
    value_from_lead = fields.Char()

    title = fields.Text(string="Title")
    comments = fields.Text(string="Comments")
    note = fields.Text(string="Note")

    close_date = fields.Datetime(string="Expected Close Date")
    
    commission_value = fields.Integer(string="Expected Commission Value")
    viewing_count = fields.Integer(related="lead_id.viewing_count")

    lead_id = fields.Many2one('atk.lead.lead', string="Lead Ref")
    listing_id = fields.Many2one('listing.listing', string="Listing Ref")
    deal_id = fields.Many2one('deal.deal', string="Deal Ref")
    
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    stage_id = fields.Many2one('opportunity.stage', default=_get_default_state, group_expand='_read_group_stage_ids')
    customer_id = fields.Many2one('res.partner', string="Contact", realated="lead_id.contact_id")
    listing_contact_id = fields.Many2one('res.partner', string="Contact", related="listing_id.customer_id")
    loss_reason = fields.Many2one('loss.reason', string="Reason for Loss", related="lead_id.loss_reason")
    lead_subtatus_id = fields.Many2one('lead.sub.status', string="Lead Sub-status", related="lead_id.sub_status_id", domain=_get_substatus_domain)
    assign_id = fields.Many2one('hr.employee', related="lead_id.agent_id", string='Assigned To', readonly="1")
    team_id = fields.Many2one("asteco.sale.team", related="assign_id.team_id", string="Team", readonly="1")
   
    state = fields.Selection([('Qualified', 'Qualified'), ('Viewings', 'Viewing'), ('Negotiation', 'Negotiation'), ('Converted to Deal', 'Converted to Deal'), ('Lost', 'Lost')], default="Qualified")
    is_lead_or_listing = fields.Selection([('Lead', 'Lead'), ('Listing', 'Listing'), ('Deal', 'Deal')], default="Lead")
    qualified_status = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')], default="In Progress")
    viewings_status = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')])
    negotiation_status = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')])
    deal_status = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')])
    
    @api.constrains('commission_value')
    def _check_commission_value(self):
        for record in self:
            if record.commission_value <= 0.0 and record.state not in ['Qualified']:
                raise ValidationError("Please enter a valid commission amount!!!")

    @api.multi
    def name_get(self):
        result = []
        for opportunity in self:
            name = str(opportunity.lead_id.name)
            result.append((opportunity.id, name))
        return result

    @api.model
    def create(self, vals):
        res = super(Opportunities, self).create(vals)
        if res.qualified_status == 'Won':
            res.state = 'Viewings'
            res.viewings_status = 'In Progress'
            state_id = self.env['opportunity.stage'].search([('name', '=', 'Viewings')])
            if state_id:
                res.stage_id = state_id.id
        elif res.qualified_status == 'Lost':
            lost_status_id = self.env['lead.sub.status'].search([('name', '=', 'Lead Lost')], limit=1)
            if lost_status_id:
                res.lead_subtatus_id = lost_status_id.id
        return res

    @api.multi
    def write(self, vals):
        res = super(Opportunities, self).write(vals)
        if 'qualified_status' in vals:
            if vals['qualified_status'] == 'Won':
                self.state = 'Viewings'
                self.viewings_status = 'In Progress'
                state_id = self.env['opportunity.stage'].search([('name', '=', 'Viewings')])
                lead_state_id = self.env['lead.sub.status'].search([('name', '=', 'Viewings')])
                if state_id:
                    self.stage_id = state_id.id
                if lead_state_id:
                    self.lead_subtatus_id = lead_state_id.id
            elif vals['qualified_status'] == 'Lost':
                self.update_lead_status()
        elif 'viewings_status' in vals:
            if vals['viewings_status'] == 'Won':
                self.state = 'Negotiation'
                self.negotiation_status = 'In Progress'
                state_id = self.env['opportunity.stage'].search([('name', '=', 'Negotiation')])
                lead_state_id = self.env['lead.sub.status'].search([('name', '=', 'Negotiation')])
                if state_id:
                    self.stage_id = state_id.id
                self.lead_subtatus_id = self.lead_id.sub_status_id.id
                if lead_state_id:
                    self.lead_subtatus_id = lead_state_id.id
                for record in self.lead_id.lead_offered_unit_ids:
                    if self.listing_id:
                        if self.listing_id.id == record.listing_id.id:
                            record.status = 'Negotiation'
            elif vals['viewings_status'] == 'Lost':
                self.update_lead_status()
        elif 'negotiation_status' in vals:
            if vals['negotiation_status'] == 'Won':
                self.state = 'Converted to Deal'
                self.deal_status = 'In Progress'
                state_id = self.env['opportunity.stage'].search([('name', '=', 'Converted to Deal')])
                lead_state_id = self.env['lead.sub.status'].search([('name', '=', 'Converted to Deal')])
                if state_id:
                    self.stage_id = state_id.id
                self.lead_subtatus_id = self.lead_id.sub_status_id.id
                if lead_state_id:
                    self.lead_subtatus_id = lead_state_id.id
                if not self.deal_id:
                    self.deal_id = self.env['deal.deal'].create({
                        'lead_id': self.lead_id.id,
                        'state': 'in_Progress',
                        'listing_id': self.listing_id.id,
                        'commission_value': self.deal_id.gross_commission,
                        'sub_status_id': 'Documentation',
                    }).id
                for record in self.lead_id.lead_offered_unit_ids:
                    if self.listing_id:
                        if self.listing_id.id == record.listing_id.id:
                            record.status = 'Converted to Deal'

            elif vals['negotiation_status'] == 'Lost':
                self.update_lead_status()
        elif 'deal_status' in vals:
            if vals['deal_status'] == 'Won':
                for record in self.lead_id.lead_offered_unit_ids:
                    if self.listing_id:
                        if self.listing_id.id == record.listing_id.id:
                            record.status = 'Success'
            elif vals['deal_status'] == 'Lost':
                self.update_lead_status()

        if 'stage_id' in vals:
            self.state = self.stage_id.name
        # if 'state' in vals:
        # 	if self.state == 'Lost':
        # 		if self.listing_id:
        # 			self.listing_id.opportunity_state = 'Failed'
        return res

    @api.multi
    def update_lead_status(self):
        lost_status_id = self.env['lead.sub.status'].search([('name', '=', 'Lead Lost')], limit=1)
        if lost_status_id:
            self.lead_subtatus_id = lost_status_id.id
        self.state = 'Lost'
        self.customer_id = False
        for record in self.lead_id.lead_offered_unit_ids:
            if self.listing_id:
                if self.listing_id.id == record.listing_id.id:
                    record.status = 'Failed'
        # self.lead_id = False
        return

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        self.state = self.stage_id.name

    @api.onchange('lead_id')
    def onchange_lead(self):
        if self.lead_id:
            # self.listing_id = False
            # self.customer_id = self.lead_id.contact_id.id
            self.title = self.lead_id.title
        # self.lead_subtatus_id = self.lead_id.sub_status_id.id
    # else:
    # self.customer_id = False
    # self.lead_subtatus_id = False

# @api.onchange('listing_id')
# def onchange_listing(self):
# 	if self.listing_id:
# 		self.name = False
# 		self.customer_id = self.listing_id.customer_id.id
# 		self.title = self.listing_id.name
# 	else:
# 		self.title = False
# 		self.customer_id = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Opportunities, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        current_user = self.env.user
        for record in self.sudo().search([]):
            if record.lead_id:
                if not current_user.has_group('asteco_crm.group_coordinator'):
                    current_emp_id = self.env['hr.employee'].search([('user_id', '=', current_user.id)])
                    if record.lead_id.agent_id.id != current_emp_id.id and record.lead_id.agent_id.parent_id.id != current_emp_id.id and record.lead_id.agent_id.parent_id.parent_id.id != current_emp_id.id:
                        record.sudo().lead_id.sudo().accessible_user_ids = [[4, current_user.id]]
        return res

    @api.multi
    def roll_back(self):
        stage_roll_back = {'stage_id':self.stage_id.id,'deal_id':self.deal_id,'lead_id': self.lead_id,
                           'listing_id':self.listing_id,'listing_contact_id':self.listing_contact_id}
        self.roll_back_impl(stage_roll_back)

    @api.multi
    def roll_back_impl(self,vals):
        if vals['stage_id'] == self.env.ref('asteco_crm.converted_to_deal').id:
            self.deal_id.deal_status = "Archived"
            self.deal_id = False
            self.lead_id.nego_won_or_lost = "In Progress"
            self.lead_id.offered_unit_id.status = 'Negotiation'
            self.stage_id = self.env.ref('asteco_crm.negotiation').id
        elif vals['stage_id'] == self.env.ref('asteco_crm.negotiation').id:
            self.listing_id = vals['listing_contact_id'] = False
            self.stage_id = self.env.ref('asteco_crm.viewings').id
            self.lead_id.nego_won_or_lost = "In Progress"
            self.lead_id.view_won_or_lost = "In Progress"
            self.lead_id.offered_unit_id.status = 'Viewings'
            self.lead_id.offered_unit_id = False
            self.lead_id.opportuninty_stage = 'Viewing'
        return

    @api.multi
    def roll_back(self):
        stage_roll_back = {'stage_id':self.stage_id.id, 'listing_contact_id':self.listing_contact_id}
        self.roll_back_impl(stage_roll_back)
        return True



class Stage(models.Model):
    _name = "opportunity.stage"
    _description = "Opportunity Stage"
    _order = "id"

    name = fields.Char('Stage Name', required=True, translate=True)


class LossReason(models.Model):
    _name = "loss.reason"
    _description = "Loss Reason"
    _order = "id"

    name = fields.Char('Loss Reason', required=True, translate=True)
