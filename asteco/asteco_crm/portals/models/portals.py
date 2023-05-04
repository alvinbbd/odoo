import base64
import io
from urllib.parse import urlparse
from odoo.exceptions import Warning

import html2text

from odoo import fields, models, api, http
from datetime import datetime
from datetime import timedelta
from odoo.tools import pycompat, os
from dateutil.parser import parse

import logging
_logger = logging.getLogger(__name__)


class Portals(models.Model):
    _name = 'crm.portal'
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']

    name = fields.Char(string="Portal Name", required=True,track_visibility="onchange")
    xml_feedback_link = fields.Char('XML Feedback Link', required=True,track_visibility="onchange")
    ip_restriction = fields.Char('IP Restriction',track_visibility="onchange")

    portal_id = fields.Integer('Portal Id', required=True,track_visibility="onchange")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id,track_visibility="onchange", required=True)

    description = fields.Text(string="Description", required=True,track_visibility="onchange")
    xml_link = fields.Text(string="Xml Link",track_visibility="onchange")

    listing_type = fields.Selection([('Free', 'Free'), ('Paid', 'Paid')], string="Listing Type", default='Free',track_visibility="onchange", required=True)
    pull_type = fields.Selection([('Complete', 'Complete'), ('Differential', 'Differential')], 'Pull Type', default='Complete',
                                 required=True,track_visibility="onchange")
    pull_interval = fields.Integer('Update interval(min)',track_visibility="onchange",default=5)
    last_xml_pull_at = fields.Datetime('Last Pull At', required=True,track_visibility="onchange")
    status = fields.Boolean(string="Status", required=True,track_visibility="onchange")
    xml_definition = fields.Binary('XML Definition Fields', required=True,track_visibility="onchange")
    xml_definition_vals = fields.Binary('XML Definition Values (Optional)', required=False,track_visibility="onchange")
    xml_root_tags = fields.Char('XML Root Tags', required=False,track_visibility="onchange")

    @api.model
    def create(self, vals):
        res = super(Portals, self).create(vals)

        if ',' not in res.xml_root_tags:
            raise warning("Please specify the xml root tags seperated by comma!!!")
        if len(self.search([('portal_id','=',res.portal_id),('company_id','=',res.company_id.id)]).ids) > 1:
            raise Warning("Portal ID already exist for this company!!!")

        if 'xml_definition' in vals:
            self.env['portal.xml.definition'].search([('portal_id', '=', res.portal_id),('company_id','=',res.company_id.id)]).unlink()
            csv_data = base64.b64decode(res.xml_definition)
            csv_iterator = pycompat.csv_reader(
                io.BytesIO(csv_data),
                quotechar='"',
                delimiter=',')
            next(csv_iterator)
            for row in csv_iterator:
                if res.portal_id == int(row[0]):
                    self.env['portal.xml.definition'].create({
                            'portal_id': int(row[0]),
                            'portal_field_name': row[1],
                            'portal_sub_field_name': row[2],
                            'ast_crm_field': row[3],
                            'company_id':res.company_id.id,
                        })
                else:
                    raise Warning('Mismatch in Portal Id !! Please check whether the portal id is same in csv.')
        if 'xml_definition_vals' in vals:
            self.env['portal.xml.definition.values'].search([('portal_id', '=', res.portal_id),('company_id','=',res.company_id.id)]).unlink()
            if vals['xml_definition_vals']:
                csv_data = base64.b64decode(res.xml_definition_vals)
                csv_iterator = pycompat.csv_reader(
                    io.BytesIO(csv_data),
                    quotechar='"',
                    delimiter=',')
                next(csv_iterator)
                for row in csv_iterator:
                    self.env['portal.xml.definition.values'].create({
                            'ast_crm_field': row[0],
                            'ast_crm_field_value': row[1],
                            'portal_field_value': row[2],
                            'portal_id': res.portal_id,
                            'company_id':res.company_id.id,
                        })
        return res

    @api.multi
    def write(self, vals):
        res = super(Portals, self).write(vals)
        if 'xml_root_tags' in vals and ',' not in vals['xml_root_tags']:
            raise Warning("Please specify the xml root tags seperated by comma!!!")

        if 'portal_id' in vals:
            if len(self.search([('portal_id','=',vals['portal_id']),('company_id','=',self.company_id.id)]).ids) > 1:
                raise Warning("Portal ID already exist for this company!!!")
        if 'xml_definition' in vals:
            if 'company_id' in vals and vals['company_id']:
                company_id = vals['company_id']
            else:
                company_id = self.company_id.id
            self.env['portal.xml.definition'].search([('portal_id', '=', self.portal_id),('company_id','=',company_id)]).unlink()
            csv_data = base64.b64decode(self.xml_definition)
            csv_iterator = pycompat.csv_reader(
                io.BytesIO(csv_data),
                quotechar='"',
                delimiter=',')
            next(csv_iterator)
            for row in csv_iterator:
                if self.portal_id == int(row[0]):
                    self.env['portal.xml.definition'].create({
                            'portal_id': int(row[0]),
                            'portal_field_name': row[1],
                            'portal_sub_field_name': row[2],
                            'ast_crm_field': row[3],
                            'company_id':company_id,
                        })
                else:
                    raise Warning('Mismatch in Portal Id !! Please check whether the portal id is same in csv.')
        if 'xml_definition_vals' in vals:
            if 'company_id' in vals and vals['company_id']:
                company_id = vals['company_id']
            else:
                company_id = self.company_id.id
            if 'portal_id' in vals and vals['portal_id']:
                portal_id = vals['portal_id']
            else:
                portal_id = self.portal_id
            self.env['portal.xml.definition.values'].search([('portal_id', '=', self.portal_id),('company_id','=',company_id)]).unlink()
            if vals['xml_definition_vals']:
                csv_data = base64.b64decode(self.xml_definition_vals)
                csv_iterator = pycompat.csv_reader(
                    io.BytesIO(csv_data),
                    quotechar='"',
                    delimiter=',')
                next(csv_iterator)
                for row in csv_iterator:
                    self.env['portal.xml.definition.values'].create({
                            'ast_crm_field': row[0],
                            'ast_crm_field_value': row[1],
                            'portal_field_value': row[2],
                            'portal_id': portal_id,
                            'company_id':company_id,
                        })
        return res

    @api.multi
    def email(self):
        pass

    @api.multi
    def run_staging_pull(self):
        self.env['staging.table.master'].sudo().search([],limit=1)._staging_pull()
        return

    @api.multi
    def run_staging_pull_config(self):
        self.env['staging.table.master'].sudo().search([],limit=1).manual_staging_update()
        return


class StagingTableMaster(models.Model):

    _name = 'staging.table.master'

    company_id = fields.Many2one('res.company', string='Company Id')
    crm_portal_id = fields.Many2one('crm.portal', 'Portal Id')
    listing_id = fields.Many2one('listing.listing', 'Listing Id')
    list_write_date = fields.Datetime(related='listing_id.list_write_date')
    last_updated = fields.Datetime('Last Updated')
    pull_interval = fields.Integer('Pull Interval(min)', default=0)
    detailed_ids = fields.One2many('staging.detailed.table', 'staging_id', string='Detailed data')
    is_active_feed = fields.Boolean(default=False)

    @api.multi
    def _staging_pull(self):
        start_time = datetime.now()

        base_url = str(self.env['res.company'].sudo().search([('id','=',1)]).base_url)
        xml_definition_obj = self.env['portal.xml.definition']
        detailed_table_obj = self.env['staging.detailed.table']
        detailed_images_table_obj = self.env['staging.images.table']
        detailed_facility_table_obj = self.env['staging.facilities.table']
        agent_details_obj = self.env['staging.agent.detail']
        listing_obj = self.env['listing.listing']

        time_10 = datetime.strftime(datetime.now()-timedelta(1),'%Y-%m-%d %H:%M:%S')
        published_listing_ids = listing_obj.sudo().search([('listing_status','=','Published'),('list_write_date','>',time_10)], order='list_write_date desc')
        for listing_id in published_listing_ids:
            for crm_portal_id in listing_id.portal_ids:                
                staging_master_ids = self.search([('company_id','=',crm_portal_id.company_id.id),('crm_portal_id','=',crm_portal_id.id),('listing_id','=',listing_id.id)])
                # Remove listing data from staging table those are edited after last pull
                if listing_id.list_write_date > crm_portal_id.last_xml_pull_at and staging_master_ids:
                    master_ids = staging_master_ids
                    detailed_ids = detailed_table_obj.search([('staging_id','in',master_ids.ids)])
                    detailed_images_table_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
                    agent_details_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
                    detailed_ids.unlink()
                    master_ids.unlink()
                    staging_master_ids = []
                stage = 0
                for record in staging_master_ids:
                    stage = 1
                    record.is_active_feed = True
                if stage == 1:
                    continue
                portal_xml = xml_definition_obj.search([('portal_id', '=', crm_portal_id.portal_id),('company_id','=',listing_id.company_id.id)])
                detailed_ids = []
                if crm_portal_id.name in ['Generic','Ownsite']:
                    count_value = {
                        'tag': 'count',
                        'value': ' ',
                    }
                    detailed_ids.append(detailed_table_obj.create(count_value).id)
                try: 
                    self.env.cr.execute("select * from listing_listing where id = %s",(listing_id.id,))
                    listing_values = self.env.cr.dictfetchall()
                except Exception as e:
                    logging.error('--------------------Exception occured when fetching data-----------------------//****Staging Pull!!!')
                    logging.error(e)
                for xml in portal_xml:
                    if not xml.portal_sub_field_name:
                        ir_field = self.env['ir.model.fields'].search([('name','=',xml.ast_crm_field),('model','=','listing.listing')])
                        if xml.ast_crm_field == 'preview_listing':
                            preview_url = listing_id.preview()
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': base_url + preview_url['url'],
                            }
                        elif xml.ast_crm_field == 'description':
                            if crm_portal_id.name == 'Dubizzle':
                                description_cdata = listing_id.description
                            else:
                                h = html2text.HTML2Text()
                                if listing_id.description != False:
                                    description = h.handle(str(listing_id.description))
                                    description_cdata = str(description)
                                else:
                                    description_cdata = ""
                            vals = {
                            'tag': xml.portal_field_name,
                            'value': description_cdata,
                            }
                        elif xml.portal_field_name in ['geopoints','geopoint'] and crm_portal_id.name in ['PropertyFinder','Dubizzle']:
                            if listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                geo_tag = listing_id.unit_geo_tag
                                latitude = geo_tag.split(',')[0].strip()
                                longitude = geo_tag.split(',')[1].strip()
                                geo_tag = longitude + ',' + latitude
                            else:
                                geo_tag = ""
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': geo_tag,
                            }
                        elif xml.portal_field_name == 'photos' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'image_url',
                            }
                        elif xml.portal_field_name == 'pricecurrency' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'AED',
                            }
                        elif xml.portal_field_name == 'sizeunits' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'SqFt',
                            }
                        elif xml.portal_field_name == 'status' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'vacant',
                            }
                        elif ir_field and ir_field.ttype == 'many2one':
                            field_value = (listing_id.mapped(xml.ast_crm_field)).name
                            if xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['Bayut','bayut']:
                                if not field_value:
                                    field_value = '0'
                                elif field_value == 'Studio':
                                    field_value = '-1'
                                elif int(field_value.split(' ')[0]) > 10:
                                    field_value = '10+'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                if not field_value:
                                    field_value = '0'
                                elif field_value == 'Studio':
                                    field_value = '0'
                                elif int(field_value.split(' ')[0]) > 10:
                                    field_value = '10+'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                if field_value == 'Studio':
                                    field_value = '0'
                                elif int(field_value.split(' ')[0]) > 9:
                                    field_value = '9'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bath_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                if not field_value:
                                    field_value = '0'
                                elif int(field_value) > 7:
                                    field_value = '7+'
                            elif xml.ast_crm_field == 'bath_id' and crm_portal_id.name in ['Dubizzle']:
                                if not field_value:
                                    field_value = '0'
                                elif int(field_value) > 9:
                                    field_value = '9'
                            elif xml.ast_crm_field == 'emirate_id' and crm_portal_id.name in ['Dubizzle']:
                                if field_value == 'Dubai':
                                    field_value = '2'
                                elif field_value == 'Abu Dhabi':
                                    field_value = '3'
                                elif field_value == 'Ras al-Khaimah':
                                    field_value = '11'
                                elif field_value == 'Sharjah':
                                    field_value = '12'
                                elif field_value == 'Fujairah':
                                    field_value = '13'
                                elif field_value == 'Ajman':
                                    field_value = '14'
                                elif field_value == 'Umm al-Quwain':
                                    field_value = '15'
                                elif field_value == 'Al Ain':
                                    field_value = '39'
                                else:
                                    field_value = ''
                            elif xml.ast_crm_field == 'no_of_cheques' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder'] and field_value:
                                field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'no_of_cheques' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                field_value = field_value.split(' ')[0]
                                if field_value == '1':
                                    field_value = 'YR'
                                elif field_value == '2':
                                    field_value = 'BY'
                                elif field_value == '3':
                                    field_value = 'QU'
                                else:
                                    field_value = 'MO'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['Bayut','bayut'] and field_value:
                                if field_value == 'Per Year':
                                    field_value = 'yearly'
                                elif field_value == 'Per Month':
                                    field_value = 'monthly'
                                elif field_value == 'Per Week':
                                    field_value = 'weekly'
                                elif field_value == 'Per Day':
                                    field_value = 'daily'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder'] and field_value:
                                if field_value == 'Per Year':
                                    field_value = 'Y'
                                elif field_value == 'Per Month':
                                    field_value = 'M'
                                elif field_value == 'Per Week':
                                    field_value = 'W'
                                elif field_value == 'Per Day':
                                    field_value = 'D'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                if field_value == 'Per Month':
                                    field_value = 'MO'
                                else:
                                    field_value = 'YR'
                            field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.ast_crm_field),('ast_crm_field_value','=',str(field_value)),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                            if field_val_def:
                                field_value = field_val_def.portal_field_value
                                if xml.portal_field_name == 'offering_type' and '-' in str(field_val_def.portal_field_value):
                                    if listing_id.listing_type == 'Rental':
                                        field_value = str(field_value.split('-')[1]) + 'R'
                                    elif listing_id.listing_type == 'Sale':
                                        field_value = str(field_value.split('-')[1]) + 'S'
                                elif xml.portal_field_name == 'property_type' and '-' in str(field_val_def.portal_field_value):
                                    field_value = field_value.split('-')[0]

                                elif xml.portal_field_name == 'subtype' and '-' in str(field_val_def.portal_field_value) and crm_portal_id.name in ['Dubizzle']:
                                    field_value = field_value.split('-')[0]
                                elif xml.portal_field_name == 'commercialtype' and '-' in str(field_val_def.portal_field_value) and crm_portal_id.name in ['Dubizzle']:
                                    field_value = field_value.split('-')[1]
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': str(field_value) if field_value else "",
                            }
                        elif xml.portal_field_name == 'Listing_Agent_Email':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.agent_id.user_id.login,
                            }
                        elif xml.portal_field_name == 'Listing_Agent_Phone':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.agent_id.user_id.mobile,
                            }
                        elif xml.ast_crm_field == 'parking':
                            val = 'Yes' if listing_values[0][xml.ast_crm_field] == True else 'No'
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': val,
                            }
                        elif xml.ast_crm_field == 'is_featured':
                            val = '1' if listing_values[0][xml.ast_crm_field] == True else '0'
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': val,
                            }
                        elif xml.portal_field_name == 'company_name':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.company_id.name,
                            }
                        elif xml.portal_field_name == 'company_logo':
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': base_url + '/web/image/res.company/'+ str(listing_id.company_id.id)+'/company_logo',
                            }
                        elif xml.portal_field_name == 'features':
                            value = ""
                            for feature in listing_id.feature_ids:
                                value += str(feature.name) + ","
                            value = value[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': value,
                           }
                        elif xml.portal_field_name == 'private_amenities':
                            feature_vals = ""
                            for feature in listing_id.feature_ids:
                                value = str(feature.name)
                                value = value.strip()
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=','facility'),
                                    ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def and field_val_def.portal_field_value.strip() not in ['',False]:
                                    feature_vals += field_val_def.portal_field_value.strip() + ","
                            feature_vals = feature_vals[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': feature_vals,
                            }
                        elif xml.portal_field_name == 'privateamenities' and crm_portal_id.name in ['Dubizzle']:
                            feature_vals = ""
                            for feature in listing_id.feature_ids:
                                value = str(feature.name)
                                value = value.strip()
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=','facility'),
                                    ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def and field_val_def.portal_field_value.strip() not in ['',False]:
                                    feature_vals += field_val_def.portal_field_value.strip() + "|"
                            feature_vals = feature_vals[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': feature_vals,
                            }
                        else:
                            if xml.ast_crm_field:
                                val = listing_values[0][xml.ast_crm_field]
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.ast_crm_field),('ast_crm_field_value','=',str(val)),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def:    
                                    val = field_val_def.portal_field_value
                                else:                         
                                    if type(val) == str and self.is_date(val) == True:
                                        if len(val) > 16:
                                            if crm_portal_id.name in ['Dubizzle']:
                                                val = val[:19]
                                            else:
                                                val = val[:16]
                                    elif type(val) == float:
                                        if crm_portal_id.name in ['Ownsite','ownsite'] and xml.ast_crm_field=='build_up_area_sqf':
                                            val = int(listing_id.build_up_area_sqm)
                                        elif crm_portal_id.name in ['Bayut','bayut'] and xml.portal_field_name == 'Property_Size_Unit':
                                            val = 'SQFT'
                                        else:
                                            val = int(val)
                                    elif str(xml.ast_crm_field) == 'listing_type' and crm_portal_id.name in ['Bayut','bayut']:
                                        val = 'Rent' if val == 'Rental' else 'Buy'
                                    elif str(xml.ast_crm_field) == 'furnished_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                        if val == 'yes':
                                            val = 'Y'
                                        elif val == 'no':
                                            val = 'N'
                                        elif val == 'semi':
                                            val = 'Partly'
                                    elif str(xml.ast_crm_field) == 'furnished_id' and crm_portal_id.name in ['Dubizzle']:
                                        if val == 'yes':
                                            val = '1'
                                        else:
                                            val = '0'
                                vals = {
                                    'tag': xml.portal_field_name,
                                    'value': val if xml.ast_crm_field != '' else '',
                                }
                            else:
                                if xml.portal_field_name == 'Latitude' and listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                    geo_tag = listing_id.unit_geo_tag
                                    latitude = geo_tag.split(',')[0].strip()
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': latitude,
                                    }
                                elif xml.portal_field_name == 'Longitude' and listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                    geo_tag = listing_id.unit_geo_tag
                                    longitude = geo_tag.split(',')[1].strip()
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': longitude,
                                    }
                                else:
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': '',
                                    }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'other_media' and xml.portal_sub_field_name != '' and xml.portal_sub_field_name:
                        vals = {
                            'tag': xml.portal_field_name,
                            'value': 'image_url'
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'feature_ids' and xml.portal_sub_field_name != '' and xml.portal_sub_field_name:
                        facility_ids = []
                        for facility in listing_id.feature_ids:
                            value = str(facility.name)
                            value = value.strip()
                            field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.portal_sub_field_name),
                                ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                            if field_val_def:
                                value = field_val_def.portal_field_value
                            if value.strip() not in ['',False]:
                                facility_vals = {
                                    'facility_tag': xml.portal_sub_field_name,
                                    'value': value,
                                }
                                facility_ids.append(detailed_facility_table_obj.create(facility_vals).id)
                        vals = {
                            'tag': xml.portal_field_name,
                            'facilities_ids': [(6, 0, facility_ids)]
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'agent_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                        agent_data = []
                        vals = {
                            'tag': 'id',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'name',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'email',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'phone',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'photo',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'license_no',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        
                        vals = {
                            'tag': xml.portal_field_name,
                            'agent_data_ids': [(6, 0, agent_data)]
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    else:
                        pass
                vals = {
                    'crm_portal_id': crm_portal_id.id,
                    'listing_id': listing_id.id,
                    'company_id': listing_id.company_id.id,
                    'pull_interval': crm_portal_id.pull_interval,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'detailed_ids': [(6, 0, detailed_ids)],
                    'is_active_feed': True,
                }
                res = self.create(vals)
        
        rem_start_date = datetime.now()
        old_published_listing_ids = listing_obj.sudo().search([('listing_status','=','Published'),('list_write_date','<=',time_10)])
        for listing_id in old_published_listing_ids:
            for crm_portal_id in listing_id.portal_ids:                
                staging_master_ids = self.search([('company_id','=',crm_portal_id.company_id.id),('crm_portal_id','=',crm_portal_id.id),('listing_id','=',listing_id.id)])
                for record in staging_master_ids:
                    record.is_active_feed = True
        rem_end_date = datetime.now()

        staging_rem_start_date = datetime.now()
        master_ids = self.search([('is_active_feed','=',False)])
        detailed_ids = detailed_table_obj.search([('staging_id','in',master_ids.ids)])
        detailed_images_table_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
        agent_details_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
        detailed_ids.unlink()
        master_ids.unlink()
        staging_rem_end_date = datetime.now()

        try: 
            self.env.cr.execute("update staging_table_master set is_active_feed = FALSE")
        except Exception as e:
            logging.error('--------------------Exception occured when updating staging table-----------------------//****Staging Pull!!!')
            logging.error(e)
        for portal in self.env['crm.portal'].search([('status','=',True)]):
            portal.last_xml_pull_at = start_time
        self.env['res.company'].browse(1).stage_pull_time = str(start_time) + " --> " +  str(datetime.now()) + " //\n " + str(rem_start_date) + " --> " + str(rem_end_date) + " //\n " + str(staging_rem_start_date) + " --> " + str(staging_rem_end_date)
        return

    @api.multi
    def is_date(self, string, fuzzy=False):
        try: 
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False


    @api.multi
    def manual_staging_update(self):
        c_id = int(self.env['res.company'].browse(1).api_key_type)
        portal_name = str(self.env['res.company'].browse(1).watermark)
        start_time = datetime.now()

        base_url = str(self.env['res.company'].sudo().search([('id','=',1)]).base_url)
        xml_definition_obj = self.env['portal.xml.definition']
        detailed_table_obj = self.env['staging.detailed.table']
        detailed_images_table_obj = self.env['staging.images.table']
        detailed_facility_table_obj = self.env['staging.facilities.table']
        agent_details_obj = self.env['staging.agent.detail']
        listing_obj = self.env['listing.listing']

        published_listing_ids = listing_obj.sudo().search([('listing_status', '=', 'Published'),('company_id','=',c_id),('is_portal_pull','=',False)], order='company_id asc,list_write_date desc')
        lcount = 0
        for listing_id in published_listing_ids:
            self.env.cr.execute("select * from listing_listing where id = %s",(listing_id.id,))
            listing_values = self.env.cr.dictfetchall()

            if lcount == 50:
                break

            for crm_portal_id in listing_id.portal_ids:
                crm_portal_id.last_xml_pull_at = datetime.now()

                if crm_portal_id.name != portal_name:
                    continue

                lcount += 1

                listing_id.is_portal_pull = True
                
                portal_xml = xml_definition_obj.search([('portal_id', '=', crm_portal_id.portal_id),('company_id','=',listing_id.company_id.id)])
                detailed_ids = []
                if crm_portal_id.name in ['Generic','Ownsite']:
                    count_value = {
                        'tag': 'count',
                        'value': ' ',
                    }
                    detailed_ids.append(detailed_table_obj.create(count_value).id)
                
                for xml in portal_xml:
                    if not xml.portal_sub_field_name:
                        ir_field = self.env['ir.model.fields'].search([('name','=',xml.ast_crm_field),('model','=','listing.listing')])
                        if xml.ast_crm_field == 'preview_listing':
                            preview_url = listing_id.preview()
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': base_url + preview_url['url'],
                            }
                        elif xml.ast_crm_field == 'description':
                            if crm_portal_id.name == 'Dubizzle':
                                description_cdata = listing_id.description
                            else:
                                h = html2text.HTML2Text()
                                if listing_id.description != False:
                                    description = h.handle(str(listing_id.description))
                                    description_cdata = str(description)
                                else:
                                    description_cdata = ""
                            vals = {
                            'tag': xml.portal_field_name,
                            'value': description_cdata,
                            }
                        elif xml.portal_field_name in ['geopoints','geopoint'] and crm_portal_id.name in ['PropertyFinder','Dubizzle']:
                            if listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                geo_tag = listing_id.unit_geo_tag
                                latitude = geo_tag.split(',')[0].strip()
                                longitude = geo_tag.split(',')[1].strip()
                                geo_tag = longitude + ',' + latitude
                            else:
                                geo_tag = ""
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': geo_tag,
                            }
                        elif xml.portal_field_name == 'photos' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'image_url',
                            }
                        elif xml.portal_field_name == 'pricecurrency' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'AED',
                            }
                        elif xml.portal_field_name == 'sizeunits' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'SqFt',
                            }
                        elif xml.portal_field_name == 'status' and crm_portal_id.name == 'Dubizzle':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': 'vacant',
                            }
                        elif ir_field and ir_field.ttype == 'many2one':
                            field_value = (listing_id.mapped(xml.ast_crm_field)).name
                            if xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['Bayut','bayut']:
                                if not field_value:
                                    field_value = '0'
                                elif field_value == 'Studio':
                                    field_value = '-1'
                                elif int(field_value.split(' ')[0]) > 10:
                                    field_value = '10+'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                if not field_value:
                                    field_value = '0'
                                elif field_value == 'Studio':
                                    field_value = '0'
                                elif int(field_value.split(' ')[0]) > 10:
                                    field_value = '10+'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bed_id' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                if field_value == 'Studio':
                                    field_value = '0'
                                elif int(field_value.split(' ')[0]) > 9:
                                    field_value = '9'
                                else:
                                    field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'bath_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                if not field_value:
                                    field_value = '0'
                                elif int(field_value) > 7:
                                    field_value = '7+'
                            elif xml.ast_crm_field == 'bath_id' and crm_portal_id.name in ['Dubizzle']:
                                if not field_value:
                                    field_value = '0'
                                elif int(field_value) > 9:
                                    field_value = '9'
                            elif xml.ast_crm_field == 'emirate_id' and crm_portal_id.name in ['Dubizzle']:
                                if field_value == 'Dubai':
                                    field_value = '2'
                                elif field_value == 'Abu Dhabi':
                                    field_value = '3'
                                elif field_value == 'Ras al-Khaimah':
                                    field_value = '11'
                                elif field_value == 'Sharjah':
                                    field_value = '12'
                                elif field_value == 'Fujairah':
                                    field_value = '13'
                                elif field_value == 'Ajman':
                                    field_value = '14'
                                elif field_value == 'Umm al-Quwain':
                                    field_value = '15'
                                elif field_value == 'Al Ain':
                                    field_value = '39'
                                else:
                                    field_value = ''
                            elif xml.ast_crm_field == 'no_of_cheques' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder'] and field_value:
                                field_value = field_value.split(' ')[0]
                            elif xml.ast_crm_field == 'no_of_cheques' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                field_value = field_value.split(' ')[0]
                                if field_value == '1':
                                    field_value = 'YR'
                                elif field_value == '2':
                                    field_value = 'BY'
                                elif field_value == '3':
                                    field_value = 'QU'
                                else:
                                    field_value = 'MO'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['Bayut','bayut'] and field_value:
                                if field_value == 'Per Year':
                                    field_value = 'yearly'
                                elif field_value == 'Per Month':
                                    field_value = 'monthly'
                                elif field_value == 'Per Week':
                                    field_value = 'weekly'
                                elif field_value == 'Per Day':
                                    field_value = 'daily'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder'] and field_value:
                                if field_value == 'Per Year':
                                    field_value = 'Y'
                                elif field_value == 'Per Month':
                                    field_value = 'M'
                                elif field_value == 'Per Week':
                                    field_value = 'W'
                                elif field_value == 'Per Day':
                                    field_value = 'D'
                            elif xml.ast_crm_field == 'price_frequency_id' and crm_portal_id.name in ['Dubizzle'] and field_value:
                                if field_value == 'Per Month':
                                    field_value = 'MO'
                                else:
                                    field_value = 'YR'
                            field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.ast_crm_field),('ast_crm_field_value','=',str(field_value)),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                            if field_val_def:
                                field_value = field_val_def.portal_field_value
                                if xml.portal_field_name == 'offering_type' and '-' in str(field_val_def.portal_field_value):
                                    if listing_id.listing_type == 'Rental':
                                        field_value = str(field_value.split('-')[1]) + 'R'
                                    elif listing_id.listing_type == 'Sale':
                                        field_value = str(field_value.split('-')[1]) + 'S'
                                elif xml.portal_field_name == 'property_type' and '-' in str(field_val_def.portal_field_value):
                                    field_value = field_value.split('-')[0]

                                elif xml.portal_field_name == 'subtype' and '-' in str(field_val_def.portal_field_value) and crm_portal_id.name in ['Dubizzle']:
                                    field_value = field_value.split('-')[0]
                                elif xml.portal_field_name == 'commercialtype' and '-' in str(field_val_def.portal_field_value) and crm_portal_id.name in ['Dubizzle']:
                                    field_value = field_value.split('-')[1]
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': str(field_value) if field_value else "",
                            }
                        elif xml.portal_field_name == 'Listing_Agent_Email':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.agent_id.user_id.login,
                            }
                        elif xml.portal_field_name == 'Listing_Agent_Phone':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.agent_id.user_id.mobile,
                            }
                        elif xml.ast_crm_field == 'parking':
                            val = 'Yes' if listing_values[0][xml.ast_crm_field] == True else 'No'
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': val,
                            }
                        elif xml.ast_crm_field == 'is_featured':
                            val = '1' if listing_values[0][xml.ast_crm_field] == True else '0'
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': val,
                            }
                        elif xml.portal_field_name == 'company_name':
                            vals = {
                                'tag': xml.portal_field_name,
                                'value': listing_id.company_id.name,
                            }
                        elif xml.portal_field_name == 'company_logo':
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': base_url + '/web/image/res.company/'+ str(listing_id.company_id.id)+'/company_logo',
                            }
                        elif xml.portal_field_name == 'features':
                            value = ""
                            for feature in listing_id.feature_ids:
                                value += str(feature.name) + ","
                            value = value[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': value,
                           }
                        elif xml.portal_field_name == 'private_amenities':
                            feature_vals = ""
                            for feature in listing_id.feature_ids:
                                value = str(feature.name)
                                value = value.strip()
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=','facility'),
                                    ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def and field_val_def.portal_field_value.strip() not in ['',False]:
                                    feature_vals += field_val_def.portal_field_value.strip() + ","
                            feature_vals = feature_vals[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': feature_vals,
                            }
                        elif xml.portal_field_name == 'privateamenities' and crm_portal_id.name in ['Dubizzle']:
                            feature_vals = ""
                            for feature in listing_id.feature_ids:
                                value = str(feature.name)
                                value = value.strip()
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=','facility'),
                                    ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def and field_val_def.portal_field_value.strip() not in ['',False]:
                                    feature_vals += field_val_def.portal_field_value.strip() + "|"
                            feature_vals = feature_vals[:-1]
                            vals = {
                               'tag': xml.portal_field_name,
                               'value': feature_vals,
                            }
                        else:
                            if xml.ast_crm_field:
                                val = listing_values[0][xml.ast_crm_field]
                                field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.ast_crm_field),('ast_crm_field_value','=',str(val)),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                                if field_val_def:    
                                    val = field_val_def.portal_field_value
                                else:                         
                                    if type(val) == str and self.is_date(val) == True:
                                        if len(val) > 16:
                                            if crm_portal_id.name in ['Dubizzle']:
                                                val = val[:19]
                                            else:
                                                val = val[:16]
                                    elif type(val) == float:
                                        if crm_portal_id.name in ['Ownsite','ownsite'] and xml.ast_crm_field=='build_up_area_sqf':
                                            val = int(listing_id.build_up_area_sqm)
                                        elif crm_portal_id.name in ['Bayut','bayut'] and xml.portal_field_name == 'Property_Size_Unit':
                                            val = 'SQFT'
                                        else:
                                            val = int(val)
                                    elif str(xml.ast_crm_field) == 'listing_type' and crm_portal_id.name in ['Bayut','bayut']:
                                        val = 'Rent' if val == 'Rental' else 'Buy'
                                    elif str(xml.ast_crm_field) == 'furnished_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                                        if val == 'yes':
                                            val = 'Y'
                                        elif val == 'no':
                                            val = 'N'
                                        elif val == 'semi':
                                            val = 'Partly'
                                    elif str(xml.ast_crm_field) == 'furnished_id' and crm_portal_id.name in ['Dubizzle']:
                                        if val == 'yes':
                                            val = '1'
                                        else:
                                            val = '0'
                                vals = {
                                    'tag': xml.portal_field_name,
                                    'value': val if xml.ast_crm_field != '' else '',
                                }
                            else:
                                if xml.portal_field_name == 'Latitude' and listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                    geo_tag = listing_id.unit_geo_tag
                                    latitude = geo_tag.split(',')[0].strip()
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': latitude,
                                    }
                                elif xml.portal_field_name == 'Longitude' and listing_id.unit_geo_tag and ',' in str(listing_id.unit_geo_tag):
                                    geo_tag = listing_id.unit_geo_tag
                                    longitude = geo_tag.split(',')[1].strip()
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': longitude,
                                    }
                                else:
                                    vals = {
                                        'tag': xml.portal_field_name,
                                        'value': '',
                                    }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'other_media' and xml.portal_sub_field_name != '' and xml.portal_sub_field_name:
                        vals = {
                            'tag': xml.portal_field_name,
                            'value': 'image_url'
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'feature_ids' and xml.portal_sub_field_name != '' and xml.portal_sub_field_name:
                        facility_ids = []
                        for facility in listing_id.feature_ids:
                            value = str(facility.name)
                            value = value.strip()
                            field_val_def = self.env['portal.xml.definition.values'].search([('ast_crm_field','=',xml.portal_sub_field_name),
                                ('ast_crm_field_value','=',value),('company_id','=',xml.company_id.id),('portal_id','=',xml.portal_id)])
                            if field_val_def:
                                value = field_val_def.portal_field_value
                            if value.strip() not in ['',False]:
                                facility_vals = {
                                    'facility_tag': xml.portal_sub_field_name,
                                    'value': value,
                                }
                                facility_ids.append(detailed_facility_table_obj.create(facility_vals).id)
                        vals = {
                            'tag': xml.portal_field_name,
                            'facilities_ids': [(6, 0, facility_ids)]
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    elif xml.ast_crm_field == 'agent_id' and crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                        agent_data = []
                        vals = {
                            'tag': 'id',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'name',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'email',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'phone',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'photo',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        vals = {
                            'tag': 'license_no',
                            'value': ' ',
                        }
                        agent_data.append(agent_details_obj.create(vals).id)
                        
                        vals = {
                            'tag': xml.portal_field_name,
                            'agent_data_ids': [(6, 0, agent_data)]
                        }
                        detailed_ids.append(detailed_table_obj.create(vals).id)
                    else:
                        pass
                vals = {
                    'crm_portal_id': crm_portal_id.id,
                    'listing_id': listing_id.id,
                    'company_id': listing_id.company_id.id,
                    'pull_interval': crm_portal_id.pull_interval,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'detailed_ids': [(6, 0, detailed_ids)],
                    'is_active_feed': True,
                }
                res = self.create(vals)

        self.env['res.company'].browse(1).stage_pull_time = str(start_time) + " \n " +  str(datetime.now())
        return


class StagingDetailedTable(models.Model):
    _name = 'staging.detailed.table'

    staging_id = fields.Many2one('staging.table.master', 'Staging')
    tag = fields.Char('Tag', required=True)
    value = fields.Char('Value')
    images_ids = fields.One2many('staging.images.table', 'staging_detailed_id', string='Image Details')
    facilities_ids = fields.One2many('staging.facilities.table', 'staging_detailed_id', string='Facility Details')
    agent_data_ids = fields.One2many('staging.agent.detail', 'staging_detailed_id', string='Agent Details')


class StagingImagesTable(models.Model):
    _name = 'staging.images.table'

    staging_detailed_id = fields.Many2one('staging.detailed.table', 'Staging Detailed')
    image_tag = fields.Char('Tag', required=True)
    value = fields.Char('Value')


class StagingFacilitiesTable(models.Model):
    _name = 'staging.facilities.table'

    staging_detailed_id = fields.Many2one('staging.detailed.table', 'Staging Detailed')
    facility_tag = fields.Char('Tag', required=True)
    value = fields.Char('Value')

class StagingAgentDetailsTable(models.Model):
    _name = 'staging.agent.detail'

    staging_detailed_id = fields.Many2one('staging.detailed.table', 'Staging Detailed')
    tag = fields.Char()
    value = fields.Char()


class PortalXMLDefinition(models.Model):
    _name = 'portal.xml.definition'

    portal_id = fields.Char('Portal Id')
    portal_field_name = fields.Char('Portal Field Name')
    portal_sub_field_name = fields.Char('Portal Sub Field Name')
    portal_field_type = fields.Char('Portal Field Type')
    ast_crm_field = fields.Char('AST CRM Field')
    ast_crm_field_order = fields.Char('AST CRM Field Order')
    company_id = fields.Many2one('res.company')

class PortalXMLDefinitionValues(models.Model):
    _name = 'portal.xml.definition.values'

    ast_crm_field = fields.Char()
    ast_crm_field_value = fields.Char()
    portal_field_value = fields.Char()
    company_id = fields.Many2one('res.company')
    portal_id = fields.Integer()