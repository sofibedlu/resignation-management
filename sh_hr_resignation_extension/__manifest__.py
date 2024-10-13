{
    'name': 'Custom Resignation Management',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Manage resignations based on contract type with notice period validation and countdown',
    'depends': ['sh_all_in_one_hrms'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sh_resignation_views.xml',
        'views/notice_period_config_views.xml',
        'data/ir_cron_data.xml',
        'data/sh_resignation_mail_template_ext.xml',
    ],
    'installable': True,
    'application': False,
}