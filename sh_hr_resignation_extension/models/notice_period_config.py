from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NoticePeriodConfig(models.Model):
    _name = 'notice.period.config'
    _description = 'Notice Period Configuration'

    name = fields.Char(string='Name', required=True)
    notice_days = fields.Integer(string='Notice Days', required=True)
    warning_days = fields.Integer(string='Warning Days', required=True)

    @api.constrains('notice_days', 'warning_days')
    def _check_days_positive(self):
        for record in self:
            if record.notice_days is not None and record.notice_days <= 0:
                raise ValidationError("Notice Days must be greater than zero.")
            if record.warning_days is not None and record.warning_days <= 0:
                raise ValidationError("Warning Days must be greater than zero.")