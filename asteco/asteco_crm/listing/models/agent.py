from odoo import fields, models, api

class Agents(models.Model):
    _name = 'agent.agent'

    name = fields.Char(string='Name')
    listing_id = fields.Many2one('listing.listing',string="Listing ID")