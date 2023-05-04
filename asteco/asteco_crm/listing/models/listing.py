from odoo import fields, models, api, _, tools
from datetime import datetime
from datetime import timedelta
import re
from odoo.exceptions import ValidationError, Warning
from PIL import *
from odoo.tools import html2plaintext, pycompat
from bs4 import BeautifulSoup
# from googlemaps import GoogleMaps
from geopy.geocoders import Nominatim



class Listing(models.Model):
    _name = 'listing.listing'
    _inherit = ['portal.mixin', 'mail.thread','mail.activity.mixin']
    _description = "Listing"

    def _default_country(self):
        return self.env.user.company_id.country_id.id

    def _get_default_listing_region(self):
        country_uae = self.env['res.country'].search([('name','=','United Arab Emirates')])
        if country_uae:
            if country_uae == self.env.user.company_id.country_id:
                return 'Local'
            else:
                return 'International'

    @api.multi
    def _get_contact_domain(self):
        sub_broker_id = self.env['contact.classification'].search([('name','=','Sub-broker')])
        contact_ids = []
        if sub_broker_id:
            contact_ids = self.env['res.partner'].search([('contact_classif_ids','in',sub_broker_id.ids)]).ids
        return [('id', 'in', contact_ids)]

    @api.multi
    def get_user_id(self):
        if self.env.user.employee_ids:
            return self.env.user.employee_ids.id
        else:
            return False

    def _get_agent_domain(self):
        emp_ids = self.env['hr.employee'].search([('company_id','=',self.env.user.company_id.id)])
        return [('id','in',emp_ids.ids)]

    # to set default portal as ownsite for jordan
    def _get_default_portals(self):
        if self.env.user.company_id.name == 'Asteco Jordan':
            portal = self.env['crm.portal'].search([('company_id','=',self.env.user.company_id.id),('name','=','Ownsite')])
            if portal:
                return portal



    available_date = fields.Date(string="Available From", track_visibility="onchange")
    rented_until_date = fields.Date(string="Rented Until", track_visibility="onchange")
    remind_date = fields.Date(string="Remind", track_visibility="onchange")

    # ref = fields.Char(string="Reference #")
    ref_name = fields.Char(string="Reference #", track_visibility="onchange") # To Replace ref with this name field
    permit_number = fields.Char(string="Permit #")
    unit = fields.Char(string="Unit #", track_visibility="onchange")
    listing_detail_type = fields.Char(string="Type", track_visibility="onchange")
    street = fields.Char(string="Street #", track_visibility="onchange")
    floor = fields.Char(string="Floor", track_visibility="onchange")
    plot_area = fields.Char(string="Plot area", track_visibility="onchange")
    property_view = fields.Char(string="View", track_visibility="onchange")
    name = fields.Char(string="Title", track_visibility="onchange")
    consumer_number = fields.Char(string="Consumer #", track_visibility="onchange")
    str = fields.Char(string="STR #", track_visibility="onchange")
    key_location = fields.Char(string="Key Location", track_visibility="onchange")
    rented_at = fields.Char(string="Rented at")
    remind = fields.Char(string="Remind")
    customer_mobile = fields.Char(related="customer_id.mobile", string="Mobile", track_visibility="onchange")
    customer_email_id = fields.Char(related="customer_id.email", string="Email Id", track_visibility="onchange")
    regulatory_permit = fields.Char("Regulatory Permit #", track_visibility="onchange")
    unit_geo_tag = fields.Char(string="Unit Geotag", track_visibility="onchange")
    # country_code = fields.Char(string="Country Code", default="UAE")

    sms = fields.Text(string="Send SMS")
    description = fields.Html(string="Description", takefocus=0, track_visibility="onchange")
    html_code = fields.Text('HTML Code')

    isd_code_id = fields.Many2one("res.country.code", "IDD", track_visibility="onchange")

    build_up_area_sqm = fields.Integer(string="Build up area(Sqm)", track_visibility="onchange")
    build_up_area_sqf = fields.Integer(string="Build up area(Sqft)", track_visibility="onchange")

    build_up_area_sqm_int = fields.Integer(string="Build up area(Sqm)", track_visibility="onchange")
    build_up_area_sqf_int = fields.Integer(string="Build up area(Sqft)", track_visibility="onchange")
    

    price = fields.Float(string="Price", track_visibility="onchange")
    price_per_sqft = fields.Float(string="Price/Sq.ft.", track_visibility="onchange")
    commission_perc = fields.Float(string="%")
    commission_amount = fields.Float(string="Commission(%)", track_visibility="onchange")
    deposit_perc = fields.Float(string="%")
    deposit_amount = fields.Float(string="Deposit", track_visibility="onchange")
    maintenance_fee = fields.Float(string="Maintenance Fee", track_visibility="onchange")
    listing_quality = fields.Float(string="Listing Quality")

    listing_type = fields.Selection([('Rental', 'Rental'), ('Sale', 'Sale')], string="Listing Type", default='Rental')
    listing_status = fields.Selection(
        [('Draft', 'Draft'), ('Requested to Publish', 'Requested to Publish'), ('Published', 'Published'), ('Unpublished', 'Unpublished'), ('Archive', 'Archive')],
        string="Published", default='Draft', track_visibility="onchange")
    listing_region = fields.Selection([('Local', 'Local'), ('International', 'International')], string="Listing Region",
                                      default=_get_default_listing_region, track_visibility="onchange")
    share_scope = fields.Selection([('Internal','Internal/Network'), ('External_Sub_broker','External Sub-broker')], track_visibility="onchange", default="Internal")

    is_featured = fields.Boolean(string="Featured", track_visibility="onchange")
    is_property_tenanted = fields.Boolean(string="Property Tenanted", track_visibility="onchange")
    furnished_id = fields.Selection([('yes','Yes'),('no','No'),('semi','Semi')],string="Furnished", track_visibility="onchange")
    parking = fields.Boolean(string="Parking", track_visibility="onchange")
    is_notify_agent = fields.Boolean("Notify agent")
    is_office = fields.Boolean()
    is_matching_leads = fields.Boolean()

    photo = fields.Binary(string='Photo')

    # Many2one
    customer_id = fields.Many2one('res.partner', "Contact", domain=[('is_contact', '=', True)], track_visibility="onchange")
    agent_id = fields.Many2one('hr.employee', string="Assigned To",default=get_user_id, track_visibility="onchange", domain=_get_agent_domain)
    # agent_id = fields.Many2one('hr.employee', string="Assigned To",default=lambda self: self.env.user.employee_ids.id)
    visibility_id = fields.Many2one('listing.visibility', string="Visibility", track_visibility="onchange", default=lambda  self:self.env["listing.visibility"].search([('name','=','Within Company')]))
    completion_status_id = fields.Many2one('listing.completion.status', string="Completion Status")
    tenure_id = fields.Many2one('listing.tenure', string="Tenure")
    category_id = fields.Many2one("listing.category", string="Category", track_visibility="onchange")
    bed_id = fields.Many2one('listing.bed', string="Bed", track_visibility="onchange")
    fitted_id = fields.Many2one('listing.fitted', string="Fitted")
    bath_id = fields.Many2one('listing.bath', string="Bath", track_visibility="onchange")
    # emirate_id = fields.Many2one("res.emirate", string="Emirate/ City")
    emirate_id = fields.Many2one("res.country.state", string='Emirate/City', domain=(), track_visibility="onchange")
    country_id = fields.Many2one("res.country", string="Country", default=_default_country)
    location_id = fields.Many2one("res.location", string="Location/ Project", track_visibility="onchange")
    sub_location_id = fields.Many2one("res.sub.location", string="Sub-Location/ Building", domain=(), track_visibility="onchange")
    price_frequency_id = fields.Many2one('listing.price.frequency',default=lambda  self:self.env["listing.price.frequency"].
                                         search([('name','=','Per Year')]), string="Price/ Frequency", track_visibility="onchange")
    no_of_cheques = fields.Many2one('number.of.cheque', string="Cheques", track_visibility="onchange")
    property_status_id = fields.Many2one('listing.property.status', string="Property Status",default=lambda  self:self.env["listing.property.status"].
                                         search([('name','=','Available')]), track_visibility="onchange")
    listing_source_id = fields.Many2one('source.master', string="Source of Listing", track_visibility="onchange")
    microsite_url = fields.Char(string="Microsite field URL", track_visibility="onchange")
    managed_status_id = fields.Many2one('listing.managed.status', string="Managed Status", track_visibility="onchange")
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('listing.listing'))

    notes = fields.Text("Note", store=False)

    # One2many
    # photo_ids = fields.One2many('ir.attachment', 'listing_id', string="Photos")
    neighborhood_ids = fields.One2many('listing.neighborhood', 'listing_id', string="Neighbourhood info", track_visibility="onchange" )
    note_ids = fields.One2many('crm.notes', 'listing_id', string="Note History")
    create_action = fields.One2many("action.action", "listing_id", string="Action")
    floor_plan_ids = fields.One2many('floor.plan','listing_id_floor',string="Floor plans", track_visibility="onchange")
    other_media = fields.One2many('media.media','listing_id_media',string="Other media", track_visibility="onchange")

    # Many2many
    # agent_ids = fields.Many2many('res.users', 'shared_agent_users_rel', 'listing_id', 'user_id', string="Shared with")
    agent_ids = fields.Many2many('hr.employee', string="Agents", track_visibility="onchange")
    contact_ids = fields.Many2many('res.partner', string="Contacts", domain=_get_contact_domain)
    portal_ids = fields.Many2many('crm.portal', 'crm_portal_listing_rel', 'portal_id', 'listing_id', string="Portals", domain=[('status','=',True)], track_visibility="onchange", default=_get_default_portals)
    feature_ids = fields.Many2many('listing.features', 'features_listing_rel', 'listing_id', 'feature_id',
                                   string="Features", track_visibility="onchange")
    matching_leads = fields.Many2many('atk.lead.lead')
    document_ids = fields.Many2many('ir.attachment', 'listing_attach_rel', 'listing_id', 'attach_id', string="Generate Documents")
    
    overall_quality = fields.Integer(string="Overall Quality", compute='_compute_percentage')
    media_quality = fields.Integer(string="Media", compute='_compute_listing_quality')
    address_quality = fields.Integer(string="Address", compute='_compute_listing_quality')
    description_quality = fields.Integer(string="Title & Description", compute='_compute_listing_quality')
    price_quality = fields.Integer(string="Price", compute='_compute_listing_quality')
    neighborhood_quality = fields.Integer(string="Neighbourhood", compute='_compute_listing_quality')
    facilities_quality = fields.Integer(string="Facilities", compute='_compute_listing_quality')

    # marketing
    email_recipients = fields.Many2many('res.partner', string="Email To", store=True)

    approval_required = fields.Boolean(string="Approval Required to Publish")
    list_write_date = fields.Datetime(string="Last Updated Date & Time")
    list_write_uid = fields.Many2one('res.users')

    active = fields.Boolean(default=True, track_visibility="onchange")
    mail_msg_ids = fields.One2many('mail.message','listing_id', domain=[('message_type','=','contact')])

    is_user_company = fields.Boolean(store=False, compute='check_user_company')

    is_portal_pull = fields.Boolean(default=False)

    count_of_other_media = fields.Char(compute='_compute_other_media')
    count_of_floor_plan = fields.Char(compute='_compute_floor_plan')

    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")

    def check_user_company(self):
        for record in self:
            if record.company_id.id in self.env.user.company_ids.ids:
                record.is_user_company = True
            else:
                record.is_user_company = False

    @api.depends('agent_id')
    def _get_val(self):
        for record in self:
            # if record.agent_id:
            #     if record.agent_id.user_id.approval_required == 'no':
            #         record.approval_required_or_not = False
            #         # print("_user_type___",self.env.user.user_type.name)
            #     else:
            #         if self.env.user.employee_ids != self.agent_id:
            #             print("___",self.env.user.approval_required)
            #             if self.env.user.approval_required == 'yes':
            #                 record.approval_required_or_not = True

            if record.agent_id:                
                if self.env.user.user_type.name == 'Agent Broker':
                    if self.env.user.employee_ids == self.agent_id:
                        if record.listing_status == 'Published' or record.listing_status == 'Requested to Publish':
                            if record.listing_status == 'Published':
                                #  if the loggined user and assigned agent are same and Agent brocker, and also the listing status is publish then setting to visible unpublish button  
                                record.approval_required_or_not = 'Unpublish'
                            else:
                                record.approval_required_or_not = 'None'
                        else:
                            if self.env.user.approval_required == 'yes':
                                record.approval_required_or_not = 'Request'
                            else:
                                record.approval_required_or_not = 'Publish'
                    else:
                        record.approval_required_or_not = 'None'
                else:
                    if record.listing_status == 'Published':
                        record.approval_required_or_not = 'Unpublish'

                    else:
                        if self.env.user.approval_required == 'no':
                            record.approval_required_or_not = 'Publish'
                        else:
                            if record.listing_status == 'Requested to Publish':
                                record.approval_required_or_not = 'None'
                            else:
                                record.approval_required_or_not = 'Request'




    approval_required_or_not = fields.Selection([('Request','Request'), ('Publish','Publish'), ('Unpublish','Unpublish'), ('None','None')], compute=_get_val)

    def _get_current_user(self):
        for rec in self:
            if rec.agent_id.id in self.env.user.employee_ids.ids:
                rec.current_user = True
            else:
                rec.current_user = False


    current_user = fields.Boolean('Is current user', compute=_get_current_user)

    def _check_description(self, description):
        text = html2plaintext(description).replace(' ','').replace('\n','')
        if len(text)==0:
            raise ValidationError("Please enter a valid description for property!!!")

    @api.onchange('emirate_id')
    def set_values(self):
        if self.emirate_id:
            idl = self.env['res.location'].search([('emirate_id','=',self.emirate_id.id)])
            return {'domain': {'location_id':[('id','in',idl.ids)],}}

    @api.onchange('location_id')
    def set_values_to(self):
        if self.location_id:
            ids = self.env['res.sub.location'].search([('location_id','=',self.location_id.id)])
            return {'domain':{'sub_location_id':[('id','in',ids.ids)],}}

    @api.onchange('country_id')
    def onchange_country(self):
        self.isd_code_id = self.env['res.country.code'].search([('country_id', '=', self.country_id.id)], limit=1).id
        if self.country_id:
            idl = self.env['res.country.state'].search([('country_id','=',self.country_id.id)])
            return {'domain': {'emirate_id':[('id','in',idl.ids)],}}

    @api.onchange('sub_location_id','street','country_id')
    def onchange_sub_location_id(self):
        geolocator = Nominatim()
        try:
            area = ""           
            # if self.street:
            #     area = area + "," + self.street
                # location = geolocator.geocode(area)
                # if not location :
                #     area = area.partition(",")[2]
                #     area = area.partition(",")[2]

            if self.sub_location_id:
                area = area + "," + self.sub_location_id.name
                # location = geolocator.geocode(area)
                # if not location :
                #     area = area.partition(",")[2]
                #     area = area.partition(",")[2]



            # if self.location_id:
            #     area = area + "," + self.location_id.name

            # if self.emirate_id:
            #     area = area + "," + self.emirate_id.name

            if self.country_id:
                area = area + "," + self.country_id.name
                # location = geolocator.geocode(area)
                # if not location:
                #     area = area.partition(",")[2]
                #     area = area.partition(",")[2]
            # if area exists then locating the place by changing the location variable, till finding
            # if area:
            #     area = area.partition(",")[2]
            #     while(1):
            #         location = geolocator.geocode(area)
            #         if location:
            #             self.longitude = location.longitude
            #             self.latitude = location.latitude
            #             self.unit_geo_tag = str(location.latitude) + ", " + str(location.longitude)
            #             break
            #         else:
            #             area = area.partition(",")[2]
            area2 = ""
            if self.street:
                area2 = area
                area = self.street + "," + area
            if area:
                location = geolocator.geocode(area)
                if location:
                    self.unit_geo_tag = str(location.latitude) + ", " + str(location.longitude)
                elif not location and area2:
                    area = area2
                    location = geolocator.geocode(area)
                    if location:
                        self.unit_geo_tag = str(location.latitude) + ", " + str(location.longitude)
        except:
            # self.onchange_sub_location_id()
            pass
        return

# Compute method to calculate the count of images in other_media
    def _compute_other_media(self):
        self.count_of_other_media = len(self.other_media)
        if self.count_of_other_media == '1':
            self.count_of_other_media = "(" + self.count_of_other_media + " Image)" 
        else:
            self.count_of_other_media = "(" + self.count_of_other_media + " Images)"

# Compute method to calculate the count of images in floor_plans_ids
    def _compute_floor_plan(self):
        self.count_of_floor_plan = len(self.floor_plan_ids)
        if self.count_of_floor_plan == '1':
            self.count_of_floor_plan = "(" + self.count_of_floor_plan + " Image)" 
        else:
            self.count_of_floor_plan = "(" + self.count_of_floor_plan + " Images)"        

    # @api.depends('overall_quality')
    def _compute_percentage(self):
        self.overall_quality = (self.media_quality + self.address_quality + self.description_quality + self.price_quality + self.neighborhood_quality + self.facilities_quality) / 6

    def _compute_listing_quality(self):
        media_perc = 0
        address_perc = 0
        descrptn_perc = 0
        price_perc = 0
        neighborhood_perc = 0
        facility_perc = 0


        # media_quality condition

        # if self.floor_plan_ids and len(self.floor_plan_ids) > 0:
        #     media_perc = media_perc + 50
        # if self.other_media and len(self.other_media) > 0:
        #     media_perc = media_perc + 50
        # self.media_quality = media_perc
        if self.other_media and len(self.other_media) > 0:
            for media in self.other_media:
                media_perc = media_perc + 25
            if media_perc > 100:
                media_perc = 100
        self.media_quality = media_perc

        # address_quality condition 
        if self.street and len(self.street) > 0:
            address_perc = address_perc + 50
        if self.location_id and len(self.location_id) > 0:
            address_perc = address_perc + 50
        self.address_quality = address_perc

        # description_quality condition
        if self.name:
            title = self.name.replace(" ", "")
            if len(title) >= 25:
                descrptn_perc = descrptn_perc + 50
        if self.description:
            temp=self.description
            soup = BeautifulSoup(temp)
            temp = soup.get_text().replace(" ","")
            if len(temp) >= 50:
                descrptn_perc = descrptn_perc + 50
        self.description_quality = descrptn_perc

        # price_quality condition
        if self.price > 0:
            price_perc = price_perc + 100
        self.price_quality = price_perc

        # additional_quality condition
        if self.neighborhood_ids and len(self.neighborhood_ids) > 0:
            for neighbor in self.neighborhood_ids:
                neighborhood_perc = neighborhood_perc + 25
            if neighborhood_perc > 100:
                neighborhood_perc = 100
        self.neighborhood_quality = neighborhood_perc

        # facilities_quality condition
        if self.feature_ids:
            for feature in self.feature_ids:
                facility_perc = facility_perc + 25
            if facility_perc > 100:
                facility_perc = 100    

        # if self.neighborhood_ids and len(self.neighborhood_ids) > 0:
        #     facility_perc = facility_perc + 75
        # if self.parking > 0:
        #     facility_perc = facility_perc + 25
        self.facilities_quality = facility_perc


# For map 
    @api.multi
    def open_map(self):
        area = ""
        for listing in self:
            url = "http://maps.google.com/maps?oi=map&q="
            if listing.street:
                url += listing.street.replace(' ', '+')

            if listing.sub_location_id:
                url += listing.sub_location_id.name.replace(' ', '+')
            
            if listing.location_id:
                url += '+'+listing.location_id.name.replace(' ', '+')
            
            if listing.emirate_id:
                url += '+'+listing.emirate_id.name.replace(' ', '+')
            
            if listing.country_id:
                url += '+'+listing.country_id.name.replace(' ', '+')

            # if self.latitude:
            #     url += '+'+self.latitude.replace(' ', '+')
            # if self.longitude:
            #     url += '+'+self.longitude.replace(' ', '+')

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        } 

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        if self.customer_id:
            self.customer_mobile = self.customer_id.mobile
            self.customer_email_id = self.customer_id.email
            self.isd_code_id = self.customer_id.isd_code_id


    @api.multi
    def add_sub_location(self):
        desc = self.description
        if self.sub_location_id:
            desc += str(self.sub_location_id.name) + "<br/>"
        self.description = desc
        return

    @api.multi
    def add_location(self):
        desc = self.description
        if self.location_id:
            desc += str(self.location_id.name) + "<br/>"
        self.description = desc
        return

    @api.multi
    def add_signature(self):
        desc = self.description
        if self.agent_id.user_id.signature:
            desc += str(self.agent_id.user_id.signature) + "<br/>"
        self.description = desc
        return

    @api.multi
    def add_company_profile(self):
        desc = self.description
        if self.agent_id:
            desc += str(self.agent_id.company_id.name) + "<br/>"
        self.description = desc        
        return

    @api.multi
    def name_get(self):
        result = []
        for listing in self:
            name = str(listing.ref_name)
            result.append((listing.id, name))
        return result

    @api.constrains('price', 'price_per_sqft')
    def _check_price(self):
        for record in self:
            if record.price <= 0.0:
                raise ValidationError("Please enter a valid price for property!!!")
            if record.price_per_sqft <= 0.0:
                raise ValidationError("Please enter a valid amount per Sq.ft.!!!")

    @api.constrains('customer_mobile')
    def _check_mobile(self):
        for record in self:
            if len(record.customer_mobile) < 7 or len(record.customer_mobile) > 15:
                raise ValidationError("Please enter a valid mobile number!!!")

    @api.constrains('customer_email_id')
    def validate_mail(self):
        for record in self:
            if record.customer_email_id:
                match = re.match('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-z]{2,4})$', record.customer_email_id)
                if match == None:
                    raise ValidationError('Please enter a valid E-mail ID!!!')

    # To Make BUA Mandatory and Validation for Price
    # @api.constrains('build_up_area_sqm', 'build_up_area_sqf' , 'price')
    # def _check_price(self):
    #     for record in self:
    #         if record.price <= 0.0:
    #             raise ValidationError("Please enter a valid price for property!!!")
    #         if record.build_up_area_sqm <= 0.0:
    #             raise ValidationError("Please enter a valid BUA!!!")
    #         if record.build_up_area_sqf <= 0.0:
    #             raise ValidationError("Please enter a valid BUA.!!!")

    # @api.multi
    # def lead_matching(self):
    #     current_user = self.env.user
    #     for record in self.env['listing.listing'].sudo().search([], limit=10):
    #         record.approval_required = True if current_user.approval_required == 'yes' else False
    #         record.update_matching_leads(current_user)
    #         return


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Listing, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     current_user = self.env.user
    #     for record in self.env['listing.listing'].sudo().search([], limit=10):
    #         record.approval_required = True if current_user.approval_required == 'yes' else False
    #         record.update_matching_leads(current_user)
    #     return res

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

    # @api.multi
    # def add_watermark(self):
    #     photo = Image.open('/opt/odoo/odoo-11.0/Asteco/asteco_crm/static/src/img/image.jpg')
    #     watermark = Image.open('/opt/odoo/odoo-11.0/Asteco/asteco_crm/static/src/img/noImage.jpg').convert("RGBA")
    #     x, y = watermark.size
    #     photo.paste(watermark, (0, 0, x, y), watermark)
    #     # photo.paste(watermark, (25, 25), watermark)
    #     photo.save("ttttttttttttttest.png", format="png")
    #     # pass
    
    @api.onchange('build_up_area_sqm')
    def onchange_buildup_area_sqm(self):
        self.build_up_area_sqf = self.build_up_area_sqm * 10.764

    approval_required
    @api.onchange('build_up_area_sqf')
    def onchange_buildup_area_sqf(self):
        self.build_up_area_sqm = self.build_up_area_sqf / 10.764

    @api.onchange('build_up_area_sqf', 'price')
    def compute_price_per_sqft(self):
        if self.build_up_area_sqf > 0:
            self.price_per_sqft = self.price / self.build_up_area_sqf

    @api.onchange('deposit_perc', 'price')
    def compute_deposit_perc(self):
        if self.deposit_perc > 0:
            self.deposit_amount = self.price * (self.deposit_perc / 100)
        if self.deposit_perc == 0:
            self.deposit_amount = 0.0

    @api.onchange('commission_perc', 'price')
    def compute_commission_perc(self):
        if self.commission_perc > 0:
            self.commission_amount = self.price * (self.commission_perc / 100)
        if self.commission_perc == 0:
            self.commission_amount = 0.0

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id.name in ['Office', 'Retail', 'Warehouse']:
            self.is_office = True
            self.bed_id = False
        else:
            self.is_office = False
            self.fitted_id = False

    @api.onchange('rented_until_date')
    def onchange_rented_until(self):
        if self.rented_until_date:
            remind = datetime.strptime(self.rented_until_date,'%Y-%m-%d') - timedelta(days=90)
            if remind >= datetime.today():
                self.remind_date = remind.date()
            else:
                self.remind_date = False    
        else:
            self.remind_date = False

    @api.model
    def create(self, vals):
        res = super(Listing, self).create(vals)
        if not res.html_code:
            res._check_description(res.description)
        else:
            res.description = res.html_code
            res.html_code = False
        code = self.env['res.company'].search([])
        for c in code:
            if c == res.company_id:
                if res.listing_type == 'Rental':
                    res.ref_name = c.code + self.env['ir.sequence'].next_by_code('listing.listing.rental')
                elif res.listing_type == 'Sale':
                    res.ref_name = c.code + self.env['ir.sequence'].next_by_code('listing.listing.sale')

        # if res.listing_type == 'Rental':
        #     res.ref = self.env['ir.sequence'].next_by_code('listing.listing.rental')
        # elif res.listing_type == 'Sale':
        #     res.ref = self.env['ir.sequence'].next_by_code('listing.listing.sale')
        return res

    

    @api.multi
    def write(self, vals):
        flag = 0
        if len(vals) == 1:
            if 'is_matching_leads' in vals or 'matching_leads' in vals or 'is_portal_pull' in vals:
                flag = 1
        if flag == 0:
            vals['list_write_date'] = datetime.now()
            vals['list_write_uid'] = self.env.user.id
        if 'description' in vals:
            self._check_description(vals['description'])
        return super(Listing, self).write(vals)

    # def add_sub_location(self):
    #     if self.description:
    #         soup = BeautifulSoup(self.description)
    #         if soup.get_text():
    #             print("")
    #         else:
    #             self.description = False
    def full_screen(self):
        res_id = self.id
        view_id = self.env.ref('asteco_crm.full_screen_description_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add property description',
            'res_model': 'listing.listing',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'view_id': view_id,
            'target': 'new',
        }

    def html_code_paste(self):
        view_id = self.env.ref('asteco_crm.html_code_paste_wizard').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Paste HTML Code',
            'res_model': 'listing.listing',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'new',
        }

    def paste_code(self):
        self.description += self.html_code
        self.html_code = False

    def action_listing_quality(self):
        res_id = self.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Listing Quality',
            'res_model': 'listing.listing',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'view_id': self.env.ref('asteco_crm.listing_quality_wizard').id,
            'target': 'new',
        }

    @api.multi
    def open_listing(self):
        view_id = self.env.ref('asteco_crm.listing_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Listing',
            'res_model': 'listing.listing',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': self.id,
        }

    @api.multi
    def update_matching_leads(self):
        self.matching_leads = False
        current_user = self.env.user
        req_list = []
        domain = [('category_id','=',self.category_id.id), ('emirate_id','=',self.emirate_id.id), 
                  ('location_id','=',self.location_id.id)]
        if self.is_office == True:
            domain.append(('fitted_id','=',self.fitted_id.id))
        else:
            domain.append(('bed_id','=',self.bed_id.id))
        if self.listing_type == 'Rental':
            domain.append(('lead_id.lead_type', 'in', ['tenant']))
        elif self.listing_type == 'Sale':
            domain.append(('lead_id.lead_type', 'in', ['buyer', 'investor', 'agent']))
        else:
            return
        requirement_ids = self.env['atk.lead.requirement'].search(domain, limit=5, order="write_date desc")
        for req in requirement_ids:
            if req.lead_id.company_id != self.company_id:
                continue
            if req.lead_id.lead_type =="Rental":
                domain.append(('lead_type', 'in', ['tenant']))
            elif req.lead_id.lead_type =="Sale":
                domain.append(('lead_type', 'in', ['buyer', 'investor', 'agent']))
            if req.max_bua and req.max_price:
                if req.max_bua < self.build_up_area_sqf and req.max_price < self.price:
                    continue
            req_list.append(req.lead_id.id)
            if not current_user.has_group('asteco_crm.group_coordinator'):
                current_emp_id = self.env['hr.employee'].search([('user_id', '=', current_user.id)])
                if req.lead_id.agent_id.id != current_emp_id.id and req.lead_id.agent_id.parent_id.id != current_emp_id.id and req.lead_id.agent_id.parent_id.parent_id.id != current_emp_id.id:
                    req.sudo().lead_id.sudo().accessible_user_ids = [[4, current_user.id]]
        req_list = list(set(req_list))
        if req_list:
            self.matching_leads = req_list
            self.is_matching_leads = True
        else:
            self.matching_leads = False
            self.is_matching_leads = False

    @api.multi
    def action_set_unactive(self):
        self.active = False
        self.listing_status = 'Archive'
        pass

    @api.multi
    def action_set_active(self):
        self.active = True
        pass

    @api.multi
    def send_email(self):
        return

    @api.multi
    def send_whatsapp(self):
        return

    @api.multi
    def send_sms(self):
        return

    @api.multi
    def choose_recipients(self):
        return

    @api.multi
    def block_unit(self):
        pass


    @api.multi
    def convert_2_deal(self):
        pass

    @api.multi
    def price_format(self):
        return "{:,}".format(int(self.price))

    @api.multi
    def round_figure(self, number):
        if number:
            return round(number)

    @api.multi
    def preview(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/listing/preview/%s' % self.id,
            'target': 'new',
        }

    def get_mail_url(self):
        return self.get_share_url()

    @api.multi
    def send_html_mail(self):
        if not self.email_from:
            raise Warning("Please provide from address!")
        if not self.email_recipients:
            raise Warning("Please enter email recipients!")
        email_from = self.email_from
        email_to = self.email_recipients
        subject = self.email_subject if self.email_subject else ""
        message = self.email_message if self.email_message else ""
        message += " https://crm.asteco.com/listing/preview/" + str(self.id)
        mail = self.env['mail.mail'].create({
                'subject':subject,
                'email_from':email_from,
                'email_to':email_to,
                'body_html':message,
            })
        mail.send()

    @api.multi
    def listing_publish(self):
        if self.env.user.employee_ids.id == self.agent_id.id or self.env.user.employee_ids.id == self.agent_id.parent_id.id\
                or self.env.user.employee_ids.id == self.agent_id.parent_id.parent_id.id \
                or self.env.user.user_type.name in ['Director','Co-ordinator','Super User','Super Admin (IT)']:
            if self.property_status_id.name == 'Available':
                if self.agent_id.user_id.approval_required == 'no' or self.env.user.employee_ids == self.agent_id.parent_id or self.env.user.user_type.name in ['Co-ordinator','Super Admin (IT)']:
                    if self.overall_quality >= 50:
                        if self.regulatory_permit:
                            if self.visibility_id.name == 'Network' or self.visibility_id.name == 'Within Company':
                                self.listing_status = 'Published'
                            else:
                                raise ValidationError('Sorry !!! Visiblity should be network or within company to publish the listing')
                        else:
                            raise ValidationError('Sorry !!! Please provide Regulatory Permit #')
                    else:
                        raise ValidationError('Sorry !!! At least you need 50% listing quality to publish the listing')
                else:
                    raise ValidationError('Sorry !!! You are not allowed to publish this listing')
            else:
                raise ValidationError('Sorry !!! Listing Property status should be available to Publish')
        else:
            raise ValidationError('Sorry !!! You are not allowed to publish this listing')
    @api.multi
    def listing_unpublish(self):
        if self.listing_status == 'Published':
            self.listing_status = 'Unpublished'

    @api.multi
    def request_publish(self):
        if self.agent_id.user_id.approval_required == 'yes':
            self.listing_status = 'Requested to Publish'
            if self.agent_id.parent_id:
                new_agent_id = self.agent_id.parent_id
                if self.ref_name:
                    email_to = self.agent_id.parent_id.work_email
                    template = self.env.ref("asteco_crm.email_template_to_parent_on_publising_listing")
                    if template and email_to and self.env.user.company_id.email:
                        values = template.sudo().generate_email(self.id)
                        _msg_ = "The Listing with Ref"+self.ref_name+" has been sent for your approval to publish"
                        _header_ = "Listing for Approval"
                        values['body_html'] = values['body_html'].replace("_msg_", _msg_).replace("_header_",_header_)
                        values['email_to'] = email_to
                        values['email_from'] = self.env.user.company_id.email
                        values['res_id'] = False
                        if not values['email_to'] and not values['email_from']:
                            pass
                        send_mail = self.env['mail.mail'].sudo().create(values)
                        if send_mail:
                            send_mail.send()
                self.sudo().write({'agent_id': new_agent_id.sudo().id})
                return True

    @api.multi
    def send_preview_mail(self):
        self.ensure_one()
        template = self.env.ref('asteco_crm.email_template_listing_preview_send_mail', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        self.email_recipients += self.customer_id
        ctx = dict(
            default_model='listing.listing',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            default_partner_ids=self.email_recipients.ids,
            mark_invoice_as_sent=True,
            custom_layout="asteco_crm.mail_template_listing_preview",
            force_email=True
        )
        self.email_recipients = False
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


class ListingPreview(models.TransientModel):
    _name = 'listing.preview'

    listing_ids = fields.Char()
    company = fields.Many2one('res.company', default=lambda self:self.env.user.company_id.id)
    user = fields.Many2one('res.users', default=lambda self:self.env.user.id)

    @api.multi
    def preview_listing(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        listing_ids = "["
        for listing in active_ids:
            listing_ids += str(listing) + "-"
        listing_ids = listing_ids[:-1]
        listing_ids += "]"
        return {
            'type': 'ir.actions.act_url',
            'url': '/preview/listings/%s' % str(listing_ids),
            'target': 'new',
        }

    @api.multi
    def send_mail(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        listing_ids = "["
        for listing in active_ids:
            listing_ids += str(listing) + "-"
        listing_ids = listing_ids[:-1]
        listing_ids += "]"
        self.listing_ids = str(listing_ids)
        template = self.env.ref('asteco_crm.email_template_listing_preview', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='listing.preview',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id= template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="asteco_crm.mail_template_multi_listing_preview",
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        
class FloorPlan(models.Model):
    _name = 'floor.plan'

    name = fields.Char("Name")
    image = fields.Binary(attachment=True, track_visibility="onchange", string="Image")
    listing_id_floor = fields.Many2one('listing.listing', copy=True)


class MediaMedia(models.Model):
    _name = 'media.media'

    name = fields.Char('Name')
    image = fields.Binary(string="Image", track_visibility="onchange", attachment=True)
    listing_id_media = fields.Many2one('listing.listing', copy=True)

class ListingVisibility(models.Model):
    _name = 'listing.visibility'

    name = fields.Char(sring="Name")


class ListingCompletionStatus(models.Model):
    _name = 'listing.completion.status'

    name = fields.Char(string="Name")


class ListingTenure(models.Model):
    _name = 'listing.tenure'

    name = fields.Char(string="Tenure")


class ListingBed(models.Model):
    _name = 'listing.bed'

    name = fields.Char(string="Name")

class ListingFitted(models.Model):
    _name = 'listing.fitted'

    name = fields.Char(string="Name")

class ListingBath(models.Model):
    _name = 'listing.bath'

    name = fields.Char(string="Name")


class ListingPriceFrequency(models.Model):
    _name = 'listing.price.frequency'

    name = fields.Char(string="Name")


class ListingFeatures(models.Model):
    _name = 'listing.features'
    _order = "name asc"

    name = fields.Char(string="Name")


class ListingPropertyStatus(models.Model):
    _name = 'listing.property.status'

    name = fields.Char(string="Name")


class SourceMaster(models.Model):
    _name = 'source.master'

    name = fields.Char(string="Name")


class ListingNeighborhood(models.Model):
    _name = 'listing.neighborhood'

    neighbor_id = fields.Many2one('res.neighborhood', string="Neighbor", track_visibility="onchange")
    location = fields.Char('Location', track_visibility="onchange")
    name = fields.Char('Name', track_visibility="onchange")
    geotag = fields.Char('Geotag', track_visibility="onchange")
    distance = fields.Float('Distance from property (KM)', track_visibility="onchange")
    listing_id = fields.Many2one('listing.listing', string='Listing')


class ResNeighborhood(models.Model):
    _name = 'res.neighborhood'

    name = fields.Char('Name')


class ResEmirate(models.Model):
    _name = "res.emirate"

    name = fields.Char("Name")


class ResLocation(models.Model):
    _name = "res.location"
    _order = "name asc"

    name = fields.Char("Location")
    emirate_id = fields.Many2one('res.country.state')


class ResSubLocation(models.Model):
    _name = "res.sub.location"
    _order = "name asc"
    name = fields.Char("Name")
    location_id = fields.Many2one('res.location')


class ListingCategory(models.Model):
    _name = "listing.category"

    name = fields.Char("Name")
    property_use_type = fields.Selection([('Commercial','Commercial'), ('Residential','Residential')], string="Property Use Type")


class NumberOfCheque(models.Model):
    _name = "number.of.cheque"

    name = fields.Char("Name")


class ListingManagedStatus(models.Model):
    _name = "listing.managed.status"

    name = fields.Char("Name")


class CrmNotes(models.Model):
    _name = "crm.notes"

    listing_id = fields.Many2one('listing.listing', string="Listing")
    name = fields.Text("Note", track_visibility="onchange")
    is_notify_agent = fields.Boolean("Notify agent")

# class ProductImage(models.Model):
#     _inherit = "product.image"

#     media_listing_id = fields.Many2one('listing.listing')
    # floor_listing_id = fields.Many2one('listing.listing')



