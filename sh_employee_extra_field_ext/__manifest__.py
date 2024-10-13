{
    'name': 'Employee Custom Fields',
    'version': '1.0',
    'catagory': 'Human Resources',
    'summary': 'Add custom fields to employee',
    'description': 'This module adds custom fields like account_number and tax_id to the employee model.',
    'author': 'Sofonias',
    'depends': ['hr', 'sh_all_in_one_hrms'],
    'data': [
        'views/employee_custom_view.xml',
    ],
    'installable': True,
    'application': False,
}