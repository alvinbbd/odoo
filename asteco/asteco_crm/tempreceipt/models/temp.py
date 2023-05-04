from odoo import fields, models, api, _
import datetime

class ReceiptTemporary(models.Model):
    _name = "crm.temporary.receipt"
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']
    _description = "Temporary Receipt"

    @api.depends('payment_amount','vat_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.payment_amount + record.vat_amount

    name = fields.Char()
    deal_id = fields.Many2one("deal.deal", string='Deal Ref #',track_visibility="onchange")
    partner_id = fields.Many2one('res.partner', "Customer",track_visibility="always")
    pro_invoice_id = fields.Many2one("crm.proforma.invoice", string='Invoice',track_visibility="onchange")
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Received'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    agent_id = fields.Many2one("hr.employee", "Agent",track_visibility="onchange")
    mobile = fields.Char(string="Mobile", related="partner_id.mobile",track_visibility="onchange")
    email = fields.Char(string="Email", related="partner_id.email",track_visibility="onchange")
    address = fields.Text(string="Address")
    payment_date = fields.Date("Payment Date", default=lambda self:datetime.datetime.now().date(),track_visibility="onchange")
    payment_type = fields.Selection([('cash','Cash'),('cheque','Cheque')], "Payment Method",track_visibility="onchange")
    payment_amount = fields.Float(string="Payment Amount",track_visibility="onchange", related="pro_invoice_id.Payment_amount")
    vat_amount = fields.Float(string="VAT Amount",track_visibility="onchange", related="pro_invoice_id.vat_amount")
    net_amount = fields.Float(string="Net Payment Amount",track_visibility="onchange", compute=_compute_net_amount)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'), ],
        string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('deal.deal'))
    currency_id = fields.Many2one('res.currency', related="partner_id.currency_id")

    @api.multi
    def receipt_print(self):
        return self.env.ref('asteco_crm.report_ast_temp_receipt').report_action(self)

    def get_mail_url(self):
        return self.get_share_url()

    @api.multi
    def send_mail(self):
        self.ensure_one()
        template = self.env.ref('asteco_crm.email_template_temporary_receipt', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='crm.proforma.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="asteco_crm.mail_template_data_notification_email_temporary_receipt",
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

    @api.onchange('pro_invoice_id')
    def onchange_pro_invoice_id(self):
        self.partner_id = self.pro_invoice_id.partner_id.id
        self.deal_id = self.pro_invoice_id.deal_id.id
        self.agent_id = self.pro_invoice_id.agent_id.id
        self.address = self.pro_invoice_id.address
        self.invoice_ids = self.pro_invoice_id

    @api.model
    def create(self, vals):
        res = super(ReceiptTemporary, self).create(vals)
        code = self.env.user.company_id.code if self.env.user.company_id.code else ""
        res.name = code + self.env['ir.sequence'].next_by_code('crm.temporary.receipt')
        return res

    @api.multi
    def write(self, vals):
        if 'pro_invoice_id' in vals:
            self.invoice_ids = self.pro_invoice_id
        return super(ReceiptTemporary, self).write(vals)

    @api.multi
    def change_state_to_received(self):
        self.state = 'received'
        self.pro_invoice_id.state = 'received'

    @api.multi
    def invoice_print_date_time(self):
        return self.pro_invoice_id.invoice_print_date_time()
