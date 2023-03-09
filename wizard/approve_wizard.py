# -*- coding: utf-8 -*-

from odoo import models, fields


class ApproveWizard(models.TransientModel):
    _name = 'vrs.approve.wizard'
    _description = 'Approve request'

    check = fields.Boolean(default=False)
    request_id = fields.Many2one('vrs.request', required=True)
    reason_id = fields.Many2one('vrs.reject.reason')

    def do_action(self):
        # self.env['vrs.request']
        if self.check:
            self.request_id.accept()
        else:
            self.request_id.reject()
        return {'type': 'ir.actions.act_window_close'}
