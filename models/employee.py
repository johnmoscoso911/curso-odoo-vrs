# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Employee(models.Model):
    _name = 'vrs.employee'
    _description = 'Employee'

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', required=True)
    parent_id = fields.Many2one('vrs.employee')

    # _sql_constraints = [
    #     ('unique_name', 'unique(name)', _('Employee must be unique'))
    # ]
