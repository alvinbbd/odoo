# from odoo import models,api,fields
#
# class PartnerFillPDF(models.AbstractModel):
#     _name = 'report.asteco_crm.partner_fillpdf'
#     _inherit = 'report.report_fillpdf.abstract'
#
#     name = fields.Char()
#     mobile = fields.Char()
#
#     @api.model
#     def get_original_document_path(self, data, objs):
#         return get_resource_path(
#             'report_fillpdf', 'static/src/pdf', 'Mockup_Contact.pdf')
#
#     @api.model
#     def get_document_values(self, data, objs):
#         objs.ensure_one()
#         return {'name': objs.name}
