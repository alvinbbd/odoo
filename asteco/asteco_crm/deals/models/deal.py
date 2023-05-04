from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import Warning,  ValidationError


class DealDeal(models.Model):
    _name = "deal.deal"
    _description = "Deal"
    _inherit = ['mail.thread','mail.activity.mixin']

    @api.multi
    def _get_contact_domain(self):
        sub_broker_id = self.env['contact.classification'].search([('name', '=', 'Sub-broker')])
        contact_ids = []
        if sub_broker_id:
            contact_ids = self.env['res.partner'].search([('contact_classif_ids', 'in', sub_broker_id.ids)]).ids
        return [('id', 'in', contact_ids)]

    name = fields.Char("Reference #", readonly=True, track_visibility="onchange")
    valuation_field_id = fields.Char("Valuation fields")
    lease_renewal_field_id = fields.Char("Lease Renewal fields")
    listing_mobile = fields.Char(" Mobile", related="listing_id.customer_mobile")
    listing_email = fields.Char("Email", related="listing_id.customer_email_id")
    listing_street = fields.Char(string="Street #", track_visibility="onchange")
    listing_floor = fields.Char(string="Floor", related="listing_id.floor", track_visibility="onchange")
    listing_plot_area = fields.Char(string="Plot area", related="listing_id.plot_area")
    listing_regulatory_permit = fields.Char("Regulatory Permit #", related="listing_id.regulatory_permit")
    listing_unit = fields.Char(string="Unit #", related="listing_id.unit", track_visibility="onchange")
    listing_unit_geo_tag = fields.Char(string="Unit Geotag", related="listing_id.unit_geo_tag", track_visibility="onchange")
    listing_listing_detail_type = fields.Char(string="Type", related="listing_id.listing_detail_type", track_visibility="onchange")
    listing_property_view = fields.Char(string="View", related="listing_id.property_view", track_visibility="onchange")
    listing_parking = fields.Char(string="Parking", track_visibility="onchange")
    listing_key_location = fields.Char(string="Key Location", related="listing_id.key_location")
    deal_confidence_level = fields.Char(track_visibility="onchange")
    lead_mobile = fields.Char("Mobile", related="lead_id.customer_mobile")
    lead_email = fields.Char("Email", related="lead_id.customer_email_id")
    # proforma_invoice_narration = fields.Char("Pro-forma Invoice Narration")
    
    is_invoice = fields.Boolean(compute="_check_invoiced")
    split_ext_ref = fields.Boolean("Split with External Referral", track_visibility="onchange")
    split_int_ref = fields.Boolean("Split with Internal/ Network")
    is_notify_agent = fields.Boolean("Notify Agent")
    # is_notify_agent = fields.Boolean("Notify agent")

    date_deal = fields.Date(string="Date current action", default=lambda *a: datetime.now().date())
    estimated_date = fields.Date("Estimated Deal Date", track_visibility="onchange")
    actual_date = fields.Datetime("Actual Deal Date", track_visibility="onchange")
    tenancy_contract_start_date = fields.Date("Tenancy Contract Start Date", track_visibility="onchange")
    tenancy_renewal_date = fields.Date("Tenancy Renewal Date", track_visibility="onchange")
    first_reminder = fields.Date("Reminder 1")
    second_reminder = fields.Date("Reminder 2")
    listing_available = fields.Date(string="Available From", related="listing_id.available_date")
    expected_close_date = fields.Datetime(string="Expected Close Date", track_visibility="onchange")
    # ref = fields.Char("Reference #", readonly=True)
    

    shared_with_id = fields.Many2one("hr.employee", "Shared with", related="lead_id.agent_id", track_visibility="onchange")
    create_uid = fields.Many2one("res.users", string="Created By", required=True, readonly=True, default=lambda self: self.env.user)
    tenent_id = fields.Many2one("res.partner", "Tenant")
    landlord_id = fields.Many2one("res.partner", "Landlord")
    cheque_id = fields.Many2one('number.of.cheque', string="Cheques", track_visibility="onchange")
    agent_performance_id = fields.Many2one("agent.performance")
    external_referral_type = fields.Many2one("res.referral_type", string="External Referral Type")
    deal_sub_broker = fields.Many2one("res.partner", string="Add Sub-broker", domain=_get_contact_domain)
    add_franchisee = fields.Many2one("res.franchisee")
    company_id = fields.Many2one('res.company', string='Company', change_default=True, required=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('deal.deal'))
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    pro_invoice_id = fields.Many2one('crm.proforma.invoice', string="Invoice", track_visibility="onchange")
    temp_payment_id = fields.Many2one('crm.temporary.receipt', string="Receipt", track_visibility="onchange")
    listing_id = fields.Many2one("listing.listing", "Listing Ref #")
    listing_agent = fields.Many2one('hr.employee', string="Assigned To", related="listing_id.agent_id")
    listing_customer = fields.Many2one('res.partner', domain=[('is_contact', '=', True)], related="listing_id.customer_id", string="Contact")
    listing_category = fields.Many2one("listing.category", string="Category",related="listing_id.category_id")
    listing_emirate_id = fields.Many2one("res.country.state", string="Emirate/City", related="listing_id.emirate_id")
    listing_location_id = fields.Many2one('res.location', string="Location/ Project", related="listing_id.location_id")
    listing_sub_location_id = fields.Many2one('res.sub.location', string="Sub-Location/ Building", related="listing_id.sub_location_id")# cheque_id = fields.Many2one("res.cheque", "Cheques")
    listing_category_id = fields.Many2one('listing.category', string="Category", related="listing_id.category_id")
    listing_bed = fields.Many2one('listing.bed', string="Bed", related="listing_id.bed_id")
    listing_bath = fields.Many2one('listing.bath', string="Bath", related="listing_id.bath_id")
    list_managed_status_id = fields.Many2one('listing.managed.status', string="Managed Status", track_visibility="onchange", related="listing_id.managed_status_id")
    lead_contact = fields.Many2one('res.partner', "Contact", related="lead_id.contact_id")
    document_ids = fields.Many2many('ir.attachment', 'deal_attach_rel', 'deal_id', 'attach_id')
    lead_id = fields.Many2one("atk.lead.lead", "Lead Ref #")
    lead_agent = fields.Many2one("hr.employee", "Assigned to", related="lead_id.agent_id", track_visibility="onchange")
    lead_source_id = fields.Many2one("source.master", "Lead Source", related="lead_id.lead_source_id")
    deal_loss_reason = fields.Many2one('loss.reason', string="Reason for Loss")
    # agent = fields.Many2one("res.agent")
    # currency_code = fields.Many2one('res.currency',string="Currency", related="company_id.currency_id")

    type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')], string="Transaction type", track_visibility="onchange", related="listing_id.listing_type")
    sub_status_id = fields.Selection([('Documentation','Documentation'), ('pending_approval','Pending Approval'), ('Pending Completion','Pending Completion'), ('pending_selection','Pending Selection'), ('pending_signature','Pending Signature'), ('unit_reserved','Unit Reserved'), ('deal_lost','Deal Lost')], "Sub - status", track_visibility="onchange")
    include_commission_vat = fields.Selection([('no', 'Yes'), ('yes', 'No')], "Inclusive of VAT – Yes /No", default='no')
    buyer_type = fields.Selection([('investor', 'Investor'), ('end_user', 'End User')], track_visibility="onchange")
    finance_type = fields.Selection([('cash', 'Cash'), ('mortgage', 'Mortgage')])
    deal_status = fields.Selection([('In Progress', 'In Progress'), ('Invoice Issued', 'Invoice Issued'), ('Deposit Received', 'Deposit Received'), ('Archived','Archived'), ('Lost','Closed')], default="In Progress", track_visibility="onchange")
    listing_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')], string="Listing Type", related="listing_id.listing_type")
    listing_furnished_id = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('semi', 'Semi')], string="Furnished", related="listing_id.furnished_id")
    lead_type = fields.Selection([('land_lord', 'Land Lord'), ('tenant', 'Tenant'),('buyer', 'Buyer'), ('seller', 'Seller'), ('investor', 'Investor'), ('agent', 'Agent')], related="lead_id.lead_type")
    lead_share_scope = fields.Selection([('Internal', 'Internal/Network'), ('External', 'External Sub-broker')], string="Share with", related="lead_id.share_scope")
    # state = fields.Selection([('in_Progress', 'In Progress'),('won', 'Won'),('lost','Lost')], string="Status", default="in_Progress")
  

    deal_price = fields.Float(track_visibility="onchange")
    deposit = fields.Float(track_visibility="onchange")
    total_gross_commision = fields.Float("Total gross commission + Commission VAT",compute='onchange_field')
    total_earned_commission_amount = fields.Float("Total Earned Commission - ", compute="_compute_total_earned_commission", store=True)
    commission_vat_amt = fields.Float(compute="_compute_percentage", string="Commission VAT amount")
    listing_price = fields.Float("Price", related="listing_id.price")
    listing_build_up_area_sqf = fields.Integer(string="Build up area(Sqft)", related="listing_id.build_up_area_sqf", track_visibility="onchange")
    listing_build_up_area_sqm = fields.Integer(string="Build up area(Sqm)", related="listing_id.build_up_area_sqm", track_visibility="onchange")
    total_company_earnings = fields.Float("Total Company Earnings - ", compute="_compute_total_company_earnings")
    
    gross_commission = fields.Float()
    external_referral_commision = fields.Integer()
    external_referral_commision_value = fields.Integer(compute='_compute_by_percentage')
    
    create_action = fields.One2many("action.action", "action_id", string="Action")
    notes_ids = fields.One2many('crm.notes', 'deal_id', string="Note History")
    deal_split_internal = fields.One2many("deal.split.internal", "deal_id", string="Split with Internal")
    deal_split_network = fields.One2many("deal.split.network", "deal_id", string="Split with Network")
    mail_msg_ids = fields.One2many('mail.message','deal_id')

    @api.constrains('deal_confidence_level')
    def _check_deal_confidence_level(self):
        for record in self:
            if record.deal_confidence_level == "0":
                raise ValidationError("Please enter a valid deal confidence level!!!")


    @api.constrains('deal_price')
    def _check_commission_value(self):
        for record in self:
            if record.deal_price <= 0.0:
                raise ValidationError("Please enter a valid deal price!!!")

    @api.constrains('expected_close_date')
    def _check_expected_close_date(self):
        for record in self:
            if record.expected_close_date:
                if datetime.strptime(record.expected_close_date,'%Y-%m-%d %H:%M:%S') < datetime.now():
                    raise Warning("Please enter a valid expected close date !!!")

    @api.constrains('actual_date')                
    def _check_actual_deal_date(self):
        for record in self:
            if record.actual_date:
                if datetime.strptime(record.actual_date,'%Y-%m-%d %H:%M:%S') < datetime.now():
                    raise Warning("Please enter a valid actual deal date !!!")


    @api.multi
    def write(self, vals):
        res = super(DealDeal, self).write(vals)
        if 'gross_commission' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('deal_id','=',self.id)], limit=1)
            if opportunity_id:
                opportunity_id.commission_value = vals['gross_commission']
        if 'actual_date' in vals:
            opportunity_id = self.env['lead.opportunity'].search([('deal_id','=',self.id)], limit=1)
            if opportunity_id:
                opportunity_id.close_date = vals['actual_date']
        if 'sub_status_id' in vals:
            if self.sub_status_id == 'deal_lost':
                self.deal_status = 'Lost'
        return res


    @api.depends('pro_invoice_id')
    def _check_invoiced(self):
        for record in self:
            if record.pro_invoice_id:
                record.is_invoice = True
            else:
                record.is_invoice = False

    def open(self):
        view = self.env.ref('asteco_crm.deal_wizard_form_view')
        return {
            'name': 'Deal Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'deal.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view.id, 'form')],
            'view_id': view.id
        }

    @api.onchange('deal_status')
    def onchange_deal_status(self):
        if self.deal_status == 'won':
            self.open()

    @api.onchange('split_ext_ref')
    def onchange_split_ext_ref(self):
        if not self.split_ext_ref:
            self.external_referral_commision = 0

    @api.depends('gross_commission')
    def _compute_percentage(self):
        self.commission_vat_amt = self.gross_commission * (5 / 100)

    @api.onchange('gross_commission', 'commission_vat_amt', 'include_commission_vat')
    def onchange_field(self):
        if self.gross_commission or self.commission_vat_amt:
            if self.include_commission_vat == 'yes':
                self.total_gross_commision = self.gross_commission + self.commission_vat_amt
            else:
                self.total_gross_commision = self.gross_commission
            self.deal_split_internal._onchange_compute_internal()
            self.deal_split_network._onchange_compute_network()

    @api.depends('gross_commission', 'external_referral_commision_value', 'deal_split_internal', 'deal_split_network')
    def _compute_total_earned_commission(self):
        for record in self:
            internal_commission = 0.0
            external_commission = 0.0
            for interal in record.deal_split_internal:
                internal_commission += interal.commission_value_internal
            for network in record.deal_split_network:
                external_commission += network.commission_value_network
            record.total_earned_commission_amount = record.gross_commission - record.external_referral_commision_value - internal_commission - external_commission

    @api.depends('gross_commission', 'external_referral_commision_value')
    def _compute_total_company_earnings(self):
        for record in self:
            record.total_company_earnings = record.gross_commission - record.external_referral_commision_value

    @api.depends('external_referral_commision', 'gross_commission')
    def _compute_by_percentage(self):
        for record in self:
            record.external_referral_commision_value = record.gross_commission * (
                        record.external_referral_commision / 100)

    @api.model
    def create(self, vals):
        res = super(DealDeal, self).create(vals)
        code = self.env.user.company_id.code if self.env.user.company_id.code else ""
        res.name = code + self.env['ir.sequence'].next_by_code('deal.deal')
        return res

    @api.multi
    def create_proforma_invoice(self):
        proforma_invoice = {'gross_commission':self.gross_commission, 'commission_vat_amt':self.commission_vat_amt,
                'include_commission_vat': self.include_commission_vat, 'id':self.id, 'lead_contact_id':self.lead_contact.id
                }
        self.create_proforma_invoice_impl(proforma_invoice)

    @api.multi
    def create_proforma_invoice_impl(self,vals):
        if vals['gross_commission'] == 0.0:
            raise Warning("Sorry!!! You cannot create a proforma invoice with 'zero' amount!")
        vat = vals['commission_vat_amt'] if vals['include_commission_vat'] == 'yes' else 0.0
        deal_obj = self.env['deal.deal'].browse(vals['id'])
        deal_obj.pro_invoice_id = self.env['crm.proforma.invoice'].create({
            'deal_id': vals['id'],
            'partner_id': vals['lead_contact_id'],
            'date_invoice': datetime.now().date(),
            'date_due': (datetime.now().date() + timedelta(30)),
            'Payment_amount': vals['gross_commission'],
            'vat_amount': vat,
            'state': 'issued',
        })
        deal_obj.deal_status = "Invoice Issued"

    @api.multi
    def create_proforma_invoice_api(self,vals):
        proforma_invoice = {'gross_commission': vals['gross_commission'], 'commission_vat_amt': vals['commission_vat_amt'],
                'include_commission_vat': vals['include_commission_vat'], 'id': vals['deal_id'],
                'lead_contact_id': vals['lead_contact_id']
                }
        self.create_proforma_invoice_impl(proforma_invoice)
        return True

    @api.multi
    def create_temp_receipt(self):
        temp_receipt = {'lead_contact_id':self.lead_contact.id, 'id':self.id, 'pro_invoice_id_id':self.pro_invoice_id.id,
                'pro_invoice_id_agent_id_id': self.pro_invoice_id.agent_id.id,
                'pro_invoice_id_address':self.pro_invoice_id.address}
        self.create_temp_receipt_impl(temp_receipt)

    @api.multi
    def create_temp_receipt_impl(self,vals):
        deal_obj = self.env['deal.deal'].browse(vals['id'])
        deal_obj.temp_payment_id = deal_obj.env['crm.temporary.receipt'].create({
            'partner_id': vals['lead_contact_id'],
            'payment_date': datetime.now().date(),
            'deal_id': vals['id'],
            'pro_invoice_id': vals['pro_invoice_id_id'],
            'agent_id': vals['pro_invoice_id_agent_id_id'],
            'address': vals['pro_invoice_id_address'],
            'state': 'received',
        })
        deal_obj.deal_status = "Deposit Received"

    @api.multi
    def create_temp_receipt_api(self,vals):
        pro_inv_id = vals['pro_invoice_id_id']
        pro_inv_obj = self.env['crm.proforma.invoice'].search([('id', '=', pro_inv_id)])
        temp_receipt = {'lead_contact_id':vals['lead_contact_id'], 'id':vals['id'],
                     'pro_invoice_id_id':pro_inv_id,
                        'pro_invoice_id_agent_id_id': pro_inv_obj.agent_id.id,
                        'pro_invoice_id_address':pro_inv_obj.address}
        self.create_temp_receipt_impl(temp_receipt)
        return True


    @api.multi
    def view_proforma_invoice(self):
        view = self.env.ref('asteco_crm.proforma_invoice_form_view')
        return {
            'type':'ir.actions.act_window',
            'res_model':'crm.proforma.invoice',
            'res_id':self.pro_invoice_id.id,
            'view_id':view.id,
            'view_mode':'form',
        }

    @api.multi
    def view_temp_receipt(self):
        view = self.env.ref('asteco_crm.temporary_receipt_form_view')
        return {
            'type':'ir.actions.act_window',
            'res_model':'crm.temporary.receipt',
            'res_id':self.temp_payment_id.id,
            'view_id':view.id,
            'view_mode':'form',
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


class DealSplitInternal(models.Model):
    _name = 'deal.split.internal'

    @api.multi
    def _internal_current_company(self):
        return [('company_id', '=', self.env.user.company_id.id)]

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company'])
    agent = fields.Many2one("hr.employee")
    parent_agent = fields.Many2one("hr.employee")
    deal_id = fields.Many2one("deal.deal")
    commission_internal = fields.Float(string="Commission (%)")
    commission_value_internal = fields.Integer(compute='_onchange_compute_internal')
    agent_temp = fields.Many2one("hr.employee", "Assigned to", related="deal_id.lead_agent", store=False)
    company_id = fields.Many2one('res.company', string='Company', change_default=True, required=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('deal.split.internal'))

    @api.onchange('commission_internal')
    def _onchange_compute_internal(self):
        for record in self:
            record.commission_value_internal = 0
        for record in self:
            record.commission_value_internal = 0
            record.commission_value_internal = record.deal_id.total_earned_commission_amount * (
                        record.commission_internal / 100)


class DealSplitNetwork(models.Model):
    _name = 'deal.split.network'

    @api.multi
    def _network_current_company(self):
        return [('company_id', '!=', self.env.user.company_id.id)]

    agent = fields.Many2one("hr.employee", domain=_network_current_company)
    deal_id = fields.Many2one("deal.deal")
    commission_network = fields.Float(string="Commission (%)")
    commission_value_network = fields.Integer()
    agent_temp = fields.Many2one("hr.employee", "Assigned to", related="deal_id.lead_agent", store="False")

    @api.onchange('commission_network')
    def _onchange_compute_network(self):
        for record in self:
            record.commission_value_network = 0
        for record in self:
            record.commission_value_network = record.deal_id.total_earned_commission_amount * (
                        record.commission_network / 100)


class ListingBed(models.Model):
    _name = 'listing.bed'

    name = fields.Char(string="Name")


class ListingBath(models.Model):
    _name = 'listing.bath'

    name = fields.Char(string="Name")


class DealTransaction(models.Model):
    _name = "deal.transaction"

    name = fields.Char("Name", required=True)


class DealAddAgent(models.Model):
    _name = "res.add_agent"

    name = fields.Char("Name")


class DealAgent(models.Model):
    _name = "res.agent"

    name = fields.Char("Name")


class DealSubBroker(models.Model):
    _name = "res.sub_broker"

    name = fields.Char("Name")


class CrmNotes(models.Model):
    _inherit = "crm.notes"

    deal_id = fields.Many2one('deal.deal', string="Deals")


class ResReferral(models.Model):
    _name = 'res.referral_type'

    name = fields.Char("Name")


class ResFranchisee(models.Model):
    _name = 'res.franchisee'

    name = fields.Char("Name")
