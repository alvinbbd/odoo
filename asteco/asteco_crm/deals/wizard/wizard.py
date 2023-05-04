from odoo import models, fields, api

class DealWizard(models.Model):
    _name = "deal.wizard"

    # def_get_deal_wizard(self):
    deal_id = fields.Many2one("deal.deal",string="Deal")
    label = fields.Char("Do you want to unpublish the list?")
    unpublish = fields.Selection([('yes','Yes'),('no','No')])

    def action_done(self):
        if self.unpublish == "yes":
            if len(self.listing_id) > 0:
                self.listing_id.unpublish()

