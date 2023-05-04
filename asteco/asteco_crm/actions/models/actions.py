from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
import pytz

_logger = logging.getLogger(__name__)


class Actions(models.Model):
    _name = 'action.action'
    _inherits = {'calendar.event': 'event_id'}
    _order = 'create_date desc'
    _description = "Action"

    action_id = fields.Many2one("res.partner", domain=[('is_contact', '=', True)])
    contact_id = fields.Many2one("res.partner", domain=[('is_contact', '=', True)])
    offered_unit_id = fields.Many2one('lead.offered.unit', string="Offered Unit", domain=[])

    listing_id = fields.Many2one("listing.listing", "Ref No")
    lead_id = fields.Many2one("atk.lead.lead", "Ref No")
    name = fields.Char(related='event_id.name', inherited=True, string="Subject", required=True)
    start_datetime = fields.Datetime(related='event_id.start_datetime', inherited=True, string="Start Time")
    stop_datetime = fields.Datetime(related='event_id.stop_datetime', inherited=True, string="End Time")
    duration = fields.Float(related='event_id.duration', inherited=True, string='Duration')
    status = fields.Selection([('scheduled','Scheduled'),('cancelled','Cancelled'),('successful','Successful'),('unsuccessful','Unsuccessful'),('missed','Missed'),('done','Done')],
                              string="Status", default="scheduled")
    state = fields.Selection([('draft', 'Unconfirmed'), ('open', 'Confirmed')], string='State', readonly=True,
                             track_visibility='onchange', default='draft', related='event_id.state', inherited=True)
    start = fields.Datetime('Start', related='event_id.start', inherited=True)
    stop = fields.Datetime('Stop', related='event_id.stop', inherited=True)
    start_date = fields.Date('Start Date',  related='event_id.start_date', inherited=True)
    stop_date = fields.Date('Stop Date', related='event_id.stop_date', inherited=True)
    action_type = fields.Selection([
        ('reminder','Reminder'),('meeting','Meeting'),
        ('viewings','Viewings'),('documentation','Documentation'),
        ('open_house','Open House'),('events','Events'),
        ('agent_tour','Agent Tour'),('calls','Calls')])
    item = fields.Selection([
        ('listing','Listing'),('lead','Lead'),
        ('contacts','Contacts'),('oppertunities','Oppertunities'),('deals','Deals')])
    agents_ids = fields.Many2many("hr.employee", string="Agents")
    contacts_ids = fields.Many2many("res.partner", string="Contacts", domain=[('contact_type', 'in', ['network','within_company'])])
    location = fields.Char("Location", related='event_id.location')
    message = fields.Html('Message or Note')
    date_and_time = fields.Datetime(default=datetime.now(), required=True)

    event_id = fields.Many2one('calendar.event', required=True, ondelete='restrict', auto_join=True,
                                 string='Event')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.onchange('action_type')
    def onchange_action_type(self):
        return {'domain':{'offered_unit_id':[('id','in',self.lead_id.lead_offered_unit_ids.ids)]}}

    @api.model
    def create(self, vals):
        res = super(Actions, self).create(vals)
        res.event_id.write({'action_id': res.id})
        # if len(res.agents_ids) > 0:
        #     res.event_id.agents_ids = res.agents_ids
        # if res.action_type:
        #     res.event_id.action_type = res.action_type
        # if res.item:
        #     res.event_id.item = res.item
        # if res.message:
        #     res.event_id.description = res.message
        if res.action_type == 'viewings' and res.lead_id != False:
            res.lead_id.viewing_count += 1
            opportunity_id = self.env['lead.opportunity'].search([('lead_id','=',res.lead_id.id),('state','=','Qualified')], limit=1)
            if opportunity_id:
                # opportunity_id.state = 'Viewings'
                opportunity_id.stage_id = self.env['opportunity.stage'].search([('name', '=', 'Viewings')]).id
                opportunity_id.commission_value = res.lead_id.commission_value_opportunity
                opportunity_id.close_date = res.lead_id.close_date_opportunity
                if res.lead_id.offered_unit_id:
                    res.lead_id.offered_unit_id.status = 'Viewings'
        res.send_mail_to_client()
        return res

    @api.multi
    def send_mail_to_client(self):
        for action in self:
            # mail_template = self.env.ref("asteco_crm.direct_meeting_mail_template")
            mail_template = self.env.user.company_id.meeting_mail_temp_id
            if mail_template:
                vals = mail_template.generate_email(action.id, fields=None)
                if action.contacts_ids:
                    type = False
                    if 'default_listing_id' in self._context:
                        type = 'Listing'
                        ref = action.listing_id.ref_name
                        contact_id = action.listing_id.customer_id
                    elif 'default_lead_id' in self._context:
                        type = 'Lead'
                        ref = action.lead_id.name
                        contact_id = action.lead_id.contact_id
                    elif 'default_contact_id' in self._context:
                        type = 'Contact'
                        ref = action.contact_id.ref_name
                        contact_id = action.contact_id
                    agent_id = self.agents_ids.browse(self._context['default_agents_ids'][0][2])
                    start_date = stop_date ='Not mentioned'
                    if action.start_datetime:
                        start_date = self.get_timezone_time(action.start_datetime)
                    if action.stop_datetime:
                        stop_date = self.get_timezone_time(action.stop_datetime)
                    if agent_id:
                        vals['email_from'] = agent_id.name + "<" + agent_id.user_id.email or agent_id.user_id.login
                        vals['email_from'] += ">"
                        vals['recipient_ids'] = [[6,0,action.contacts_ids.ids]]
                        vals['subject'] = 'Direct Mail for ' + type + " - " + ref
                        vals['body_html'] = vals['body_html'].replace("_recipient_name", contact_id.name).replace("_start_datetime", start_date).replace("_stop_datetime", stop_date).replace("_signature", agent_id.user_id.signature)
                        
                        mail_mail_obj = self.env['mail.mail']
                        mail_id = mail_mail_obj.create(vals)
                        mail_id.send()
                        email_action = self.env['mail.message']
                        for mail_contact in action.contacts_ids:
                            email_action.create(
                                {
                                  'lead_id' : action.lead_id.id or False,
                                  'listing_id': action.listing_id.id or False,
                                  'contact_id': mail_contact.id or False,
                                  'body' : "Lead ref : " + str(action.lead_id.name)+'<br/>'+"Listing ref : " +str(action.listing_id.ref_name)+'<br/>'+"Agent : "+agent_id.name+'<br/>'+"Contact : "+mail_contact.name+'<br/>'+ self.get_timezone_time(self.date_and_time),
                                  'agent_id' : agent_id,
                                  'message_type' : 'contact'
                                })
                        # res = super(Actions, self).create(vals)       
            else:
                raise ValidationError("Please choose a meeting email template!!!")

    @api.multi
    def get_timezone_time(self, time):
        user_tz = self.env.user.company_id.tz or "Asia/Dubai"
        display_date_result = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        gmt = pytz.timezone('GMT')
        usertzobj = pytz.timezone(user_tz)
        dategmt = gmt.localize(display_date_result)
        return dategmt.astimezone(usertzobj).strftime("%d-%m-%Y %I:%M %p")


    def unlink(self):
        self.event_id.unlink()
        res = super(Actions, self).unlink()
        return res


    @api.onchange('start_datetime','stop_datetime')
    def onchange_start_stop_datetime(self):
        if self.start_datetime:
            self.start = self.start_datetime
        if self.stop_datetime:
            self.stop = self.stop_datetime

    @api.model
    def update_status(self):
        _logger.info('*********************Getting inside update status method*********************')
        current_datetime = datetime.now()
        for action in self.search([('status', '=', 'scheduled')]):
            if current_datetime > datetime.strptime(action.stop_datetime, "%Y-%m-%d %H:%M:%S"):
                action.status = 'missed'
                _logger.info('**  Within the condition - %s  **', (action))
        _logger.info('*********************Getting Out from update status method*********************')

    @api.multi
    def action_save(self):
        result=self.listing_id.write({'create_action': [(6, 0, [self.id])]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    #
    # @api.multi
    # def action_discard(self):
    #     return {
    #         'type': 'ir.actions.act_window_close',
    #     }

    @api.multi
    def action_done(self):
        self.status = 'done'



