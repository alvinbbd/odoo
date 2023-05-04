from lxml import etree
from odoo import http
from odoo.http import request
import sys
from dateutil import tz
import datetime

class Main(http.Controller):

    @http.route(['/feed/xml'], method="POST", type='http', auth="public", website=True)
    def xml_pull(self, **kwargs):
        values = dict(kwargs)
        if 'portal' not in values or 'C_ID' not in values:
            return "Invalid URL!!!"
        elif not values['portal'] or not values['C_ID']:
            return "Invalid parameters!!!"

        company_id = request.env['res.company'].sudo().search([('code', '=', values['C_ID'])], limit=1)
        if not company_id:
            return "Invalid company code!!!"

        domain_portal = []
        domain_portal.append(('portal_id', '=', int(values['portal'])))
        domain_portal.append(('company_id', '=', company_id.id))
        crm_portal_id = request.env['crm.portal'].sudo().search(domain_portal, limit=1)
        if not crm_portal_id:
            return "Invalid portal specified!!!"
        
        base_url = str(request.env['res.company'].sudo().search([('id','=',1)]).base_url)
        domain_staging = []
        domain_staging.append(('company_id', '=', company_id.id))
        domain_staging.append(('crm_portal_id', '=', crm_portal_id.id))
        staging_ids = request.env['staging.table.master'].sudo().search(domain_staging, order="list_write_date desc")
        staging_detailed_obj = request.env['staging.detailed.table']
        portal_list = ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder','Bayut','bayut']

        # create XML
        root_tag = crm_portal_id.xml_root_tags.split(',')[0]
        sub_root_tag = crm_portal_id.xml_root_tags.split(',')[1]
        root = etree.Element(root_tag)
        if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
            root.set("last_update", str(datetime.datetime.strptime(crm_portal_id.last_xml_pull_at,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=4)))

        listing_count = 0
        for staging in staging_ids:
            tag_list = []
            listing_count += 1
            sub_root = etree.Element(sub_root_tag)

            if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                list_write_date = str(datetime.datetime.strptime(staging.listing_id.list_write_date,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=4))
                sub_root.set("last_update", list_write_date)

            root.append(sub_root)
            tag_ids = staging_detailed_obj.sudo().search([('staging_id', '=', staging.id)])
            for tag_id in tag_ids:
                if crm_portal_id.name == 'PropertyFinder' and tag_id.tag == 'features':
                    continue
                if tag_id.tag in tag_list:
                    tag_id.unlink()
                    continue
                else:
                    tag_list.append(tag_id.tag)
                if tag_id.tag == 'count':
                    if crm_portal_id.name in ['PropertyFinder','Bayut','Dubizzle']:
                        continue
                    else:
                        tag_id.value = str(listing_count)
                child = etree.SubElement(sub_root, tag_id.tag.strip())

                if not tag_id.value:
                    if tag_id.facilities_ids:
                        for facility in tag_id.facilities_ids:
                            child_2 = etree.SubElement(child, facility.facility_tag.strip())
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(facility.value))
                            else:
                                child_2.text = str(facility.value)
                    elif tag_id.tag == 'agent':
                        child_2 = etree.SubElement(child, 'id')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.id))
                        child_2 = etree.SubElement(child, 'name')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.name))
                        child_2 = etree.SubElement(child, 'email')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.email))
                        child_2 = etree.SubElement(child, 'phone')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.mobile))
                        child_2 = etree.SubElement(child, 'photo')
                        child_2.text = etree.CDATA(str(base_url + '/web/image/res.users/'+ str(staging.listing_id.sudo().agent_id.user_id.id)+'/image'))
                        child_2 = etree.SubElement(child, 'license_no')
                        value = staging.listing_id.sudo().agent_id.user_id.rera_brn if staging.listing_id.sudo().agent_id.user_id.rera_brn else ""
                        child_2.text = etree.CDATA(str(value))
                    elif crm_portal_id.name in ['Bayut'] and tag_id.tag.strip() == 'Property_Status':
                        child.text = etree.CDATA('live')
                    elif crm_portal_id.name in ['PropertyFinder'] and tag_id.tag.strip() == 'geopoints':
                        child.text = etree.CDATA('55.275298,25.209901')
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'contactemail':
                        child.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.email))
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'contactnumber':
                        child.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.mobile))
                    else:
                        child.text = " "    
                else:
                    if tag_id.value == 'image_url' and crm_portal_id.name not in ['Dubizzle']:
                        if crm_portal_id.name in ['PropertyFinder']:
                            tag = 'url'
                        else:
                            tag = 'image'
                        flag = 0
                        if staging.listing_id.photo:
                            flag = 1
                            child_2 = etree.SubElement(child, tag)
                            image_url = base_url + '/web/image/listing.listing/'+ str(staging.listing_id.id)+'/photo'
                            if crm_portal_id.name in ['PropertyFinder']:
                                child_2.set("last_update", list_write_date)
                                child_2.set("watermark", "no")
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(image_url))
                            else:
                                child_2.text = str(image_url)
                        for image in staging.listing_id.sudo().other_media:
                            flag = 1
                            child_2 = etree.SubElement(child, tag)
                            image_url = base_url + '/web/image/media.media/'+ str(image.id)+'/image'
                            if crm_portal_id.name in ['PropertyFinder']:
                                child_2.set("last_update", list_write_date)
                                child_2.set("watermark", "no")
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(image_url))
                            else:
                                child_2.text = str(image_url)
                        if flag == 0:
                            child.text = ' '
                    elif tag_id.value == 'image_url' and crm_portal_id.name in ['Dubizzle']:
                        if staging.listing_id.photo:
                            image_data = base_url + '/web/image/listing.listing/'+ str(staging.listing_id.id)+'/photo|'
                        else:
                            image_data = ''
                        for image in staging.listing_id.other_media:
                            image_data += base_url + '/web/image/media.media/'+ str(image.id)+'/image|'
                        image_data = image_data[:-1]
                        child.text = etree.CDATA(str(image_data))
                    elif crm_portal_id.name in portal_list or str(tag_id.tag) == 'Web_Remarks':
                        child.text = etree.CDATA(str(tag_id.value))
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'lastupdated' and len(tag_id.value) == 16:
                        child.text = str(tag_id.value) + ':00'
                    else:
                        if crm_portal_id.name == 'Dubizzle':
                            child.text = etree.CDATA(str(tag_id.value))
                        else:
                            child.text = str(tag_id.value)
        if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
            root.set("listing_count", str(listing_count))
            xml_String = etree.tostring(root,xml_declaration=True,encoding="UTF-8")
        else:
            xml_String = etree.tostring(root,xml_declaration=True,encoding="ISO-8859-1")
        headers = [
            ('Content-Type', 'text/xml'),
        ]
        return request.make_response(xml_String, headers=headers)

    @http.route(['/feed/xml/inc'], method="POST", type='http', auth="public", website=True)
    def xml_pull_increment(self, **kwargs):
        values = dict(kwargs)
        if 'portal' not in values or 'C_ID' not in values:
            return "Invalid URL!!!"
        elif not values['portal'] or not values['C_ID']:
            return "Invalid parameters!!!"

        company_id = request.env['res.company'].sudo().search([('code', '=', values['C_ID'])], limit=1)
        if not company_id:
            return "Invalid company code!!!"

        domain_portal = []
        domain_portal.append(('portal_id', '=', int(values['portal'])))
        domain_portal.append(('company_id', '=', company_id.id))
        crm_portal_id = request.env['crm.portal'].sudo().search(domain_portal, limit=1)
        if not crm_portal_id:
            return "Invalid portal specified!!!"
        
        base_url = str(request.env['res.company'].sudo().search([('id','=',1)]).base_url)
        domain_staging = []
        domain_staging.append(('company_id', '=', company_id.id))
        domain_staging.append(('crm_portal_id', '=', crm_portal_id.id))
        second_last_pull = datetime.datetime.strptime(crm_portal_id.last_xml_pull_at,'%Y-%m-%d %H:%M:%S') - datetime.timedelta(minutes=60)
        domain_staging.append(('list_write_date', '>', datetime.datetime.strftime(second_last_pull,'%Y-%m-%d %H:%M:%S')))
        staging_ids = request.env['staging.table.master'].sudo().search(domain_staging, order="list_write_date desc")

        staging_detailed_obj = request.env['staging.detailed.table']
        portal_list = ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder','Bayut','bayut']

        # create XML
        root_tag = crm_portal_id.xml_root_tags.split(',')[0]
        sub_root_tag = crm_portal_id.xml_root_tags.split(',')[1]
        root = etree.Element(root_tag)
        if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
            root.set("last_update", str(datetime.datetime.strptime(crm_portal_id.last_xml_pull_at,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=4)))

        listing_count = 0
        for staging in staging_ids:
            tag_list = []
            listing_count += 1
            sub_root = etree.Element(sub_root_tag)

            if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
                list_write_date = str(datetime.datetime.strptime(staging.listing_id.list_write_date,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=4))
                sub_root.set("last_update", list_write_date)

            root.append(sub_root)
            tag_ids = staging_detailed_obj.sudo().search([('staging_id', '=', staging.id)])
            for tag_id in tag_ids:
                if crm_portal_id.name == 'PropertyFinder' and tag_id.tag == 'features':
                    continue
                if tag_id.tag in tag_list:
                    tag_id.unlink()
                    continue
                else:
                    tag_list.append(tag_id.tag)
                if tag_id.tag == 'count':
                    if crm_portal_id.name in ['PropertyFinder','Bayut','Dubizzle']:
                        continue
                    else:
                        tag_id.value = str(listing_count)
                child = etree.SubElement(sub_root, tag_id.tag.strip())

                if not tag_id.value:
                    if tag_id.facilities_ids:
                        for facility in tag_id.facilities_ids:
                            child_2 = etree.SubElement(child, facility.facility_tag.strip())
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(facility.value))
                            else:
                                child_2.text = str(facility.value)
                    elif tag_id.tag == 'agent':
                        child_2 = etree.SubElement(child, 'id')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.id))
                        child_2 = etree.SubElement(child, 'name')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.name))
                        child_2 = etree.SubElement(child, 'email')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.email))
                        child_2 = etree.SubElement(child, 'phone')
                        child_2.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.mobile))
                        child_2 = etree.SubElement(child, 'photo')
                        child_2.text = etree.CDATA(str(base_url + '/web/image/res.users/'+ str(staging.listing_id.sudo().agent_id.user_id.id)+'/image'))
                        child_2 = etree.SubElement(child, 'license_no')
                        value = staging.listing_id.sudo().agent_id.user_id.rera_brn if staging.listing_id.sudo().agent_id.user_id.rera_brn else ""
                        child_2.text = etree.CDATA(str(value))
                    elif crm_portal_id.name in ['Bayut'] and tag_id.tag.strip() == 'Property_Status':
                        child.text = etree.CDATA('live')
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'contactemail':
                        child.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.email))
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'contactnumber':
                        child.text = etree.CDATA(str(staging.listing_id.sudo().agent_id.user_id.mobile))
                    else:
                        child.text = " "    
                else:
                    if tag_id.value == 'image_url' and crm_portal_id.name not in ['Dubizzle']:
                        if crm_portal_id.name in ['PropertyFinder']:
                            tag = 'url'
                        else:
                            tag = 'image'
                        flag = 0
                        if staging.listing_id.photo:
                            flag = 1
                            child_2 = etree.SubElement(child, tag)
                            image_url = base_url + '/web/image/listing.listing/'+ str(staging.listing_id.id)+'/photo'
                            if crm_portal_id.name in ['PropertyFinder']:
                                child_2.set("last_update", list_write_date)
                                child_2.set("watermark", "no")
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(image_url))
                            else:
                                child_2.text = str(image_url)
                        for image in staging.listing_id.sudo().other_media:
                            flag = 1
                            child_2 = etree.SubElement(child, tag)
                            image_url = base_url + '/web/image/media.media/'+ str(image.id)+'/image'
                            if crm_portal_id.name in ['PropertyFinder']:
                                child_2.set("last_update", list_write_date)
                                child_2.set("watermark", "no")
                            if crm_portal_id.name in portal_list:
                                child_2.text = etree.CDATA(str(image_url))
                            else:
                                child_2.text = str(image_url)
                        if flag == 0:
                            child.text = ' '
                    elif tag_id.value == 'image_url' and crm_portal_id.name in ['Dubizzle']:
                        if staging.listing_id.photo:
                            image_data = base_url + '/web/image/listing.listing/'+ str(staging.listing_id.id)+'/photo|'
                        else:
                            image_data = ''
                        for image in staging.listing_id.other_media:
                            image_data += base_url + '/web/image/media.media/'+ str(image.id)+'/image|'
                        image_data = image_data[:-1]
                        child.text = etree.CDATA(str(image_data))
                    elif crm_portal_id.name in portal_list or str(tag_id.tag) == 'Web_Remarks':
                        child.text = etree.CDATA(str(tag_id.value))
                    elif crm_portal_id.name in ['Dubizzle'] and tag_id.tag.strip() == 'lastupdated' and len(tag_id.value) == 16:
                        child.text = str(tag_id.value) + ':00'
                    else:
                        if crm_portal_id.name == 'Dubizzle':
                            child.text = etree.CDATA(str(tag_id.value))
                        else:
                            child.text = str(tag_id.value)
        if crm_portal_id.name in ['propertyfinder','Propertyfinder','PropertyFinder','Property Finder']:
            root.set("listing_count", str(listing_count))
            xml_String = etree.tostring(root,xml_declaration=True,encoding="UTF-8")
        else:
            xml_String = etree.tostring(root,xml_declaration=True,encoding="ISO-8859-1")
        headers = [
            ('Content-Type', 'text/xml'),
        ]
        return request.make_response(xml_String, headers=headers)


    @http.route(['/update/staging'], method="POST", type='http', auth="public", website=True)
    def update_description(self, **kwargs):

        master_obj = request.env['staging.table.master']
        detailed_table_obj = request.env['staging.detailed.table']
        detailed_images_table_obj = request.env['staging.images.table']
        agent_details_obj = request.env['staging.agent.detail']

        company_id = int(request.env['res.company'].browse(1).api_key_type)
        portal_id = int(request.env['res.company'].browse(1).api_key)

        master_ids = master_obj.search([('company_id','=',company_id),('crm_portal_id','=',portal_id)])
        detailed_ids = detailed_table_obj.search([('staging_id','in',master_ids.ids)])
        detailed_images_table_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
        agent_details_obj.search([('staging_detailed_id','in',detailed_ids.ids)]).unlink()
        detailed_ids.unlink()
        master_ids.unlink()
        return "Done"


    @http.route(['/update/listing/portal'], method="POST", type='http', auth="public", website=True)
    def update_descriptionssss(self, **kwargs):
        request.env.cr.execute("update listing_listing set is_portal_pull = FALSE")
        return "Done"

