# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools import drop_view_if_exists

_STATES = [
    ('draft', _('Draft')),
    ('accepted', _('Accepted')),
    ('rejected', _('Rejected'))
]


class Request(models.Model):
    _name = 'vrs.request'
    _description = 'Request'
    _rec_name = 'requester_id'

    @api.model
    def _default_requester(self):
        _obj = self.env['vrs.employee'].sudo()
        ids = _obj.search([('user_id', '=', self.env.user.id)])
        res = ids.mapped('id')
        return res and res[0]

    # name = fields.Char(required=True, translate=True, help='The description')
    requester_id = fields.Many2one('vrs.employee', default=_default_requester)
    parent_id = fields.Many2one('vrs.employee', related='requester_id.parent_id')
    start_date = fields.Date()
    end_date = fields.Date()
    comments = fields.Text()
    state = fields.Selection(_STATES, default='draft')

    _sql_constraints = [
        ('check_dates', 'check(start_date < end_date)', _('Starting date should to before end date'))
    ]

    @api.model
    def create(self, vals):
        print(vals)
        x = super(Request, self).create(vals)
        return x


class RequestView4Approver(models.Model):
    _name = 'vrs.request.view'
    _auto = False
    _description = 'View'
    _rec_name = 'id'

    request_id = fields.Many2one('vrs.request')
    user_id = fields.Many2one('res.users')
    name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    comments = fields.Text()
    state = fields.Selection(_STATES)

    def init(self):
        drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                with boss(user_id, id) as (
                    select u.id, b.id
                    from res_users u
                    join vrs_employee b join vrs_employee s on s.parent_id = b.id
                        on b.user_id = u.id
                ), employee(request_id, n, sd, ed, c, p, state) as (
                    select vr.id, e."name", vr.start_date, vr.end_date, vr."comments", e.parent_id, vr.state
                    from vrs_employee e join vrs_request vr on vr.requester_id = e.id
                    where not vr.start_date is null
                )
                select row_number() over(order by employee.n) as id,
                    request_id,
                    boss.user_id,
                    employee.n "name",
                    employee.sd start_date,
                    employee.ed end_date,
                    employee.c comments,
                    employee.state
                from boss join employee on employee.p = boss.id
                order by employee.sd
            )
            """ % (self._table,)
        )

    def action_open_wizard(self):
        pass
