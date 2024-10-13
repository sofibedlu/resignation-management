from odoo import fields, models
from datetime import timedelta

class ShResignationApprovedWizardInherit(models.Model):
    _inherit = 'sh.resignation.approve.wizard'

    def action_ok(self):
        # Your custom implementation
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            resignation = self.env['sh.hr.resignation'].browse(active_id)
            resignation.write({
                'approved_comment': self.res_comment,
                'approved_by': self.env.user.id,
                'state': 'approve',
            })

            # Send email notification to the employee
            template = self.env.ref(
                'sh_hr_resignation_extension.send_resignation_approved_notification_created_user_ext')
            template.send_mail(active_id, force_send=True,
                               notif_layout='mail.mail_notification_light')

            # Send email notification to HR responsible persons
            hr_template = self.env.ref(
                'sh_hr_resignation_extension.send_resignation_approved_notification_hr_responsible_ext')

            partner_to = ''
            total_receipients = len(resignation.hr_responsible_ids)
            count = 1
            if resignation.hr_responsible_ids:
                for resp in resignation.hr_responsible_ids:
                    partner_to += str(resp.user_id.partner_id.id)
                    if count < total_receipients:
                        partner_to += ','
                    count += 1

            hr_template.partner_to = partner_to
            hr_template.send_mail(active_id, force_send=True,
                                  notif_layout='mail.mail_notification_light')

            # Add a log note to the chatter without sending an email
            resignation.with_context(mail_post_autofollow=False).message_post(
                body=f"Resignation approved by {self.env.user.name}. Comment: {self.res_comment}",
                subtype_xmlid='mail.mt_note',  # Log note type
                message_type='comment',
                partner_ids=[]
            )

            # Schedule activity for HR responsible persons
            self.schedule_hr_activity(resignation)

    def schedule_hr_activity(self, resignation):
        notice_days = resignation.notice_period_id.notice_days if resignation.notice_period_id else 30
        for hr_responsible in resignation.hr_responsible_ids:
            resignation.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=hr_responsible.user_id.id,
                date_deadline=(resignation.create_date + timedelta(days=notice_days)).date(),
                summary='Resignation Approved',
                note='A resignation has been approved. Please take the necessary actions.'
            )