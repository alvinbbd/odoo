from odoo import models, fields, api
from odoo import SUPERUSER_ID

class KsToggleBoolean(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Inherited res.config.settings to display the toggle switch on the general setting'
    ks_togg_ctrl = fields.Boolean(config_parameter='base_setup.ks_togg_ctrl')
    ks_togg_type = fields.Selection([('Rounded', 'Rounded'), ('Rectangular', 'Rectangular')],
                                    default='Rounded',
                                    required=True,
                                    config_parameter='base_setup.ks_togg_type')


    def get_values(self):
        res = super(KsToggleBoolean, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            ks_togg_ctrl = params.get_param('base_setup.ks_togg_ctrl'),
            ks_togg_type = params.get_param('base_setup.ks_togg_type')
        )
        return res

    def set_values(self):
        super(KsToggleBoolean, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('base_setup.ks_togg_ctrl',self.ks_togg_ctrl)
        params.set_param('base_setup.ks_togg_type',self.ks_togg_type)


class KsSaveUser(models.Model):
    # Inherited res.users to store toggle background color value.
    _inherit = 'res.users'
    ks_togg_color = fields.Char()

    # Get the color value from res.users
    @api.model
    def ks_get_toggle_color(self, user_id):
        res_usrs_color = self.env['res.groups'].search([('id', '=', self.env.ref('base.group_erp_manager').id)]).users.search([('ks_togg_color',"!=",False)],limit=1,order='write_date desc').ks_togg_color
        ks_color = res_usrs_color
        if ks_color is False:
            ks_color = "#68c156"

        return ks_color


class KsHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # Set toggle value to the session.
    def session_info(self):
        rec = super(KsHttp, self).session_info()
        rec['ks_toggle_status'] = self.env['ir.config_parameter'].sudo().get_param('base_setup.ks_togg_ctrl')
        rec['ks_toggle_type'] = self.env['ir.config_parameter'].sudo().get_param('base_setup.ks_togg_type')
        return rec
