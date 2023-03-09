# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ReasonForRejection(models.Model):
    _name = 'vrs.reject.reason'
    _description = 'Reason of reject'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', _('Reason must be unique'))
    ]


class RejectedRequest(models.Model):
    _name = 'vrs.rejected.request'
    _description = 'Rejected requests'
    _rec_name = 'request_id'

    request_id = fields.Many2one('vrs.request', required=True)
    reason_id = fields.Many2one('vrs.reject.reason', required=True)
    date = fields.Date(default=fields.Date.context_today)
