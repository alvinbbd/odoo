
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import pytz
import babel.dates
from odoo.tools import html2plaintext

class ProformaInvoice(models.Model):
    _name = "crm.proforma.invoice"
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']
    _description = "Proforma Invoice"

    @api.depends('Payment_amount','vat_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.Payment_amount + record.vat_amount

    name = fields.Char(string="Ref #",track_visibility="always")
    partner_id = fields.Many2one('res.partner',"Customer",track_visibility="always")
    mobile = fields.Char(string="Mobile",related="partner_id.mobile",track_visibility="onchange")
    email = fields.Char(string="Email",related="partner_id.email",track_visibility="onchange")
    deal_id = fields.Many2one("deal.deal", string='Deal Ref #',track_visibility="onchange")
    date_invoice = fields.Date(string='Invoice Date',track_visibility="onchange",
        readonly=True,  index=True,
        help="Keep empty to use the current date", copy=False, default=lambda self:datetime.now().date())
    date_due = fields.Date(string='Due Date',track_visibility="onchange")
    agent_id = fields.Many2one("hr.employee", "Agent", related="deal_id.shared_with_id", readonly=False,track_visibility="onchange")
    narration = fields.Text(string="Narration",track_visibility="onchange")
    address = fields.Text(string="Address")
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',track_visibility="onchange")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('received', 'Received'),],
        string='Status', index=True, readonly=True, default='issued',
        track_visibility='onchange', copy=False)
    number = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('deal.deal'))

    # Payment_amount = fields.Float(related="deal_id.deposit", string="Amount",track_visibility="onchange")
    Payment_amount = fields.Float(string="Invoice Amount")
    vat_amount = fields.Float(string=" VAT Amount")
    net_amount = fields.Float(string="Net Invoice Amount", compute=_compute_net_amount)
    currency_id = fields.Many2one('res.currency', related="partner_id.currency_id")
    
    @api.multi
    def invoice_print_date_time(self):
        user_tz = self.env.user.company_id.tz or "Asia/Dubai"
        display_date_result = datetime.now(pytz.timezone(user_tz))
        return display_date_result.strftime("%d-%m-%Y %I:%M %p")
    
    @api.multi
    @api.onchange('agent_id')
    def _onchange_agent_id(self):
        if self.agent_id:
            self.user_id = self.agent_id.user_id.id
        else:
            self.user_id = False

    @api.onchange('date_invoice')
    def onchange_due_date(self):
        self.date_due = (datetime.strptime(self.date_invoice, '%d-%m-%Y') + datetime.timedelta(30)).date()
    @api.model
    def create(self, vals):
        res = super(ProformaInvoice, self).create(vals)
        code = self.env.user.company_id.code if self.env.user.company_id.code else ""
        res.name = code + self.env['ir.sequence'].next_by_code('crm.proforma.invoice')
        return res

    def get_mail_url(self):
        return self.get_share_url()

    @api.multi
    def action_invoice_sent(self):
        self.ensure_one()
        # template = self.env.ref('asteco_crm.email_template_proforma_invoice')
        template = self.env.user.company_id.email_invoice_template
        if template:
            compose_form = self.env.ref('mail.email_compose_message_wizard_form')
            ctx = dict(
                default_model='crm.proforma.invoice',
                default_res_id=self.id,
                default_use_template=bool(template),
                default_template_id= template.id,
                default_composition_mode='comment',
                force_email=True
            )
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
        else:
            raise ValidationError("Please choose an invoice email template!!!")

    @api.multi
    def proforma_invoice_print(self):
        return self.env.ref('asteco_crm.report_ast_proforma_invoice').report_action(self)

    @api.multi
    def change_state_to_issued(self):
        self.state = 'issued'

    @api.multi
    def change_state_to_received(self):
        self.state = 'received'

    





