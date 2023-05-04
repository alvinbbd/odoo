from odoo import http
from odoo.http import request
import json
import re

class ListingMain(http.Controller):

	@http.route(['/listing/preview/<model("listing.listing"):list_id>'], type='http', auth="public", website=True)
	def listing_html_preview(self, list_id, debug=True):
		return http.request.render('asteco_crm.template_listing_preview',{'listing':list_id})

	@http.route(['/preview/listings/<string:ids>'], type='http', auth="public", website=True)
	def listing_html_preview_multi(self, ids, debug=True):
		new_ids = ids[1:-1].split('-')	
		listing_ids = {}
		for item in new_ids:
			listing_ids[item] = request.env['listing.listing'].browse(int(item))
		return http.request.render('asteco_crm.template_listing_preview_multi',{'listing_ids':listing_ids})

	@http.route(['/print/listing/preview/<model("listing.listing"):list_id>'], type='http', auth="public", website=True)
	def print_listing_preview(self, list_id):
		pdf = request.env.ref('asteco_crm.report_list_html_preview').sudo().render_qweb_pdf([list_id.id])[0]
		pdfhttpheaders = [
			('Content-Type', 'application/pdf'),
			('Content-Length', len(pdf)),
		]
		return request.make_response(pdf, headers=pdfhttpheaders)

	@http.route(['/send/enquiry'], type='http', auth="public", website=True, csrf=False)
	def send_enquiry(self, **kw):
		if 'firstname' in kw and 'phone' in kw and 'email' in kw and 'datetimeast' in kw and 'listing' in kw and 'datetimeast' in kw:
			if kw['firstname'] and kw['phone'] and kw['email'] and kw['datetimeast'] and kw['listing'] and kw['datetimeast']:
				# mobile validation
				for char in kw['phone']:
					if char.isalpha():
						values = {'success':'invalid-phone'}
						return json.JSONEncoder().encode(values)	
				if len(kw['phone']) < 7 or len(kw['phone']) > 11:
					values = {'success':'invalid-phone'}
					return json.JSONEncoder().encode(values)
				# email validation
				match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', kw['email'])
				if match == None:
					values = {'success':'invalid-mail'}
					return json.JSONEncoder().encode(values)
				
				enq_id = request.env['listing.enquiry'].search([('email','=',kw['email']),('listing_id','=',int(kw['listing']))])
				if enq_id:
					values= {'success':'lead exist','lead':enq_id.name}
					return json.JSONEncoder().encode(values)
				else:
					comments = ""
					if 'comments' in kw and kw['comments']:
						comments = kw['comments']
					enq_id = request.env['listing.enquiry'].create({
							'contact_name':kw['firstname'],
							'email':kw['email'],
							'mobile':kw['phone'],
							'prefered_date':kw['datetimeast'],
							'comments':comments,
							'listing_id':int(kw['listing']),
						})
					if enq_id:
						values= {'success':'lead','lead':enq_id.name}
					else:
						values= {'success':'no lead'}
					return json.JSONEncoder().encode(values)
			else:
				values= {'success':'0'}
		else:
			values= {'success':'0'}
		return json.JSONEncoder().encode(values)

	@http.route(['/preview/send/html/mail'], type='http', auth="public", website=True, csrf=False)
	def send_html_preview_mail(self, **kw):
		ids = kw['partner_ids'][2:-2]
		if ids:
			ids = ids.split('","')
		mailto = ""
		for data in ids:
			partner = request.env['res.partner'].browse(int(data))
			mailto += partner.email + ","
		if mailto:
			message = "Dear Customer, \nWe are sharing the below listing for your consideration. \n https://odoo.asteco.ae/listing/preview/" + str(kw['listing_id'])
			mail = request.env['mail.mail'].create({
					'subject':"Listing Preview",
					'email_from':"asteco@asteco.com",
					'email_to':mailto,
					'body_html':message,
				})
			mail.send()
			values = {'success':'1'}
		else:
			values = {'success':'0'}
		return json.JSONEncoder().encode(values)

	@http.route(['/listing/send/mail'], type='http', auth="public", website=True, csrf=False)
	def send_listing_mail(self,lead_ids, listing_id):
		listing_id = listing_id.replace(',','')
		new_ids = lead_ids[2:-2].split('","')
		lead_ids = "["
		for item in new_ids:
			lead_ids += str(item)+"-"
		lead_ids = lead_ids[:-1]
		lead_ids += "]"
		lead_ids = lead_ids.replace(',','')
		match_lead_ids = lead_ids[1:-1]
		match_lead_ids = match_lead_ids.split('-')
		if len(lead_ids) > 2:
			listing_id = request.env['atk.lead.lead'].browse(int(listing_id))
			server = str(request.env['res.company'].sudo().search([('id','=',1)]).base_url)
			text = "Dear Customer, We are sharing the below listings for your consideration. \n"
			url = server + "/preview/listings/" + str(listing_id.id) + "?debug "
			mail_text = text + url
			mailto = ''
			for lead_id in match_lead_ids:
				lead = request.env['atk.lead.lead'].browse(int(lead_id))
				mailto += lead.customer_email_id + ','
			mailto = mailto[:-1]
			mail = 'mailto:'+ mailto +'?subject='+ "Matching Listings" +'&body=' + mail_text
			values = {'success':'1', 'mail':mail}
			return json.JSONEncoder().encode(values)
		else:
			values = {'success':'0'}
			return json.JSONEncoder().encode(values)


	@http.route(['/get/live/location'], type='http', auth="public", website=True, csrf=False)
	def get_live_location(self, **kw):
		listing_id = request.env['listing.listing'].browse(int(kw['listing_id']))
		latitude = ''
		longitude = ''
		if listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
			geo_tag = listing_id.unit_geo_tag
			latitude = geo_tag.split(',')[0].strip()
			longitude = geo_tag.split(',')[1].strip()
		if latitude and longitude:
			url = 'https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d15652.203288069075!2d'+longitude+'!3d'+latitude+'!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sin!4v1572586749296!5m2!1sen!2sin'
		else:
			url = 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d924107.6834490718!2d55.275064308777814!3d25.210113411147816!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3e5f428d9fe8c1d1%3A0x5b40a0d5f349ad75!2sAsteco+Property+Management+-+Head+Office!5e0!3m2!1sen!2sin!4v1564225384781!5m2!1sen!2sin'
		values = {'success':url}
		return json.JSONEncoder().encode(values)