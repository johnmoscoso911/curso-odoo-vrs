# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ApproveWizard(models.TransientModel):
    _name = 'vrs.approve.wizard'
    _description = 'Approve request'

    check = fields.Boolean(default=False)
    reason_id = fields.Many2one('vrs.reject.reason')
