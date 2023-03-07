# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Request(models.Model):
    _name = 'vrs.request'
    _description = 'Request'
    _rec_name = 'requester_id'

    @api.model
    def _default_requester(self):
        _obj = self.env['vrs.employee'].sudo()
        print(self.env.user)
        ids = _obj.search([('user_id', '=', self.env.user)])
        res = ids.mapped('id')  # _obj.browse(ids)
        print(res)
        return res and res[0].id

    # name = fields.Char(required=True, translate=True, help='The description')
    requester_id = fields.Many2one('vrs.employee', default=_default_requester)
    parent_id = fields.Many2one('vrs.employee', related='requester_id.parent_id')

    # _sql_constraints = [
    #     ('unique_name', 'unique(name)', _('Request must be unique'))
    # ]
