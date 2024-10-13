from odoo import models, fields, api, exceptions
from datetime import timedelta, datetime
#import logging

#_logger = logging.getLogger(__name__)

class ShResignation(models.Model):
    _inherit = 'sh.hr.resignation'

    countdown_days = fields.Integer(string='Countdown Days', compute='_compute_days', store=True)
    remaining_working_days = fields.Integer(string='Remaining Working Days', compute='_compute_days', store=True)
    description = fields.Text('Description', required=True)
    attachment = fields.Binary('Document Attachment', required=True)

    hr_responsible_ids = fields.Many2many(
        'hr.employee', string="HR Responsible",
        compute='_compute_hr_responsible_ids', store=True)
    
    notice_period_id = fields.Many2one('notice.period.config', string='Notice Period', required=True)
    
    @api.depends('sh_contract_id')
    def _compute_hr_responsible_ids(self):
        # Fetch HR responsible employees once
        hr_responsible_employees = self.env['hr.employee'].search([('hr_responsible', '=', True)])
        for record in self:
            record.hr_responsible_ids = hr_responsible_employees

    @api.depends('state', 'notice_period_id')
    def _compute_days(self):
        for rec in self:
            if rec.state == 'approve':
                notice_days = rec.notice_period_id.notice_days if rec.notice_period_id else 30
                warning_days = rec.notice_period_id.warning_days if rec.notice_period_id else 5

                notice_end_date = rec.create_date.date() + timedelta(days=notice_days)  # Keep the original end date
                #countdown_minutes = (notice_end_date - datetime.now()).total_seconds() // 60
                #rec.countdown_days = countdown_minutes
                #rec.remaining_working_days = countdown_minutes
                countdown_days = (notice_end_date - fields.Date.today()).days
                rec.countdown_days = countdown_days
                rec.remaining_working_days = countdown_days

                # Trigger warning if remaining working days are less than warning days
                if rec.remaining_working_days == warning_days:
                    rec._send_warning()

            else:
                rec.countdown_days = 0
                rec.remaining_working_days = 0

    @api.constrains('sh_contract_id')
    def _check_contract_notice_period(self):
        for rec in self:
            if rec.sh_contract_id and rec.sh_contract_id.sudo().date_end:
                notice_days = rec.notice_period_id.notice_days if rec.notice_period_id else 30
                remaining_days = (rec.sh_contract_id.sudo().date_end - fields.Date.today()).days
                if remaining_days < notice_days:
                    raise exceptions.ValidationError(
                        "The remaining contract period is less than the required notice period."
                    )

    @api.model
    def create(self, vals):
        records = super(ShResignation, self).create(vals)
        records._check_contract_notice_period()
        return records

    def update_remaining_working_days(self):
        #_logger.info('Running update_remaining_working_days cron job')
        resignations = self.search([('state', '=', 'approve')])
        for resignation in resignations:
            resignation._compute_days()

    def _send_warning(self):
        for rec in self:
            warning_days = rec.notice_period_id.warning_days if rec.notice_period_id else 5
            for hr_responsible in rec.hr_responsible_ids:
                rec.activity_schedule(
                    'mail.mail_activity_data_warning',
                    user_id=hr_responsible.user_id.id,
                    date_deadline = fields.Date.today() + timedelta(days=warning_days),
                    summary='Resignation Notice Period Warning',
                    note='The resignation is approaching the notice period end date.'
                )