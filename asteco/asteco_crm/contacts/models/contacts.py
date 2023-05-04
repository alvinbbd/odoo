from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from datetime import datetime,timedelta
import pytz
import logging
import re
_logger = logging.getLogger(__name__)


class ATKContactContact(models.Model):
    _inherit = 'res.partner'

    def _get_default_country(self):
        return self.env.user.company_id.country_id.id
        # return self.env['res.country'].search([('name', '=', 'United Arab Emirates')])
# selection
    contact_type = fields.Selection([('private', 'Private'), ('within_company', 'Within Company'), ('network', 'Network')],
                                    required=True, default="within_company", track_visibility="onchange")

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], track_visibility="onchange")
    head = fields.Selection([('individual', 'Individual'), ('company', 'Company')], default='individual')
    contact_rate = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                                    "Contact Rating", track_visibility="onchange")
    title = fields.Selection(
        [('mr', 'Mr'), ('mrs', 'Mrs'), ('miss', 'Miss'), ('ms', 'Ms'), ('mx', 'Mx'), ('master', 'Master'),
         ('sir', 'Sir')], "Title", track_visibility="onchange")
    change_items = fields.One2many('mail.message','contact_id')



# Char
    name = fields.Char(index=True, track_visibility="onchange")
    mobile = fields.Char(track_visibility="onchange")
    email = fields.Char(track_visibility="onchange")
    ref_name = fields.Char("Ref#", readonly=True)
    # country_code = fields.Char(related="country_id.code", string="Country code", required=True)
    source = fields.Char("Contact source", track_visibility="onchange")
    ofc_phn = fields.Char("Phone (Company)", track_visibility="onchange")
    home_phn = fields.Char("Phone (Home)", track_visibility="onchange")
    company_email = fields.Char("Company Email", track_visibility="onchange")
    customer_trn = fields.Char("Customer TRN No.(for VAT)", track_visibility="onchange")
    warning_msg = fields.Char('Warning')
    atk_company_id = fields.Char("Company Name", track_visibility="onchange")
    fax = fields.Char("Fax", track_visibility="onchange")
    # created_by = fields.Char("Created by", readonly=True)
    address = fields.Text("Address", track_visibility="onchange")
    notes = fields.Text("Notes")
    # note_history = fields.Text("Note history", readonly=True,required=True)
    reason = fields.Text("Reason", track_visibility="onchange")
    isd_code = fields.Integer()
    website = fields.Char(help="Website of Partner or Company", track_visibility="onchange")

# Many2one
    assigned_to_id = fields.Many2one("hr.employee", "Assigned to", track_visibility="onchange")
    shared_with_id = fields.Many2one("hr.employee", "Shared with", track_visibility="onchange")
    city_id = fields.Many2one("res.country.state", "Emirate/City",required=True, track_visibility="onchange")
    nationality_id = fields.Many2one("res.country", "Nationality", track_visibility="onchange")
    religion_id = fields.Many2one("res.religion", "Religion", track_visibility="onchange")
    language_id = fields.Many2one("res.lang", domain=[('active', '=', True)], track_visibility="onchange")
    source = fields.Many2one("source.master", "Source" ,required=True, track_visibility="onchange")
    # user_id = fields.Many2one("res.users", "User", readonly=True)
    listing_action = fields.Many2one("listing.listing", "Listing")
    lead_action = fields.Many2one("atk.lead.lead", "Lead")
    contact_owner = fields.Many2one("res.users", string="Contact owner", track_visibility="onchange")
    designation = fields.Many2one("hr.designation", string="Designation", track_visibility="onchange")
    country_id = fields.Many2one('res.country', default=_get_default_country,required=True, track_visibility="onchange")
    isd_code_id = fields.Many2one('res.country.code', "IDD", required="True", track_visibility="onchange")
    primary_contact = fields.Many2one("res.partner", "Primary Contact", domain= [('is_contact','=',True)], track_visibility="onchange")

# Many2many
    contact_classif_ids = fields.Many2many("contact.classification", string="Contact Classification", track_visibility="onchange")
    hobbies = fields.Many2many("res.hobbies", string="Hobbies", track_visibility="onchange")
    document_ids = fields.Many2many('ir.attachment', 'contact_attach_rel', 'contact_id', 'attach_id')


# One2many
    social_media_ids = fields.One2many("contacts.social.media", "partner_id", track_visibility="onchange")
    notes_ids = fields.One2many('crm.notes', 'partner_id', string="Note History")
    create_action = fields.One2many("action.action", "contact_id", string="Action")

# Boolean
    is_vip = fields.Boolean("Contact VIP", track_visibility="onchange")
    is_link_to_contact = fields.Boolean("Link to Company", track_visibility="onchange")
    is_notify_agent = fields.Boolean("Notify Agent")
    image = fields.Binary("Image")
    is_contact = fields.Boolean("Is Contact")

# Date
    dob = fields.Date("Date of Birth", track_visibility="onchange")

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for contact in self:
    #         name = str(contact.name)
    #         if contact.is_contact:
    #             name = str(contact.ref_name) + "-" + name
    #         result.append((contact.id, name))
    #     return result


    @api.multi
    def create_lead_for_contact(self):
        country = self.isd_code_id.country_id
        view_id = self.env.ref('asteco_crm.atk_lead_lead_view_form')
        return {
            'name': 'Create Lead',
            'type': 'ir.actions.act_window',
            'res_model': 'atk.lead.lead',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [[view_id.id, 'form']],
            'context': {'default_contact_id': self.id, 'default_country_id':country},
        }

    

    # @api.multi
    # def create_mail_msg(self,msg):
    # 	self.env['mail.message'].create({
    # 			'body':msg,
    # 			'contact_id':self.id,
    # 		})
    


    @api.onchange('country_id')
    def onchange_country(self):
        self.isd_code_id = self.env['res.country.code'].search([('country_id', '=', self.country_id.id)], limit=1).id

    @api.onchange('isd_code_id')
    def onchange_isd_code(self):
        if self.isd_code_id: 
            country_id = self.env['res.country'].search([('phone_code', '=', self.isd_code_id.country_code)], limit=1).id
            if country_id:
                self.country_id = country_id


            # else:
            #     self.country_id = ""
            #     raise ValidationError("Please check IDD  !!!")


    @api.onchange('primary_contact')
    def onchange_email(self):
        if self.primary_contact:
            self.email = self.primary_contact.email
            self.mobile = self.primary_contact.mobile

    @api.onchange('email')
    def onchange_email(self):
        if self.email:
            existing_email = self.env['res.partner'].search([('email','=',self.email)])
            if existing_email:
                self.email = False
                raise ValidationError("Email id is already exist!!!")


    def save(self):
        return

    def cancel(self):
        return

    @api.constrains('ref_name')
    def _check_reference(self):
        for record in self:
            if record.ref_name == False:
                raise ValidationError("You cannot create contact without basic information!!!")

    @api.constrains('mobile')
    def _check_mobile(self):
        for record in self:
            if len(record.mobile) < 7 or len(record.mobile) > 15:
                raise ValidationError("Please enter a valid mobile number!!!")

    @api.constrains('email')
    def validate_mail(self):
        for record in self:
            if record.email:
                match = re.match('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-z]{2,4})$', record.email)
                # match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+) *@[a-z0-9-]+(\.[a-z0-9-]+) *(\.[a-z]{2,4})$', record.email)
                if match == None:
                    raise ValidationError('Please enter a valid E-mail ID!!!')

    @api.onchange('country_id')
    def set_values_to(self):
        if self.country_id:
            ids = self.env['res.country.state'].search([('country_id','=',self.country_id.id)])
            return {'domain':{'city_id':[('id','in',ids.ids)],}}

    @api.onchange('contact_type')
    def private_to_assigned_user(self):
        if self.contact_type == 'private':
            self.assigned_to_id = self.env.user.employee_ids.id
        else:
            self.assigned_to_id = ""

    @api.model
    def create(self, vals):
        if 'is_contact' in vals and vals['is_contact']:
            vals['ref_name'] = self.env.user.company_id.code + self.env['ir.sequence'].next_by_code('res.partner.contact.seq')
        result_with_same_email = result = self
        if 'email' in vals and vals['email']:
            result_with_same_email = self.search([('email', '=', vals['email'])])
            # result_with_same_email.write({'warning_msg': 'Contact already exist with same E-mail Id !!!'})
        # If contact exist with same email id then return that contact.
        if result_with_same_email and len(result_with_same_email) == 1:
            raise Warning("Contact already exist with same E-mail Id !!!")
            
            # result_with_same_email.write({'warning_msg': 'Contact already exist with same E-mail Id !!!'})
            # raise ValidationError(_("Employee already exist %s")% result_with_same_email.ref)
            if not result_with_same_email.is_contact:
                result_with_same_email.is_contact = True
            result_with_same_email.write(vals)
            return result_with_same_email
        elif len(result_with_same_email) > 1:
            raise ValidationError(_('Same contact exist more than 1 record !!'))
        if 'name' in vals and vals['name'] and 'mobile' in vals and vals['mobile']:
            result = self.search([('name', '=', vals['name']), ('mobile', '=', vals['mobile'])])
        if result and len(result) == 1:
            # raise ValidationError(_("Employee already exist %s")% result_with_same_email.ref)
            # result.write({'warning_msg': 'Contact already exist with same Name and Mobile # !!!'})
            return result
        elif len(result) > 1:
            raise ValidationError(_('Same contact exist more than 1 record !!'))
        return super(ATKContactContact, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'email' in vals and 'flag' not in self._context:
            if vals['email'] != self.email:
                contact = self.search([('email','=',vals['email'])], limit=1)
                if contact:
                    contact.with_context(flag=True).write(vals)
                    return contact
        if 'name' in vals and 'mobile' in vals and 'test_abc' not in self._context:
            if vals['name'] != self.name and vals['mobile'] != self.mobile:
                contact = self.search([('name','=',vals['name']), ('mobile','=',vals['mobile'])], limit=1)
                if contact:
                    return contact
        res = super(ATKContactContact, self).write(vals)
        return res

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


    # @api.model
    # def create(self, vals):
    #     res = super(ATKContactContact, self).create(vals)
    #     res.contact_validation(vals)
    #     return res
    #
    # @api.model
    # def write(self):
    #     self.contact_validation(vals)
    #     return super(ATKContactContact, self).create(vals)



    # @api.onchange('country_id', 'country_id.phone_code')
    # def onchange_start_stop_datetime(self):
    #     if self.start_datetime:
    #         self.start = self.start_datetime
    #     if self.stop_datetime:
    #         self.stop = self.stop_datetime


class ResCity(models.Model):
    _name = 'res.city'

    name = fields.Char(sring="Name")


class ResLanguage(models.Model):
    _name = 'res.language'

    name = fields.Char(sring="Name")


class ResNationality(models.Model):
    _name = 'res.nationality'

    name = fields.Char(sring="Name")


class ResReligion(models.Model):
    _name = 'res.religion'

    name = fields.Char(sring="Name")


class SourceMaster(models.Model):
    _name = 'source.master'

    name = fields.Char(sring="Name")


class CompanyMaster(models.Model):
    _name = 'company.master'

    name = fields.Char(sring="Name")


class ATKContactsSocialMedia(models.Model):
    _name = 'contacts.social.media'

    image = fields.Binary('Image', related='type.image')
    # type = fields.Selection(,
    #     [('facebook', 'Facebook'), ('whatsapp', 'Whatsapp'), ('twitter', 'Twitter'), ('linkedln', 'Linkedln'),
    #      ('skype', 'Skype'), ('instagram', 'Instagram'), ('website', 'Website')], string="Type")
    type = fields.Many2one('social.media', string="Social Media")
    url = fields.Char(string="URL")
    partner_id = fields.Many2one("res.partner", readonly=True)


class SocialMedia(models.Model):
    _name = 'social.media'

    name = fields.Char('Name')
    image = fields.Binary('Image')


class ContactClassification(models.Model):
    _name = 'contact.classification'

    name = fields.Char(sring="Name")


class Hobbies(models.Model):
    _name = 'res.hobbies'

    name = fields.Char(sring="Name")


class CrmNotes(models.Model):
    _inherit = "crm.notes"

    partner_id = fields.Many2one('res.partner', string="Contacts")


class ATKDesignatiom(models.Model):
    _name = "hr.designation"

    # parent_id = fields.Many2one('hr.designation', "Parent Designation")
    name = fields.Char('Designation')


class LogNote(models.Model):
    _inherit = "mail.message"

    contact_id = fields.Many2one('res.partner')
    listing_id = fields.Many2one('listing.listing')
    lead_id = fields.Many2one('lead.lead')
    deal_id = fields.Many2one('deal.deal')
    message_type = fields.Selection([
        ('email', 'Email'),
        ('comment', 'Comment'),
        ('notification', 'System notification'),
        ('contact', 'Contact History'),],
        'Type', required=True, default='email',
        help="Message type: email for email message, notification for system "
             "message, comment for other messages such as user replies",
        oldname='type')


class LogPhoneCallWizard(models.TransientModel):
    _name = "log.phone.call.wizard"

    contact_id = fields.Many2one('res.partner', string="Contact", domain= [('is_contact','=',True)])
    date_and_time = fields.Datetime(default=datetime.now(), required=True)
    listing_id = fields.Many2one('listing.listing')
    lead_id = fields.Many2one('lead.lead')
    deal_id = fields.Many2one('deal.deal')
    notes = fields.Text('Notes')

    @api.multi
    def save(self):
        contact_id = listing_id = lead_id = deal_id = False
        if 'default_contact_id' in self._context:
            contact_id = self._context['default_contact_id']
        if 'default_listing_id' in self._context:
            listing_id = self._context['default_listing_id']
        if 'default_lead_id' in self._context:
            lead_id = self._context['default_lead_id']
        if 'default_deal_id' in self._context:
            deal_id = self._context['default_deal_id']
        notes = ''
        if self.notes:
            notes = self.notes
        self.env['mail.message'].create({
            'body' : "Call on " + self.get_timezone_time(self.date_and_time) + '<br/>' + notes,
            # 'body' : "Call on " + self.get_timezone_time(self.date_and_time)+'<br/>'+str(self.notes),
            'contact_id' : contact_id,
            'listing_id' : listing_id,
            'lead_id' : lead_id,
            'deal_id' : deal_id,
            'message_type' : 'contact'
        })

    @api.multi
    def get_timezone_time(self, time):
        user_tz = self.env.user.company_id.tz or "Asia/Dubai"
        display_date_result = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        gmt = pytz.timezone('GMT')
        usertzobj = pytz.timezone(user_tz)
        dategmt = gmt.localize(display_date_result)
        return dategmt.astimezone(usertzobj).strftime("%d-%m-%Y %I:%M %p")