from odoo import fields, models, api

class IrAttachments(models.Model):
    _inherit = 'ir.attachment'

    listing_id = fields.Many2one('listing.listing')
    contact_id = fields.Many2one('res.partner')
    lead_id = fields.Many2one('atk.lead.lead')
    deal_id = fields.Many2one('deal.deal')