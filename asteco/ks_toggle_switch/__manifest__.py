# -*- coding: utf-8 -*-
{
    'name': "Toggle Switch",

    'summary': """
        Toggle Switch for version 11.0 """,

    'description': """
        Toggle Switch for version 11.0
        -toggle button,
        -boolean toggle,
        -boolean field toggle,
        -checkbox to toggle,
        -odoo toggle switch,
    """,

    'author': "Ksolves",
    'website': "https://www.ksolves.com/",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': '9.0',
    'category': 'Tools',
    'support': 'sales@ksolves.com',
    'version': '1.0.0',
    # 'live_test_url':'https://youtu.be/bD_SjbySwbk',
    'images': [
        'static/description/main.jpg',
    ],
    'depends': ['base','web','base_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/ks_assets.xml',
        'views/ks_inherited_res_config.xml'
    ],
    # only loaded in demonstration mode

}
