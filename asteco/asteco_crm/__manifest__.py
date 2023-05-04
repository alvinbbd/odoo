# -*- coding: utf-8 -*-
{
    'name': "Asteco CRM",
    'summary': """
        Asteco CRM
    """,
    'description': """
        Asteco CRM
    """,
    'author': "SANESQUARE Technologies",
    'website': "https://sanesquare.com",
    'category': 'crm',
    'version': '11.0.1',
    'depends': [
        'web',
        'mail',
        'calendar',
        'asteco_custom_theme',
        'crnd_web_widget_popup_image',
        'ks_toggle_switch',
        'account_invoicing',
        'portal',
        'website',
        'datepicker_disable_autocomplete',
        'fetchmail',
        'hr',
        'employee_creation_from_user',
        'restapi',
        'web_access_rule_buttons',
        'web_disable_export_group',
        'web_widget_many2many_tags_multi_selection',
        'website_sale',
        'multi_attachment_product_image',
        # 'login_user_detail',
    ],
    'images': [],
    'license': 'AGPL-3',
    'data': [
        'security/asteco_security.xml',
        'security/ir.model.access.csv',
        'enquiry/views/enquiry_views.xml',
        'menus/menu_views.xml',

        'res/views/res_company_views.xml',
        'res/views/res_user_views.xml',
        'res/data/res_data.xml',
        'res/data/country_code.xml',
        'res/data/res.lang.csv',
        
        'invoice/reports/report_proforma_invoice.xml',
        'invoice/reports/template_layout.xml',
        'tempreceipt/reports/report_temp_receipt.xml',

        'mail/views/email_template.xml',
        'mail/views/mail_compose_message_view.xml',

        'listing/data/sequence.xml',
        'listing/views/listing_views.xml',
        'listing/views/listing_html_preview.xml',
       
        'contacts/views/contacts_views.xml',
        'contacts/data/sequence.xml',
        'contacts/wizard/call_centre_agent_wizard.xml',

        'leads/views/lead_views.xml',
        'leads/views/lead_rotation_views.xml',
        'leads/views/assets.xml',
        'leads/data/sequence.xml',
        'leads/data/data.xml',
        
        'escalation/views/escalation_views.xml',
        'escalation/views/cron.xml',
        'escalation/data/data.xml',

        'deals/views/deal_views.xml',
        'deals/data/sequence.xml',

        'actions/views/actions_views.xml',

        'opportunities/views/opportunity_views.xml',
        'opportunities/views/templates.xml',
        'opportunities/data/data.xml',

        'listing/data/data.xml',
        'listing/views/template.xml',
        'listing/views/listing_field_views.xml',
        'calendar/views/calendar_views.xml',

        'contacts/data/data.xml',

        'deals/wizard/wizard_views.xml',

        'agents/data/data.xml',
        'agents/views/agents_views.xml',

        'employee/views/employee_views.xml',
        'static/src/xml/assets.xml',
        'listing/data/location.xml',
        'listing/data/sub_location.xml',
        'actions/data/data.xml',
        'invoice/views/invoice_views.xml',
        'invoice/data/sequence.xml',
        'tempreceipt/views/temp_views.xml',
        'tempreceipt/data/sequence.xml',

        'portals/views/cron.xml',
        'portals/views/portals_views.xml',

        'dashboard/views/dashboard_views.xml',
        'dashboard/views/assets.xml',

        'audit_trail/views/audit_trail_views.xml',

        'reports/views/reports_views.xml',
        'reports/views/report_deal_number_views.xml',
        'reports/views/listing_report_summery.xml',
        'reports/views/agent_performance_report.xml',
        'reports/views/reports_leads_lost_views.xml',
        'reports/views/reports_deals_lost_views.xml',
        'reports/views/reports_deal_views.xml',
        'reports/views/leads_and_deals_report.xml',        
        'reports/views/template_report_analysis.xml',        
        'reports/views/reports_commission_deals.xml',


        'management_reports/views/management_reports_views.xml',

        'market_intelligence/views/market_intelligence_views.xml',
        'res/security/fields_security.xml',

        'configuration/views/configuration_views.xml',
        'data_loading/deal_temp_views.xml',
        'document_management/views/document_management_views.xml',
    ],
    'qweb': [
        'static/src/xml/many2many_checkbox.xml',
        'dashboard/static/src/xml/dashboard.xml',
    ],
    'application': True,
    'installable': True,
}