from odoo import models, fields, api


class MailHistory(models.Model):
	_inherit = 'mail.mail'

	# @api.model
	# def create(self,vals):
	# 	res=super(MailHistory,self).create(vals)
	# 	for contact in res.recipient_ids:
	# 		msg = "From : " + str(res.email_from) +"<br />Content :" + str(res.body_html)
	# 		contact.create_mail_msg(msg)

	# 	return res

	@api.model
	def create(self, vals):
		res = super(MailHistory, self).create(vals)
		if res.author_id.company_id.out_mail_server_id:
			res.mail_server_id = res.author_id.company_id.out_mail_server_id.id
		return res