# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class RequestWizard(models.TransientModel):
    _name = 'vrs.request.wizard'
    _description = 'Request'

    @api.model
    def _default_requester(self):
        _obj = self.env['vrs.employee'].sudo()
        ids = _obj.search([('user_id', '=', self.env.user.id)])
        res = ids.mapped('id')
        return res and res[0]

    requester_id = fields.Many2one('vrs.employee', default=_default_requester)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    comments = fields.Text()

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for x in self:
            if x.start_date and x.end_date and x.start_date >= x.end_date:
                raise UserError(
                    _('end date (%s) should be greater than start date (%s)', format_date(self.env, x.end_date),
                      format_date(self.env, x.start_date)))

    def do_action(self):
        vals = {
            'requester_id': self.requester_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'comments': self.comments,
        }
        # print(vals)
        _id = self.env['vrs.request'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
