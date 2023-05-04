from odoo import models,fields,api
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    action_id = fields.Many2one("action.action")
    action_type = fields.Selection([
        ('reminder', 'Reminder'), ('meeting', 'Meeting'),
        ('viewings', 'Viewings'), ('documentation', 'Documentation'),
        ('open_house', 'Open House'), ('events', 'Events'),
        ('agent_tour', 'Agent Tour'), ('calls', 'Calls')], related='action_id.action_type')

    item = fields.Selection([
        ('listing', 'Listing'), ('lead', 'Lead'),
        ('contacts', 'Contacts'), ('oppertunities', 'Oppertunities'), ('deals', 'Deals')], related='action_id.item')

    agents_ids = fields.Many2many("hr.employee", string="Agents", related='action_id.agents_ids')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
