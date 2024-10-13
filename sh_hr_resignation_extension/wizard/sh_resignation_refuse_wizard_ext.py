from odoo import fields, models

class ShResignationRefuseWizardInherit(models.Model):
    _inherit = 'sh.resignation.refuse.wizard'

    def ref_action_ok(self):
        # Custom implementation for refusal action
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            resignation = self.env['sh.hr.resignation'].browse(active_id)
            resignation.write({
                'refused_comment': self.ref_comment,
                'refused_by': self.env.user.id,
                'state': 'refused',
            })

            # Use a new email template for the refusal notification
            template = self.env.ref(
                'sh_hr_resignation_extension.send_resignation_refused_notification_created_user_ext')
            template.send_mail(active_id, force_send=True,
                            notif_layout='mail.mail_notification_light')

            # Add a log note to the chatter without sending an email
            resignation.with_context(mail_post_autofollow=False).message_post(
                body=f"Resignation refused by {self.env.user.name}. Comment: {self.ref_comment}",
                subtype_xmlid='mail.mt_note',  # Log note type
                message_type='comment',
                partner_ids=[]
            )