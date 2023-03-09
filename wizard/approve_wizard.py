# -*- coding: utf-8 -*-

from odoo import models, fields


class ApproveWizard(models.TransientModel):
    _name = 'vrs.approve.wizard'
    _description = 'Approve request'

    check = fields.Boolean(default=False)
    request_id = fields.Many2one('vrs.request', required=True)
    reason_id = fields.Many2one('vrs.reject.reason')

    def do_action(self):
        if self.check:
            self.request_id.accept()
        else:
            self.request_id.reject()
            self.env['vrs.rejected.request'].create({
                'request_id': self.request_id.id,
                'reason_id': self.reason_id.id
            })
        return {'type': 'ir.actions.act_window_close'}
