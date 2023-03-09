# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Reason(models.Model):
    _name = 'vrs.reject.reason'
    _description = 'Reason'

    name = fields.Char(required=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', _('Reason must be unique'))
    ]
