# -*- coding: utf-8 -*-

{
    'name': 'vrs',
    'summary': 'Vacation Request System',
    'depends': [],
    'data': [
        'security/vrs_security.xml',
        'security/ir.model.access.csv',

        'views/employee_views.xml',
        'views/request_views.xml',
        'views/approve_views.xml',
        'views/my_requests_views.xml',

        'wizard/request_wizard_views.xml',

        'views/menu.xml'
    ],
    'application': False,
    'auto_install': False,
    'installable': True
}
