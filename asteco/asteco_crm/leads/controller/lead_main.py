from odoo import http
from odoo.http import request
import json
import werkzeug
from datetime import  datetime, timedelta
import requests



class LeadMain(http.Controller):

	@http.route(['/match/listing'], type='http', auth="public", website=True , csrf=False)
	def match_listing(self,list_ids, lead_id):
		lead_id = lead_id.replace(',','')
		list_ids = list_ids.replace(',','')
		lists = json.loads(list_ids)
		if len(lists) > 1:
			msg = "You cannot add multiple listings at a time!"
			request.env.user.raise_warning(msg)
		lead_id = request.env['atk.lead.lead'].browse(int(lead_id))
		listing_id = request.env['listing.listing'].browse(int(lists[0]))
		if not request.env['lead.offered.unit'].search([('lead_id','=',lead_id.id),('listing_id','=',listing_id.id)]):
			data = listing_id.sudo().read(['location_id', 'category_id'])
			offered_unit_id = request.env['lead.offered.unit'].sudo().create({
					'lead_id':lead_id.id,
					'listing_id':listing_id.id,
					'status':'Pending',
				})
			values= {'success':'1'}
		return json.JSONEncoder().encode(values)

	@http.route(['/lead/send/mail'], type='http', auth="public", website=True , csrf=False)
	def lead_send_mail(self,list_ids, lead_id):
		lead_id = lead_id.replace(',','')
		new_ids = list_ids[2:-2].split('","')
		listing_ids = "["
		for item in new_ids:
			listing_ids += str(item)+"-"
		listing_ids = listing_ids[:-1]
		listing_ids += "]"
		listing_ids = listing_ids.replace(',','')
		if len(listing_ids) > 2:
			lead_id = request.env['atk.lead.lead'].browse(int(lead_id))
			if lead_id.customer_email_id:
				mail_recipients = lead_id.customer_email_id
				template = request.env.ref('asteco_crm.email_template_selected_listing', False)
				values = template.sudo().generate_email(lead_id.id)
				values['email_from']= lead_id.company_id.email
				values['email_to'] = mail_recipients
				values['body_html'] = values['body_html'].replace("_list_",listing_ids)
				send_mail = request.env['mail.mail'].sudo().create(values)
				send_mail.send()
			values = {'success':'1'}
			return json.JSONEncoder().encode(values)
		else:
			values = {'success':'0'}
			return json.JSONEncoder().encode(values)

	@http.route(['/send/offered/mail'], type='http', auth="public", website=True , csrf=False)
	def send_offered_mail(self,offered_unit_ids, lead_id):
		lead_id = lead_id.replace(',','')
		new_ids = offered_unit_ids[2:-2].split('","')
		offered_unit_ids = "["
		for item in new_ids:
			offered_unit_ids += str(item)+"-"
		offered_unit_ids = offered_unit_ids[:-1]
		offered_unit_ids += "]"
		offered_unit_ids = offered_unit_ids.replace(',','')
		offered_unit_ids = offered_unit_ids[1:-1]
		offered_unit_ids = offered_unit_ids.split('-')
		listing_ids = []
		if len(str(offered_unit_ids)) > 4:
			for item in offered_unit_ids:
				listing_ids.append(request.env['lead.offered.unit'].browse(int(item)).listing_id.id)
			listing_ids = str(listing_ids)
			listing_ids = listing_ids.replace(',','-')
		lead_id = request.env['atk.lead.lead'].browse(int(lead_id))
		if lead_id.customer_email_id and listing_ids:
			mail_recipients = lead_id.customer_email_id
			template = request.env.ref('asteco_crm.offered_listing_preview_mail', False)
			values = template.sudo().generate_email(lead_id.id)
			values['email_from']= lead_id.company_id.email
			values['email_to'] = mail_recipients
			values['body_html'] = values['body_html'].replace("_list_",listing_ids)
			send_mail = request.env['mail.mail'].sudo().create(values)
			send_mail.send()
			values = {'success':'1'}
			return json.JSONEncoder().encode(values)
		else:
			values = {'success':'0'}
			return json.JSONEncoder().encode(values)

	@http.route(['/lead/send/whatsapp'], type='http', auth="public", website=True , csrf=False)
	def lead_send_whatsapp(self,list_ids, lead_id):

		new_ids = list_ids[2:-2].split('","')
		listing_ids = "["
		for item in new_ids:
			listing_ids += str(item)+"-"
		listing_ids = listing_ids[:-1]
		listing_ids += "]"
		lead_id = lead_id.replace(',','')
		listing_ids = listing_ids.replace(',','')
		if len(listing_ids) > 2:
			lead_id = request.env['atk.lead.lead'].browse(int(lead_id))

			server = " https://odoo.asteco.ae/"
			mobile = " at Mobile : " + str(lead_id.agent_id.user_id.phone_office) + " or " if lead_id.agent_id.user_id.phone_office else ""
			email = " at Email : " + str(lead_id.agent_id.user_id.email) if lead_id.agent_id.user_id.email else ""
			prefix = "Hai " + str(lead_id.contact_id.name) + ", Please open the below link to view some matching listings for your lead(" + str(lead_id.name) + ")."
			suffix = " Kindly review and revert. For further information, feel free to contact " + str(lead_id.agent_id.name) + mobile + email + " Thank you."

			url = server + "preview/listings/" + listing_ids + "?debug " + suffix
			text = "Dear Customer, We are sharing the below listings for your consideration. \n" + server + "preview/listings/" + listing_ids + "?debug "
			whatsapp_url = "https://api.whatsapp.com/send?phone=" +str(lead_id.isd_code_id.country_code)+str(lead_id.customer_mobile) + "&text=" + text
			values = {'success':'1', 'whatsapp_url':whatsapp_url}
			return json.JSONEncoder().encode(values)
		else:
			values = {'success':'0'}
			return json.JSONEncoder().encode(values)

	@http.route(['/lead/send/sms'], type='http', auth="public", website=True , csrf=False)
	def lead_send_sms(self,list_ids, lead_id, ):
		new_ids = list_ids[2:-2].split('","')
		listing_ids = "["
		for item in new_ids:
			listing_ids += str(item)+"-"
		listing_ids = listing_ids[:-1]
		listing_ids += "]"
		lead_id = lead_id.replace(',','')
		listing_ids = listing_ids.replace(',','')
		lead_id = request.env['atk.lead.lead'].browse(int(lead_id))
		mobile = lead_id.isd_code_id.country_code + lead_id.customer_mobile
		if len(listing_ids)>2 and lead_id.name and mobile and lead_id.agent_id:
			server = " https://odoo.asteco.ae/"
			msg = "Dear Customer, We are sharing the below listings for your consideration. \n" + server + "preview/listings/" + listing_ids + "?debug "
			URL = "http://ae.infosatme.com/sms/smsapi?api_key=C20025715d77dfa65e7bc4.16782074%20&type=text&contacts=" + mobile + "&senderid=ASTECO&msg=" + msg + "&scheduledDateTime=" + str(datetime.now())
			r = requests.get(URL)
			values = {'success':'1'}
			return json.JSONEncoder().encode(values)
		else:
			values = {'success':'0'}
			return json.JSONEncoder().encode(values)


	