from odoo import fields, models, api
import pytz


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_meeting_mail_domain(self):
        return [('model_id', '=', self.env.ref('asteco_crm.model_action_action').id)]

    def _get_email_invoice_template_domain(self):
        return [('model_id', '=', self.env.ref('asteco_crm.model_crm_proforma_invoice').id)]

    @api.model
    def _tz_get(self):
        # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
        return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


    rera_orn = fields.Char(string="RERA ORN")
    fax = fields.Char(string="Office Fax")
    company_profile = fields.Text(string="Company Profile")
    # phone_office_id = fields.Many2one('res.partner')
    admin_mobile = fields.Char(related='admin_user_id.phone_office')

    address = fields.Text(string="Address")

    company_logo = fields.Binary(string="Logo")
    company_watermark = fields.Binary(string="Watermark")
    company_default_image = fields.Binary(string="Default Image")

    xml_name = fields.Selection([('Company', 'Company'), ('Agent', 'Agent')], string="XML Name")
    xml_number = fields.Selection([('Company', 'Company'), ('Agent', 'Agent')], string="XML Number")
    xml_email = fields.Selection([('Company', 'Company'), ('Agent', 'Agent')], string="XML Email")

    # inv_template = fields.Char(string="Invoice and Receipt Template")
    enable_vat = fields.Boolean(string="Enable VAT")
    vat = fields.Char(string="VAT(%)")
    # unit_measure = fields.Char(string="Measuring Unit")
    # pos_watermark = fields.Char(string="Watermark Position")
    lead_pool_limit = fields.Integer(string="Lead Pool Limit Per Day")
    bank_payment_details = fields.Html(string="Bank Payment Details")

    watermark = fields.Char(string="Watermark")

    pdf_template = fields.Char(string="Choose PDF Template")
    email_html_template = fields.Char(string="Choose Email HTML Template")
    api_key_type = fields.Char(string="API Key Type")
    api_key = fields.Char(string="API Key")
    pdf_color = fields.Char(string="Choose PDF Color")
    prev_color = fields.Char(string="Choose Email HTML Color")
    email_html_color = fields.Char(string="Choose Preview Color")

    out_mail_server_id = fields.Many2one('ir.mail_server')
    imap_server = fields.Char(string="IMAP Server", related="out_mail_server_id.name")
    inbound_server = fields.Char(string="Inbound Server")
    outbound_server = fields.Char(string="Outbound Server", related="out_mail_server_id.smtp_host")
    company_mail = fields.Char(string="Company Email User ID", related="out_mail_server_id.smtp_user")
    company_email_password = fields.Char(default='', copy=False, string="Password", related="out_mail_server_id.smtp_pass",
                                         help="Keep empty if you don't want the user to be able to connect on the system.")
    sms_credit_limit = fields.Integer(string="SMS Credit Limit")
    smtp_encryption = fields.Selection([('none', 'None'),
                                        ('starttls', 'TLS (STARTTLS)'),
                                        ('ssl', 'SSL/TLS')], string='Connection Security', default='none', related="out_mail_server_id.smtp_encryption")

    admin_user_id = fields.Many2one('res.users', string="Administrator")
    bank_payment_details = fields.Html(string="Bank Payment Details")
    email_template = fields.Many2one('mail.template', string="Email Template")

    email_invoice_template = fields.Many2one('mail.template', string="Invoice Email Template",
                                             domain=_get_email_invoice_template_domain)
    email_lead_template = fields.Many2one('mail.template', string="Lead Created Email Template")
    marketing_email_temp_id = fields.Many2one('mail.template', string="Marketing Email Template")
    receipt_email_temp_id = fields.Many2one('mail.template', string="Receipt Email Template")
    lead_assign_agent_mail_temp_id = fields.Many2one('mail.template', string="Lead Assign to Agent Email Template")
    lead_assign_coordinator_mail_temp_id = fields.Many2one('mail.template',
                                                           string="Lead Assign to Co-Ordinator Email Template")
    alert_mail_temp_id = fields.Many2one('mail.template', string="Alert to Agent and Manager Email Template")
    share_lead_temp_id = fields.Many2one('mail.template', string="Share Leads Email Template")
    meeting_mail_temp_id = fields.Many2one('mail.template', string="Meeting Email Template",
                                           domain=_get_meeting_mail_domain)
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'))
    company_signature = fields.Html(string="Signature")
    code = fields.Char(string="Code")
    country_id = fields.Many2one('res.country')

    base_url = fields.Text()
    listing_count = fields.Integer(default=0)
    stage_pull_time = fields.Char()

    @api.multi
    def validate(self):
        pass

    @api.model
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        if 'outbound_server' in vals and vals['outbound_server']:
            if not res.out_mail_server_id:
                res._create_outgoing_mail_server(vals)
        if 'inbound_server' in vals and vals['inbound_server']:
            res._create_incoming_mail_server()
        res.create_sequences()
        if self.env.user.has_group('asteco_crm.group_super_admin'):
            self.env.user.company_ids += res
        res
        return res

    @api.multi
    def create_sequences(self):
        seqObj = self.env['ir.sequence']
        seq_list = [
            {'name' : 'Contact Sequence','code' : 'res.partner.contact.seq','padding' : 4,'prefix' : '-C-'},
            {'name' : 'Lead Sequence','code' : 'atk.lead.lead','padding' : 4,'prefix' : '-L-'},
            {'name' : 'Lead Rotation Sequence','code' : 'atk.lead.rotation','padding' : 4,'prefix' : 'ROTA'},
            {'name' : 'Sequence Listing Sale','code' : 'listing.listing.sale','padding' : 4,'prefix' : '-S-'},
            {'name' : 'Sequence Listing Rental','code' : 'listing.listing.rental','padding' : 4,'prefix' : '-R-'},
            {'name' : 'Deal Sequence','code' : 'deal.deal','padding' : 4,'prefix' : '-D-'},
            {'name' : 'Invoice Sequence','code' : 'crm.proforma.invoice','padding' : 4,'prefix' : 'Proforma/'},
            {'name' : 'Receipt Sequence','code' : 'crm.temporary.receipt','padding' : 4,'prefix' : 'Temp.Receipt/'},
            {'name' : 'Auto Action Reference','code' : 'auto.action','prefix' : '-AUTO-ACTION-'},
            {'name' : 'Auto Action Task Scheduler Reference','code' : 'auto.action.task.scheduler','prefix' : 'ATS'},
            {'name' : 'Enquiry Sequence','code' : 'listing.enquiry','padding' : 3,'prefix' : '-ENQ-'},
        ]
        for item in seq_list:
            item['company_id'] = self.id
            seqObj.create(item)


    @api.multi
    def write(self, vals):
        outbound_name = self.company_mail
        inbound_name = self.company_mail
        res = super(ResCompany, self).write(vals)
        if 'outbound_server' in vals and vals['outbound_server']:
            if not self.out_mail_server_id:
                self._create_outgoing_mail_server(vals)
        if 'imap_server' in vals or 'company_mail' in vals or 'company_email_password' in vals or 'outbound_server' in vals or 'inbound_server' in vals or 'smtp_encryption' in vals:
            self._update_mail_servers(vals, inbound_name, outbound_name)
        # if 'inbound_server' in vals:
        # 	values ={
        # 		'name': self['inbound_server'],
        # 		'type': 'imap',
        # 		'server': vals['inbound_server'],
        # 		'user': self['company_mail'] or False,
        # 		'password':self['company_email_password'] or False,
        # 	}
        # 	incoming_server = self.env['fetchmail.server'].create(values)
        # if 'outbound_server' in vals:
        # 	values ={
        # 		'name': self['outbound_server'],
        #
        # 		'server': vals['outbound_server'],
        # 		'smtp_user': self['company_mail'] or False,
        # 		'smtp_pass':self['company_email_password'] or False,
        # 		'smtp_host':vals['outbound_server'],
        # 		'smtp_encryption':'ssl'
        # 	}
        # 	outgoing_server = self.env['ir.mail_server'].create(values)
        return res

    @api.multi
    def _create_incoming_mail_server(self):
        mail_server_obj = self.env['fetchmail.server']
        mail_server_obj.create({
            'name': self.company_mail,
            'type': 'imap',
            'server': self.inbound_server,
            'user': self.company_mail or False,
            'password': self.company_email_password or False,
        })
        return True

    @api.multi
    def _create_outgoing_mail_server(self,vals):
        mail_server_obj = self.env['ir.mail_server']
        self.out_mail_server_id = mail_server_obj.create({
            'name': vals['company_mail'],
            'smtp_host': vals['outbound_server'],
            'smtp_encryption': vals['smtp_encryption'],
            'smtp_user': vals['company_mail'] or False,
            'smtp_pass': vals['company_email_password'] or False,
        })
        return True

    @api.multi
    def _update_mail_servers(self, vals, inbound_name, outbound_name):
        inbound_values = {}
        outbound_values = {}
        if 'company_mail' in vals:
            inbound_values['user'] = outbound_values['smtp_user'] = vals['company_mail']
            inbound_values['name'] = outbound_values['name'] = vals['company_mail']
        if 'company_email_password' in vals:
            inbound_values['password'] = outbound_values['smtp_pass'] = vals['company_email_password']
        if 'outbound_server' in vals:
            outbound_values['smtp_host'] = vals['outbound_server']
        if 'inbound_server' in vals:
            inbound_values['server'] = vals['inbound_server']
        if 'smtp_encryption' in vals:
            outbound_values['smtp_encryption'] = vals['smtp_encryption']
        if inbound_values:
            mail_server_obj = self.env['fetchmail.server']
            if inbound_name:
                inbound_id = mail_server_obj.search([('name', '=', inbound_name)], limit=1)
                if inbound_id:
                    inbound_id.write(inbound_values)
                else:
                    self._create_incoming_mail_server()
            else:
                self._create_incoming_mail_server()
        if outbound_values:
            mail_server_obj = self.env['ir.mail_server']
            if outbound_name:
                outbound_id = mail_server_obj.search([('name', '=', outbound_name)], limit=1)
                if outbound_id:
                    outbound_id.write(outbound_values)
                else:
                    pass
            else:
                pass

    @api.model
    def update_company_data(self):
        self.env['res.company'].search([('id','=',1)]).currency_id.symbol = 'AED'
        user_id = self.env['res.users'].search([('id','=',1)])
        user_id.is_super_admin_it_main = True
        user_id.groups_id += self.env.ref('asteco_crm.group_super_admin_main')
        language_id = self.env['res.lang'].search([('name','=','English')]).date_format = "%d/%m/%Y"
        for department in self.env['hr.department'].search([]):
            department.company_id = False
