from odoo import models,tools,fields, api, _
from datetime import  datetime, timedelta
import base64
from odoo import modules
from odoo.exceptions import Warning, ValidationError, UserError
import re
import requests

class ATKLeadLead(models.Model):
    _name = "atk.lead.lead"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Asteco Lead"

    # @api.multi
    # def _get_qualified(self):
    #     res = self.env.ref('asteco_crm.sub_status10')
    #     return res.id or False

    @api.multi
    def _get_default_lang(self):
        eng_id = self.env.ref("base.lang_en")
        if eng_id:
            return eng_id.id
        else:
            return False

    @api.multi
    def _get_default_img(self):
        with open(modules.get_module_resource('asteco_crm', 'static/img', 'noImage.jpg'),
              'rb') as f:
              return base64.b64encode(f.read())

    # @api.multi
    # def _get_default_status(self):
    #     res = self.env.ref('asteco_crm.sub_status13')
    #     return res.id or False

    @api.multi
    def action_lead_sent(self):
        # __inherit = "mail.template"
        # self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        ctx = {
            'default_model': 'atk.lead.lead',
            'default_res_id': self.id,
            'default_use_template': False,
            'default_template_id': self.env.user.company_id.email_lead_template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            # 'custom_layout': "res.company.email_lead_template",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def _get_contact_domain(self):
        sub_broker_id = self.env['contact.classification'].search([('name', '=', 'Sub-broker')])
        contact_ids = []
        if sub_broker_id:
            contact_ids = self.env['res.partner'].search([('contact_classif_ids', 'in', sub_broker_id.ids)]).ids
        return [('id', 'in', contact_ids)]

    def _default_country(self):
        return self.env.user.company_id.country_id.id
        # return self.env['res.country'].search([('name','=','United Arab Emirates')])

    def _get_value_for_auto_asign(self):
        agent_type = self.env['res.user.type'].search([('name','=','Agent Broker')])
        if agent_type:
            if agent_type == self.env.user.user_type :
                return False
            else:
                return True

    @api.multi
    def _get_current_agent(self):
        if self.env.user.user_type == self.env['res.user.type'].search([('name', '=', 'Agent Broker')]):
            return [('id', '=', self.env.user.employee_ids.ids)]


    contact_id = fields.Many2one("res.partner", "Contact", required=True,
                                 domain=[('is_contact','=',True)], track_visibility="onchange" )

    photo = fields.Binary(string='Photo', related="contact_id.image")
    # agent_id = fields.Many2one("hr.employee", "Assigned To", default=_get_default_agent_id)
    agent_id = fields.Many2one("hr.employee", "Assigned To", domain=_get_current_agent)
    agent_ids = fields.Many2many('hr.employee', string="Agents")
    contact_ids = fields.Many2many('res.partner', string="Contacts", domain=_get_contact_domain, track_visibility="onchange")
    language_id = fields.Many2one("res.lang", "Preferred Language", related="contact_id.language_id")
    name = fields.Char("Reference #", readonly=True, track_visibility="onchange" ) #To replace ref with name ,ref where deleted
    lang_ids = fields.Many2many("res.lang", string ="Preferred Languages", track_visibility="onchange" )
    enq_date = fields.Datetime("Enquiry Date", default=datetime.now().date())
    future_action_date = fields.Datetime("Future Action Date", track_visibility="onchange")
    dead_line = fields.Date("Dead Line")
    lead_type = fields.Selection([('land_lord','Land Lord'),('tenant','Tenant'), ('buyer','Buyer'), ('seller','Seller'),
                                  ('investor','Investor'),('agent','Agent')], required=False, track_visibility="onchange")
    finance = fields.Selection([('cash','Cash'),('loan_approved','Loan (approved)'),
                                ('loan_not_approved','Loan (not approved)')],
                                "Finance")
    priority = fields.Selection([
                                ('urgent','Urgent'),
                                ('high','High'),
                                ('low','Low'),
                                ('normal','Normal')
                            ], "Priority", default= "normal", track_visibility="onchange")
    is_hot_lead = fields.Selection([('yes','Yes'),('no','No')],"Hot Lead", default="no", track_visibility="onchange")
    # auto_assign = fields.Boolean(default=True, help="Auto assign using rota", string="Auto Assign")
    auto_assign = fields.Boolean(default=_get_value_for_auto_asign, help="Auto assign using rota", string="Auto Assign")
    lead_source_id = fields.Many2one("source.master","Lead Source", required=True, track_visibility="onchange" )
    sub_status_id = fields.Many2one("lead.sub.status", "Pre-qualified Status", required=False, track_visibility="onchange",
                                    default=lambda self:self.env["lead.sub.status"].search([('name','=','New')],limit=1).id)
    state = fields.Selection([('new','New'),('work_Progress','Work In Progress'),('closed','Closed')], string="Status", required=True, default="new")
    user_uid = fields.Many2one("res.users", string="Created By", track_visibility="onchange", required=True, readonly=True, default=lambda self: self.env.user)
    note_ids = fields.One2many('crm.notes', 'lead_id', string="Note History")
    is_notify_agent = fields.Boolean("Notify Agent")
    lead_req_ids = fields.One2many("atk.lead.requirement", "lead_id", string="Property Requirement", required=True)
    customer_email_id = fields.Char(related="contact_id.email", string="Email", track_visibility="onchange")
    customer_mobile = fields.Char(related="contact_id.mobile", string="Phone", track_visibility="onchange")
    country_id = fields.Many2one("res.country", string="Country", default=_default_country)
    isd_code_id = fields.Many2one('res.country.code', related="contact_id.isd_code_id",string="IDD", track_visibility="onchange" )
    list_ids = fields.Many2many("listing.listing", store=False)
    match_list_ids = fields.Many2many("listing.listing", store=False)
    create_action = fields.One2many("action.action", "lead_id", string="Action")
    title = fields.Char(string="Title", track_visibility="onchange" )
    matching_listing = fields.Many2many('listing.listing')
    lead_offered_unit_ids = fields.One2many('lead.offered.unit','lead_id', default=False)
    share_scope = fields.Selection([('Internal','Internal/Network'), ('External','External Sub-broker')], track_visibility="onchange", default="Internal",string="Share with")
    category_id_list= fields.Many2one("listing.category", string="Category")
    emirate_id_list = fields.Many2one("res.country.state", string='Emirate/City')
    location_id_list = fields.Many2one("res.location", string="Location")
    sub_location_id_list = fields.Many2one("res.sub.location", string="Sub-Location")
    loss_reason = fields.Many2one('loss.reason', string="Reason for Loss", track_visibility="onchange")
    is_lost = fields.Boolean(default=False)
    is_qualified = fields.Boolean(default=False)
    is_matching_listing = fields.Boolean()
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id.id)

    opportunity_id = fields.Many2one("lead.opportunity", "Opportunity ref#")
    offered_unit_id = fields.Many2one("lead.offered.unit", "Finalized Unit", domain=[], track_visibility="onchange")
    opportuninty_stage = fields.Selection([('Viewing', 'Viewing'), ('Negotiation', 'Negotiation')],
                                           string="Opportunity Stage", track_visibility="onchange")
    won_or_lost = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')], track_visibility="onchange", default="In Progress")
    view_won_or_lost = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')], default="In Progress")
    nego_won_or_lost = fields.Selection([('In Progress', 'In Progress'), ('Won', 'Won'), ('Lost', 'Lost')], default="In Progress")
    comment = fields.Text(string="Comments", related="opportunity_id.comments")
    notes = fields.Text(string="Note", related="opportunity_id.note")
    commission_value_opportunity = fields.Float(string="Expected Commission Value", track_visibility="onchange")
    deal_id = fields.Many2one("deal.deal", string="Deal Id", track_visibility="onchange")
    close_date_opportunity = fields.Datetime(string="Expected Close Date", track_visibility="onchange")
    viewing_count = fields.Integer()
    pool_status = fields.Selection([('Agent Assigned','Agent Assigned'),('Lead Pool','Lead Pool'),('Network Pool','Network Pool')], default="Agent Assigned")
    agent_assign_time = fields.Datetime()
    agent_confidence_score = fields.Integer()
    document_ids = fields.Many2many('ir.attachment', 'lead_attach_rel', 'lead_id', 'attach_id')
    lead_write_date = fields.Datetime()
    lead_write_uid = fields.Many2one('res.users')
    agent_performance_id = fields.Many2one('agent.performance')
    points = fields.Integer('Points')
    accessible_user_ids = fields.Many2many('res.users')
    match_listing_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')], string="Listing Type", compute="_get_listing_type", store=False)

    # marketing
    # email_recipients = fields.Many2many('res.partner', string="Email To", store=True)
    email_recipients = fields.Char(string="Email To")
    email_recipients_2 = fields.Many2many('res.partner', string="Email To", store=True)
    mail_recipients = fields.Many2many('res.partner', string="Email To", store=True)
    email_from = fields.Char(string="From")
    email_subject = fields.Char(string="Subject")
    email_message = fields.Text(string="Message")
    is_sign = fields.Boolean(string="Signature")
    email_sign = fields.Html(string="Signature")

    is_assigned = fields.Boolean(default=False)
    mail_msg_ids = fields.One2many('mail.message','lead_id', domain=[('message_type','=','contact')])
    adhoc_listing = fields.Char(string="Adhoc Listing")
    default_or_adhoc = fields.Selection([('From Listing(Default)', 'From Listing'), ('Adhoc Listing', 'Adhoc Listing')], track_visibility="onchange", default="From Listing(Default)")
    matching_listing_ids = fields.Char()
    add_from_listing = fields.Boolean("Add Listing")

    # Collected from backup
    # @api.multi
    # def convert_deal(self):
    #     view = self.env.ref('asteco_crm.wizard_listing_form')
    #     vals = {
    #         'name': _('Select Listing'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'listing.selection.wizard',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'context': {'lead_id': self.id}
    #     }
    #     return vals



    @api.multi
    def convert_deal(self):
        view = self.env.ref('asteco_crm.wizard_listing_form')
        vals = {
            'name': _('Select Listing'),
            'type': 'ir.actions.act_window',
            'res_model': 'listing.selection.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'context': {'lead_id': self.id}
        }
        return vals

    @api.multi
    def add_listings(self):
        view = self.env.ref('asteco_crm.wizard_listing_form')
        vals = {
            'name': _('Select Listing'),
            'type': 'ir.actions.act_window',
            'res_model': 'listing.selection.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'context': {'lead_id': self.id}
        }
        return vals

    @api.multi
    @api.depends('lead_type')
    def _get_listing_type(self):
        for lead in self:
            if lead.lead_type in ['buyer', 'investor', 'agent']:
                type = 'Sale'
            elif lead.lead_type == 'tenant':
                type = 'Rental'
            else:
                type = False
            lead.match_listing_type = type

    @api.onchange('country_id')
    def _onchange_country_id(self):
        # if self.env.user.user_type == self.env['res.user.type'].search([('name','=','Agent Broker')]):
        #     self.agent_id = self.env.user.id
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    @api.onchange('agent_id')
    def onchange_agent_id(self):
        if self.agent_id:
            self.auto_assign = False
        else:
            self.auto_assign = True

    @api.onchange('country_id')
    def onchange_country(self):
        self.isd_code_id = self.env['res.country.code'].search([('country_id', '=', self.country_id.id)], limit=1).id

    @api.onchange('view_won_or_lost')
    def onchange_viewing_status(self):
        return {'domain':{'offered_unit_id':[('id','in',self.lead_offered_unit_ids.ids)]}}

    @api.onchange('opportuninty_stage')
    def onchange_opportuninty_stage(self):
        if self.opportuninty_stage == 'Viewing' and self.won_or_lost == 'In Progress':
            self.opportunity_id.state = 'Viewing'
            self.opportunity_id.lead_sub_status_id = 'Viewing'
            self.opportunity_id.viewings_status = 'In Progress'
        elif self.opportuninty_stage == 'Negotiation' and self.won_or_lost == 'In Progress':
            self.opportunity_id.state = 'Negotiation'
            self.opportunity_id.lead_sub_status_id = 'Negotiation'
            self.opportunity_id.negotiation_status = 'In Progress'

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ATKLeadLead, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     for lead in self.env['atk.lead.lead'].search([], limit=10):
    #         lead.update_matching_listing()
    #     return res

    @api.constrains('commission_value_opportunity')
    def _check_commission_value(self):
        for record in self:
            if record.is_qualified == True and record.commission_value_opportunity <= 0.00:
                raise ValidationError("Please enter a valid amount for opportunity commission!!!")

    @api.constrains('future_action_date')
    def _check_future_action(self):
        for record in self:
            if record.future_action_date:
                if datetime.strptime(record.future_action_date,'%Y-%m-%d %H:%M:%S') < datetime.now():
                    raise Warning("Please enter a valid future action date !!!")

    @api.constrains('close_date_opportunity')
    def _check_expected_action(self):
        for record in self:
            if record.close_date_opportunity:
                if datetime.strptime(record.close_date_opportunity,'%Y-%m-%d %H:%M:%S') < datetime.now():
                    raise Warning("Please enter a valid expected close date !!!")        

    @api.constrains('customer_mobile')
    def _check_mobile(self):
        for record in self:
            if len(record.customer_mobile) < 7 or len(record.customer_mobile) > 15:
                raise ValidationError("Please enter a valid mobile number!!!")

    @api.constrains('customer_email_id')
    def validate_mail(self):
        for record in self:
            if record.customer_email_id:
                match = re.match('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-z]{2,4})$', record.customer_email_id)
                if match == None:
                    raise ValidationError('Please enter a valid E-mail ID!!!')

    @api.multi
    def update_matching_listing(self):
        lead = self
        lead.matching_listing = False
        listing_list = []
        if len(lead.lead_req_ids) > 0:
            requirement = lead.lead_req_ids[0]
            domain = [('category_id', '=', requirement.category_id.id), ('emirate_id', '=', requirement.emirate_id.id), ('company_id','=',lead.company_id.id)]
            if requirement.location_id:
                domain.append(('location_id', '=', requirement.location_id.id))
            if requirement.bed_id:
                domain.append(('bed_id', '=', requirement.bed_id.id))
            elif requirement.fitted_id:
                domain.append(('fitted_id', '=', requirement.fitted_id.id))
            if lead.lead_type in ['tenant']:
                domain.append(('listing_type', 'in', ['Rental']))
            elif lead.lead_type in ['buyer', 'investor', 'agent']:
                domain.append(('listing_type', 'in', ['Sale']))
            else:
                return
            if requirement.max_bua:
                domain.append(('build_up_area_sqf', '<=', requirement.max_bua))
                domain.append(('build_up_area_sqf', '>=', requirement.min_bua))
            if requirement.max_price:
                domain.append(('price', '>=', requirement.min_price))
                domain.append(('price', '<=', requirement.max_price))
            listing_ids = self.env['listing.listing'].search(domain, limit=5, order="list_write_date desc")
            for listing in listing_ids:
                listing_list.append(listing.id)
            listing_list = list(set(listing_list))
            if listing_list:
                lead.matching_listing = listing_list
                lead.is_matching_listing = True
            else:
                lead.matching_listing = False
                lead.is_matching_listing = False
        else:
            lead.matching_listing = False
            lead.is_matching_listing = False

    @api.onchange('emirate_id')
    def set_values(self):
        if self.emirate_id:
            idl = self.env['res.location'].search([('emirate_id','=',self.emirate_id.id)])
            return {'domain':{'location_id':[('id','in',idl.ids)],}}

    @api.onchange('location_id')
    def set_values_to(self):
        if self.location_id:
            ids = self.env['res.sub.location'].search([('location_id','=',self.location_id.id)])
            return {'domain':{'sub_location_id':[('id','in',ids.ids)],}}



    @api.model
    def create(self, vals):
        if 'lead_req_ids' in vals and vals['lead_req_ids']:
            self.get_First_Property(vals)
        else:
            raise Warning("You can't create lead without a property requirement!!!")
        res = super(ATKLeadLead, self).create(vals)
        lead_rot_id = False
        auto_assign = 'N'
        if res.auto_assign:
            auto_assign = 'Y'
            lead_rot_id = res.auto_assign_lead_agent()
        
        res.name = res.company_id.code + self.env['ir.sequence'].next_by_code('atk.lead.lead')     

        if res.sub_status_id and res.sub_status_id.name == 'Qualified':
            res.create_opportunity(res)

        if res.agent_id:
            res.create_lead_assign_history(lead_rot_id,auto_assign)
            res.create_auto_action_schedules()
        elif not res.agent_id:
            agent_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])            
            if agent_id:
                res.agent_id = agent_id.id
                res.create_lead_assign_history(lead_rot_id,auto_assign)

        res.send_sms_to_contact(res.name, res.isd_code_id, res.customer_mobile,res.agent_id)
        res.send_sms_to_agent(res.name, res.agent_id, res.contact_id ,res.isd_code_id ,res.customer_mobile, res.customer_email_id)
        res.send_lead_creation_mail(1)
        return res

    @api.multi
    def create_auto_action_schedules(self):
        for record in self.env['auto.action.scheduler'].search([('module','=',self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1).id), ('object_id','=',self.id)]):
            record.is_active = False
        code = self.env.user.company_id.code if self.env.user.company_id.code else ""
        seq = code + self.env['ir.sequence'].next_by_code('auto.action.task.scheduler')
        for action in self.env['auto.action'].search([('status','=','Active'),('module','=','Leads')]):
            if action.trigger == 'Check Value' and action.interval_type in ['Hour(s)','Minute(s)']:
                if action.interval_type == 'Hour(s)':
                    interval = action.interval*60
                else:
                    interval = action.interval
                next_execution_time = datetime.now() + timedelta(minutes=interval)
                self.env['auto.action.scheduler'].create({
                        'module': self.env['ir.model'].search([('model','=','atk.lead.lead')], limit=1).id,
                        'object_id' : self.id,
                        'rule_id' : action.id,
                        'schedule_time' : next_execution_time,
                        'is_active' : True,
                        'seq':seq,
                    })
        self.agent_assign_time = datetime.now()
        return
        
    # def get_mail_url(self):
    #     return self.get_share_url()

    # @api.multi
    # def action_registered_lead_sent(self):
    #     # self.ensure_one()
    #     template = self.env.ref('asteco_crm.email_template_lead_for_contacts', False)
    #     compose_form= self.env.ref('mail.email_compose_message_wizard_form', False)
    #     ctx = {
    #         'default_model' :'atk.lead.lead',
    #         'default_res_id':self.id,
    #         'default_use_template':False,
    #         'default_template_id':template and template.id or False,
    #         'default_composition_mode':'comment',
    #         'mark_so_as_sent': True,
    #         # 'custom_layout':"asteco_crm.mail_template_data_notification_email_proforma_invoice",
    #         'force_email':True,
    #         }
    #     # mail_object=self.env[mail.mail]
        # mail_object.create({
        #     'subject' :''
        #     'email_from':'company_id.email'
        #     'recipient_ids':'agent_id.id'
        #     'email_cc':
        #     'reply_to':
        #     'scheduled_date':
        #     'body_html':
        #     })
        # return {
        #     'name': _('Compose Email'),
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(compose_form.id, 'form')],
        #     'view_id': compose_form.id,
        #     'target': 'new',
        #     'context': ctx,
        #     }

    @api.multi
    def choose_recipients(self):
        return
        

    @api.multi
    def send_mail(self, msg):
        email_to = str(self.customer_email_id)
        if self.agent_id:
            email_to += "," + str(self.agent_id.user_id.email)
        mail = self.env['mail.mail'].create({
                'subject':'Lead Creation',
                'email_from':self.env.user.company_id.email,
                'email_to':email_to,
                'body_html':msg,
            })
        mail.send()
        return

    @api.multi
    def send_lead_creation_mail(self,flag):
        if self.agent_id.work_email and self.name and self.contact_id.name and self.customer_mobile and self.customer_email_id:
            mail_template = self.env.ref("asteco_crm.lead_creation_mail")
            values = mail_template.sudo().generate_email(self.id)
            values['email_from']= self.company_id.email
            values['email_to'] = self.agent_id.work_email
            _subject_to_agent_ = "New Lead  "+self.name
            _header_to_agent_ = "New Lead "+self.name
            _msg_to_agent_ = "The following lead has to been assigned to, <br/><p style='padding-left:225px;'>"+self.contact_id.name+"</p><p style='padding-left:225px;'>"+self.isd_code_id.country_code +self.customer_mobile+"<p/><p style='padding-left:225px;'>"+self.customer_email_id+"</p>"
            values['subject'] = _subject_to_agent_
            values['body_html'] = values['body_html'].replace("_msg_", _msg_to_agent_).replace("_header_",_header_to_agent_)
            values['reply_to'] = self.company_id.email
            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()
        if flag == 1:
            if self.customer_email_id and self.name and self.company_id.email:
                mail_template = self.env.ref("asteco_crm.lead_creation_mail")
                values_for_customer = mail_template.sudo().generate_email(self.id)
                values_for_customer['email_from']= self.company_id.email
                values_for_customer['email_to'] = self.customer_email_id
                _subject_ = "Enquiry Reference  "+self.name
                _header_ = "Requested Property "+self.name
                _msg_ = "Dear Customer,<br/> Thank you for contacting us. The reference number of your enquiry is "+self.name+". Our agent will be contacting you shortly. In case you need more information you can contact us at the below number"
                values_for_customer['subject'] = _subject_
                values_for_customer['body_html'] = values_for_customer['body_html'].replace("_msg_", _msg_).replace("_header_",_header_)
                values_for_customer['reply_to'] = self.company_id.email
                send_mail = self.env['mail.mail'].create(values_for_customer)
                send_mail.send()


    @api.multi
    def create_lead_assign_history(self,lead_rot_id,auto_assign):      #taking that value into this function
        for lead in self:
            self.env['lead.assign.history'].create({
                'agent_id' : lead.agent_id.id if lead.agent_id else False,
                'lead_id' : lead.id,
                'lead_rot_id' : lead_rot_id.id if lead_rot_id else False, #assigning that value into the field, that in the other table(lead.assign.history)
                'assign_time' : datetime.now(),
                'auto_assign' : auto_assign,
            })
            
    @api.multi
    def auto_assign_lead_agent(self):
        lead_rot_id = False
        for lead in self:
            if lead.lead_req_ids:
                first_req = lead.lead_req_ids[0]
                lead_rot_obj = self.env['lead.rotation']
                domain = []
                domain.append(('agent_status', '=', True))
                domain.append(('agent_id.emp_user_type', '!=', self.env.ref('asteco_crm.coordinator').id))
                domain.append(('last_assingned_date','!=',False))
                domain.append(('leads_count','=',0))
                domain.append('|')
                domain.append(('lead_type', '=', lead.lead_type))
                domain.append(('lead_type', '=', 'Any'))
                domain.append(('company_id','=',self.env.user.company_id.id))
                if first_req.category_id:
                    property_use_type = self.env['listing.category'].search([('name','=',first_req.category_id.name)]).property_use_type
                    if property_use_type == 'Residential':
                        domain.append('|')
                        domain.append(('commercial_residential','=','residential'))
                        domain.append(('commercial_residential','=','Any'))
                    elif property_use_type == 'Commercial':
                        domain.append('|')
                        domain.append(('commercial_residential','=','commercial'))
                        domain.append(('commercial_residential','=','Any'))
                if first_req.emirate_id:
                    domain.append('|')
                    domain.append(('emirate_id', '=', first_req.emirate_id.id))
                    domain.append(('emirate_any_null', '=', 'any'))
                else:
                    domain.append(('emirate_any_null', '=', 'any'))

                if first_req.sub_location_id:
                    domain.append('|')
                    domain.append(('sub_location_id', '=', first_req.sub_location_id.id))
                    domain.append(('sub_location_any_null', '=', 'any'))
                else:
                    domain.append(('sub_location_any_null', '=', 'any'))

                if first_req.location_id:
                    domain.append('|')
                    domain.append(('location_id', '=', first_req.location_id.id))
                    domain.append(('location_any_null', '=', 'any'))
                else:
                    domain.append(('location_any_null', '=', 'any'))
                lead_rot_id = lead_rot_obj.search(domain, order="last_assingned_date asc", limit=1)
                if not lead_rot_id:
                    domain.remove(('leads_count','=',0))
                    lead_rot_id = lead_rot_obj.search(domain, order="last_assingned_date asc", limit=1)
            if not lead_rot_id:
                domain = [] #creating new domain for co-ordinator selection
                lead_rot_obj = self.env['lead.rotation'] 
                domain.append(('agent_status', '=', True)) #to ensure that the co-ordinator is available or not
                domain.append(('last_assingned_date','!=',False))  
                domain.append(('agent_id.emp_user_type', '=', self.env.ref('asteco_crm.coordinator').id)) #setting domain for co-ordinator, if there is no others are available
                domain.append(('leads_count','=',0))
                domain.append(('company_id','=',lead.company_id.id))
                lead_rot_id = lead_rot_obj.search(domain, order="last_assingned_date asc", limit=1) #taking one record from the sale manager based on last assigned date
                if not lead_rot_id:
                    domain.remove(('leads_count','=',0))
                    lead_rot_id = lead_rot_obj.search(domain, order="last_assingned_date asc", limit=1)
            if lead_rot_id:
                lead.agent_id = lead_rot_id.agent_id.id
                lead.auto_assign = False
                return lead_rot_id 
            else:
                raise Warning("The Co-ordinator is Away or There are no rules set on the Lead Rotation Table!\nPlease turn off Auto-assign and continue or contact IT.")

    @api.multi
    def write(self, vals):
        flag = 0
        if len(vals) == 1:
            if 'is_matching_listing' in vals or 'matching_listing' in vals or 'agent_performance_id' in vals:
                flag = 1

        if flag == 0:
            vals['lead_write_date'] = datetime.now()
            vals['lead_write_uid'] = self.env.user.id


            agent_user = False
            if 'agent_id' in vals and vals['agent_id']:
                agent_user = self.env['hr.employee'].browse(vals['agent_id']).user_id.id
            elif self.agent_id:
                agent_user = self.agent_id.user_id.id
            if agent_user:
                if agent_user == self.env.user.id:
                    vals['state'] = 'work_Progress' 
        res = super(ATKLeadLead, self).write(vals)

        if 'adhoc_listing' in vals and vals['adhoc_listing']:
            raise Warning("Sorry!!! Feature not activated!!!")  

        if 'agent_id' in vals and vals['agent_id']:
            self.is_assigned = True
            self.env.user.check_is_a_child(vals['agent_id'])
            self.send_sms_to_agent(self.name, self.agent_id, self.contact_id ,self.isd_code_id ,self.customer_mobile, self.customer_email_id)
            self.send_lead_creation_mail(0)
            # self.action_assigned_lead_to_agent_sent()
            self.create_auto_action_schedules()
        elif 'agent_id' in vals and vals['agent_id'] == False:
            self.is_assigned = False


        if 'lead_req_ids' in vals and vals['lead_req_ids']:
            self.get_First_Property({})
            # self.update_matching_listing()
        if 'sub_status_id' in vals:
            if self.sub_status_id.name in ['Qualified']:
                self.state = 'work_Progress'
                self.is_qualified = True
                self.create_opportunity(self)
                self.opportuninty_stage = 'Viewing'
            else:
                self.is_qualified = False
        if 'commission_value_opportunity' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('lead_id','=',self.id),('state','in',['Qualified','Viewings'])], limit=1)
            if opportunity_id:
                opportunity_id.commission_value = vals['commission_value_opportunity']
        if 'close_date_opportunity' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('lead_id','=',self.id),('state','in',['Qualified','Viewings'])], limit=1)
            if opportunity_id:
                opportunity_id.close_date = vals['close_date_opportunity']
        if 'view_won_or_lost' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('lead_id','=',self.id),('state','in',['Qualified','Viewings'])], limit=1)
            if vals['view_won_or_lost'] == 'Won':
                self.opportuninty_stage = 'Negotiation'
                if opportunity_id:
                    # opportunity_id.state = 'Negotiation'
                    opportunity_id.stage_id = self.env['opportunity.stage'].search([('name', '=', 'Negotiation')]).id
                    opportunity_id.listing_id = self.offered_unit_id.listing_id.id
                    opportunity_id.commission_value = self.commission_value_opportunity
                    opportunity_id.close_date = self.close_date_opportunity
                    if self.offered_unit_id:
                        self.offered_unit_id.status = 'Negotiation'
            elif vals['view_won_or_lost'] == 'Lost':
                if self.offered_unit_id:
                    self.offered_unit_id.status = 'Failed'
                if opportunity_id:
                    opportunity_id.state = 'Lost'
        if 'nego_won_or_lost' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('lead_id','=',self.id),('state','=','Negotiation')], limit=1)
            if vals['nego_won_or_lost'] == 'Won':
                self.state = 'closed'
                if opportunity_id:
                    # opportunity_id.state = 'Converted to Deal'
                    opportunity_id.stage_id = self.env['opportunity.stage'].search([('name', '=', 'Converted to Deal')]).id
                    opportunity_id.commission_value = self.commission_value_opportunity
                    self.offered_unit_id.status = 'Converted to Deal'
                    self.deal_id = opportunity_id.deal_id = self.env['deal.deal'].create({
                        'lead_id': opportunity_id.lead_id.id,
                        'state': 'in_Progress',
                        'listing_id': opportunity_id.listing_id.id,
                        'gross_commission': opportunity_id.lead_id.commission_value_opportunity,
                        'estimated_date': opportunity_id.lead_id.close_date_opportunity,
                        'deal_price':opportunity_id.listing_id.price,
                        'deposit':opportunity_id.listing_id.deposit_amount,
                        'sub_status_id': 'Documentation',
                    }).id
            elif vals['nego_won_or_lost'] == 'Lost':
                self.offered_unit_id.status = 'Failed'
                if opportunity_id:
                    opportunity_id.state = 'Lost'
        if 'comment' in vals:
            self.env['crm.notes'].create({
                    'name':vals['comment'],
                    'lead_id':self.id,
                })
            vals['comment'] = ''
        if 'lead_offered_unit_ids' in vals:
            pass

        return res


    # @api.multi
    # def action_assigned_lead_to_agent_sent (self):
    #     # self.ensure_one()
    #     template = self.env.ref('asteco_crm.email_template_lead_assign_to_agent', False)
    #     compose_form= self.env.ref('mail.email_compose_message_wizard_form', False)
    #     ctx = {
    #         'default_model' :'atk.lead.lead',
    #         'default_res_id':self.id,
    #         'default_use_template':False,
    #         'default_template_id':template and template.id or False,
    #         'default_composition_mode':'comment',
    #         'mark_so_as_sent': True,
    #         # 'custom_layout':"asteco_crm.mail_template_data_notification_email_proforma_invoice",
    #         'force_email':True,
    #         }
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form.id, 'form')],
    #         'view_id': compose_form.id,
    #         'target': 'new',
    #         'context': ctx,
    #         }


    @api.multi
    def update_opportunity(self):
        qualified_status_id = self.env['opportunity.stage'].search([('name','=','Qualified')], limit=1)
        opportunity_id = self.env['lead.opportunity'].search([('stage_id','=',qualified_status_id.id),('lead_id','=',self.id)], limit=1)
        if opportunity_id:
            for record in self.lead_offered_unit_ids:
                if record.status == 'Pending':
                    sub_status_id = self.env['lead.sub.status'].search([('name','=','Viewings')], limit=1)
                    viewing_status_id = self.env['opportunity.stage'].search([('name','=','Viewings')], limit=1)
                    if sub_status_id:
                        self.sub_status_id = sub_status_id.id
                    opportunity_id.listing_id = record.listing_id.id
                    opportunity_id.commission_value = self.commission_value_opportunity
                    opportunity_id.stage_id = viewing_status_id.id
                    opportunity_id.state = 'Viewings'
                    opportunity_id.qualified_status = 'Won'
                    opportunity_id.viewings_status = 'In Progress'
                    record.status = 'Viewings'
                    break
            self.opportunity_id = opportunity_id.id
        return

    @api.multi
    def create_opportunity(self, vals):
        stage_id = self.env['opportunity.stage'].search([('name','=','Qualified')], limit=1)
        self.env['lead.opportunity'].create({
            'lead_id':vals.id,
            'customer_id':vals.contact_id.id,
            'title':vals.name,
            'qualified_status':'In Progress',
            'state':'Qualified',
            'stage_id':stage_id.id,
        })
        return

    @api.multi
    def get_First_Property(self, vals):
        if vals:
            vals['category_id_list'] = vals['lead_req_ids'][0][2]['category_id'] if 'category_id' in vals['lead_req_ids'][0][2] else False
            vals['emirate_id_list'] = vals['lead_req_ids'][0][2]['emirate_id'] if 'emirate_id' in vals['lead_req_ids'][0][2] else False
            vals['location_id_list'] = vals['lead_req_ids'][0][2]['location_id'] if 'location_id' in vals['lead_req_ids'][0][2] else False
            vals['sub_location_id_list'] = vals['lead_req_ids'][0][2]['sub_location_id'] if 'sub_location_id' in vals['lead_req_ids'][0][2] else False
            return vals
        if self.lead_req_ids:
            self.category_id_list = self.lead_req_ids[0].category_id.id
            self.emirate_id_list = self.lead_req_ids[0].emirate_id.id
            self.location_id_list = self.lead_req_ids[0].location_id.id
            self.sub_location_id_list = self.lead_req_ids[0].sub_location_id.id

    @api.onchange('sub_status_id')
    def onchange_sub_status_id(self):
        if self.sub_status_id.name == 'Lead Lost':
            self.is_lost = True
        else:
            self.is_lost = False

    @api.multi
    @api.onchange('list_ids')
    def onchange_list_ids(self):
        for deal in self:
            for list in deal.list_ids:
                deal.lead_req_ids = [(0, 0,
                                      {
                                    'category_id' : list.category_id.id,
                                    'emirate_id' : list.emirate_id.id,
                                    'location_id' : list.location_id.id,
                                    'sub_location_id': list.sub_location_id.id,
                                    'bed_id' : list.bed_id.ids,
                                    'list_id' : list.id,
                                        })]
            deal.list_ids = False

    @api.onchange('match_list_ids')
    def onchange_match_list_ids(self):
        if len(self.match_list_ids) > 1:
            raise Warning("You cannot select more than one listing at a time!")
        for record in self.lead_offered_unit_ids:
            if self.match_list_ids.id == record.listing_id.id:
                raise Warning("Selected listing already added!")
        if self.match_list_ids:
            self.lead_offered_unit_ids = [(0,0, {
                        'listing_id': self.match_list_ids.id,
                        'status':'Pending',
                 })]

    @api.multi
    def name_get(self):
        result = []
        for lead in self:
            name = str(lead.name)
            result.append((lead.id, name))
        return result

    @api.multi
    def add_listing(self):
        pass

    @api.multi
    def convert_to_deal(self):
        pass

    @api.multi
    def send_email(self):
        return    

    @api.multi
    def send_sms(self):
        return
        mobile = self.isd_code_id.country_code + self.customer_mobile
        # mobile = "+919947047536"
        if self.name and mobile and self.agent_id:

            # new_ids = list_ids[2:-2].split('","')
            # listing_ids = "["
            # for item in new_ids:
            #     listing_ids += str(item)+"-"
            # listing_ids = listing_ids[:-1]
            # listing_ids += "]"
            # if listing_ids:
            server = " https://odoo.asteco.ae/"
            msg = "Dear Customer, We are sharing the below listings for your consideration. \n" + server + "preview/listings/" + "listing_ids" + "?debug "




        # msg = "Dear Customer,\nThank you for contacting us. The reference for your enquiry is " + reference_number +". Our Agent "+agent_id.name+" "+agent_id.work_phone+" will be contacting you shortly.\n\nThanks and Regards,\nAsteco Customer Service Team"
            URL = "http://ae.infosatme.com/sms/smsapi?api_key=C20025715d77dfa65e7bc4.16782074%20&type=text&contacts=" + mobile + "&senderid=ASTECO&msg=" + msg + "&scheduledDateTime=" + str(datetime.now())
            r = requests.get(URL)
            return True

        # return
    
    @api.multi
    def send_whatsapp(self):
        return
        return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+"917034658288"+"&text=" + "Hi nishitha.. this is from odoo team. hope you had a great tea and pokkavada!",
                'target': 'new',
                'res_id': self.id,
            }
    
    @api.multi
    def send_sms_to_contact(self,reference_number, isd_code_id, customer_mobile,agent_id):
        mobile = isd_code_id.country_code + customer_mobile
        if reference_number and mobile and agent_id and agent_id.work_phone:
            msg = "Dear Customer,\nThank you for contacting us. The reference for your enquiry is " + reference_number +". Our Agent "+agent_id.name+" "+agent_id.work_phone+" will be contacting you shortly.\n\nThanks and Regards,\nAsteco Customer Service Team"
            URL = "http://ae.infosatme.com/sms/smsapi?api_key=C20025715d77dfa65e7bc4.16782074%20&type=text&contacts=" + mobile + "&senderid=ASTECO&msg=" + msg + "&scheduledDateTime=" + str(datetime.now())
            r = requests.get(URL)
        return True

    @api.multi
    def send_sms_to_agent(self, reference_number, agent_id, contact_id ,isd_code_id ,customer_mobile, customer_email_id):
        if agent_id.work_phone and reference_number and isd_code_id.country_code and customer_mobile and customer_email_id:
            mobile_agent = agent_id.work_phone
            msg_agent = "The Lead reference  " + reference_number +" has been assigned to you. The contact details of the customer are "+ contact_id.name +", "+isd_code_id.country_code + customer_mobile+" and "+customer_email_id+"\n\nThanks and Regards,\nAsteco Customer Service Team"
            URL = "http://ae.infosatme.com/sms/smsapi?api_key=C20025715d77dfa65e7bc4.16782074%20&type=text&contacts=" + mobile_agent + "&senderid=ASTECO&msg=" + msg_agent + "&scheduledDateTime=" + str(datetime.now())
            r = requests.get(URL)
        return True


        # return
        # raise Warning("Sorry!!!\nSMS Not Activated!")

    @api.multi
    def add_match_list(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def action_log_phone_call(self):
        view_id = self.env.ref('asteco_crm.log_phone_call_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add phone call log',
            'res_model': 'log.phone.call.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }

    @api.multi
    def open_lead(self):
        view_id = self.env.ref('asteco_crm.atk_lead_lead_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead',
            'res_model': 'atk.lead.lead',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': self.id,
        }

    @api.multi
    def send_preview_mail(self):
        self.ensure_one()
        flag = 0
        listing_ids = "["
        for record in self.matching_listing:
            flag = 1
            listing_ids += str(record.id) + "-"
        if flag == 0:
            raise Warning("Sorry!!! No matching listing found!")
        self.matching_listing_ids = listing_ids[:-1] + "]"
        template = self.env.ref('asteco_crm.email_template_listing_preview_from_lead', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        self.mail_recipients += self.contact_id
        ctx = dict(
            default_model='atk.lead.lead',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            default_partner_ids=self.mail_recipients.ids,
            mark_invoice_as_sent=True,
            custom_layout="asteco_crm.mail_template_multi_listing_preview",
            force_email=True
        )
        self.mail_recipients = False
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    # @api.multi
    # def convert_to_deal(self):
    #

class ATKLeadRequirement(models.Model):
    _name = "atk.lead.requirement"

    def _default_country(self):
        return self.env.user.company_id.country_id.id
        # return self.env['res.country'].search([('name','=','United Arab Emirates')])

    slno = fields.Integer("No.", compute="_sequence_ref")

    ref_req = fields.Char()
    category_id = fields.Many2one("listing.category", string="Category", track_visibility="onchange")
    emirate_id = fields.Many2one("res.country.state", string="Emirate/City", track_visibility="onchange")
    country_id = fields.Many2one("res.country", string="Country", default=_default_country, track_visibility="onchange")
    location_id = fields.Many2one("res.location", string="Location", track_visibility="onchange")
    sub_location_id = fields.Many2one("res.sub.location", string="Sub-Location")
    bed_id = fields.Many2one('listing.bed',string="Bed")
    fitted_id = fields.Many2one('listing.fitted',string="Fitted")
    min_bua = fields.Float("BUA (min.)")
    max_bua = fields.Float("BUA (max.)")
    lead_id = fields.Many2one("atk.lead.lead", "Lead")
    list_id = fields.Many2one("listing.listing", "Listing")
    min_price = fields.Float("Min. Price")
    max_price = fields.Float("Max. Price")
    is_office = fields.Boolean()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    
    @api.multi
    @api.onchange('contact_id')
    def onchange_contact(self):
        self.country_id = self.contact_id.country_id.id

    # @api.onchange('emirate_id')
    # def set_values(self):
    #     if self.emirate_id:
    #         idl = self.env['res.location'].search([('emirate_id','=',self.emirate_id.id)])
    #         return {'domain':{'location_id':[('id','in',idl.ids)],}}

    # @api.onchange('location_id')
    # def set_values_to(self):
    #     if self.location_id:
    #         ids = self.env['res.sub.location'].search([('location_id','=',self.location_id.id)])
    #         return {'domain':{'sub_location_id':[('id','in',ids.ids)],}}


    #------ Changes ------
    @api.onchange('sub_location_id')
    def set_values_for_emirates_and_location(self):
        if self.sub_location_id:

            idl = self.env['res.location'].search([('id','=',self.sub_location_id.location_id.id)]) # taking location using sub-location
            self.location_id = idl.id # setting location

            ide = self.env['res.country.state'].search([('id','=',idl.emirate_id.id)]) #taking emirate_id using location_id
            self.emirate_id = ide.id #setting emirate 
            return 

    @api.onchange('location_id')
    def set_values_for_emirates_and_sub_location(self):
        if self.location_id:
            ide = self.env['res.country.state'].search([('id','=',self.location_id.emirate_id.id)]) #taking emirate_id using location_id
            self.emirate_id = ide.id #setting emirate 
            ids = self.env['res.sub.location'].search([('location_id','=',self.location_id.id)]) # taking sub-locations ids using location
            return {'domain':{'sub_location_id':[('id','in',ids.ids)],}}  # returning domain for sub-locations

    @api.onchange('emirate_id')
    def set_values_for_location(self):
        if self.emirate_id:
            idl = self.env['res.location'].search([('emirate_id','=',self.emirate_id.id)]) # taking location using emirate_id
            if not self.location_id :
                return {'domain':{'location_id':[('id','in',idl.ids)], 'sub_location_id':[('id','in',False)],}} # returning domain 
            else:
                return {'domain':{'location_id':[('id','in',idl.ids)],}}
            # return {'domain':{'location_id':[('id','in',idl.ids)],}}
    #----- End -----

    @api.depends('lead_id.lead_req_ids', 'lead_id.lead_req_ids.category_id')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.lead_id.lead_req_ids:
                no += 1
                l.slno = no

    @api.multi
    def get_filtered_listing(self):
        self.ensure_one()
        view = self.env.ref('asteco_crm.listing_tree_view')
        domain = []
        if self.category_id:
            domain.append(('category_id','=',self.category_id.id))

        if self.emirate_id:
            domain.append(('emirate_id','=',self.emirate_id.id))
        if self.location_id:
            domain.append(('location_id','=',self.location_id.id))
        if self.sub_location_id:
            domain.append(('sub_location_id','=',self.sub_location_id.id))
        if self.bed_id:
            domain.append(('bed_id','=',self.bed_id.id))
        if self.min_bua:
            domain.append(('price','>=',self.min_bua))
        if self.max_bua:
            domain.append(('price', '<=', self.max_bua))
        if self.min_price:
            domain.append(('price','>=',self.min_price))
        if self.max_price:
            domain.append(('price', '<=', self.max_price))
        return {
            'name': _('Matching listings'),
            'type': 'ir.actions.act_window',
            'res_model': 'listing.listing',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'target': 'new',
            'views': [(False,'kanban'),(view.id, 'list'), (False, 'form')],
            'context': {},
            'domain' : domain,
        }

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id.name in ['Office', 'Retail', 'Warehouse']:
            self.is_office = True
            self.bed_id = False
        else:
            self.is_office = False
            self.fitted_id = False

class LeadOfferedUnit(models.Model):
    _name = 'lead.offered.unit'

    lead_id = fields.Many2one('atk.lead.lead', required=1)
    listing_id = fields.Many2one('listing.listing', required=1)
    category_id = fields.Many2one('listing.category', related="listing_id.category_id")
    emirate_id = fields.Many2one('res.country.state', related="listing_id.emirate_id")
    location_id = fields.Many2one('res.location', related="listing_id.location_id")
    sub_location_id = fields.Many2one('res.sub.location', related="listing_id.sub_location_id")
    agent_id = fields.Many2one('hr.employee', related="listing_id.agent_id")
    bed_id = fields.Many2one('listing.bed', related="listing_id.bed_id")
    price = fields.Float('listing.listing', related="listing_id.price")

    status = fields.Selection([('Pending','Pending'), ('Viewings','Viewings'), ('Negotiation','Negotiation'), ('Converted to Deal','Converted to Deal'), ('Success','Success'), ('Failed','Failed')])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def name_get(self):
        result = []
        for unit in self:
            name = str(unit.listing_id.ref_name)
            result.append((unit.id, name))
        return result

class ListingListingLeads(models.Model):
    _inherit = 'listing.listing'

    lead_id = fields.Many2one("atk.lead.lead", "Lead")

class LeadSubStatus(models.Model):
    _name = "lead.sub.status"
    _order = "name asc"

    name = fields.Char("Name")
    state = fields.Selection([
        ('new', 'New'), ('work_Progress', 'Work In Progress'), ('success', 'Successful'),
        ('unsuccess', 'Unsuccessful')], string="State")

class CrmNotesLeads(models.Model):
    _inherit = "crm.notes"

    lead_id = fields.Many2one("atk.lead.lead", "Lead")

class SelectFromListing(models.TransientModel):
    _name = "listing.selection.wizard"

    listing_select = fields.Many2one('listing.listing', "Select Listing")

    @api.multi
    def confirm_list(self):
        context = self._context.get('active_ids')
        lead_object = self.env['atk.lead.lead'].browse(context)
        self.confirm_list_implementation(lead_object, self.listing_select)
        return

    @api.multi
    def confirm_list_implementation(self,lead_object,listing_select):
        qualified_stage = lead_object.sub_status_id = self.env.ref('asteco_crm.sub_status10')

        view = self.env['lead.offered.unit'].create({
            'lead_id':lead_object.id,
            'listing_id':listing_select.id,
            'category_id': listing_select.category_id.id,
            'emirate_id': listing_select.emirate_id.id,
            'location_id': listing_select.location_id.id,
            'sub_location_id':listing_select.sub_location_id.id,
            'status':'Pending',
        })
        finalised_unit = lead_object.offered_unit_id = view
        qualified_stage = lead_object.view_won_or_lost = 'Won'
        viewing_stage = lead_object.nego_won_or_lost = 'Won'

    @api.multi
    def confirm_list_api(self,vals):
        try:
            lead_id = vals['lead_id']
            listing_id = vals['listing_id']
            lead_obj = self.env['atk.lead.lead'].browse(lead_id)
            listing_obj = self.env['listing.listing'].browse(listing_id)
            self.confirm_list_implementation(lead_obj,listing_obj)
            return True
        except UserError as e:
            return False