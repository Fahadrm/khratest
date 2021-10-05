# -*- coding: utf-8 -*-
{
    'name': "KHRA Yelo Orders",

    'summary': """
        Receive data from yelo via webhook, then save data to odoo""",

    'description': """
        Receive data from yelo via webhook, then save data to odoo
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'khra_account_settings'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/account_move_views.xml',
        'views/configure_webhook_view.xml',
        'data/order_sync_cron.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
