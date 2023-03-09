# -*- coding: utf-8 -*-

from odoo import models, fields, _
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

    requester_id = fields.Many2one('vrs.employee', required=True)
    parent_id = fields.Many2one('vrs.employee', related='requester_id.parent_id')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    comments = fields.Text()
    state = fields.Selection(_STATES, default='draft')

    _sql_constraints = [
        ('check_dates', 'check(start_date < end_date)', _('Starting date should to before end date'))
    ]


class MyRequests(models.Model):
    _name = 'vrs.request.my.requests.view'
    _description = 'My requests'
    _auto = False
    _rec_name = 'id'

    request_id = fields.Many2one('vrs.request')
    user_id = fields.Many2one('res.users')
    state = fields.Selection(_STATES)

    def init(self):
        drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                SELECT 
                    row_number() over(order by r.start_date desc) id,
                    r.id request_id,
                    e.user_id,
                    r.state
                FROM vrs_request r 
                    JOIN vrs_employee e ON e.id = r.requester_id
                    JOIN res_users u ON u.id = e.user_id
            )
            """ % (self._table,)
        )


class RequestView4Approver(models.Model):
    _name = 'vrs.request.view'
    _auto = False
    _description = 'View'
    _rec_name = 'id'

    request_id = fields.Many2one('vrs.request')
    employee_id = fields.Many2one('vrs.employee')
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
                ), employee(request_id, id, "name", start_date, end_date, "comments", parent_id, "state") as (
                    select vr.id, e.id, e."name", vr.start_date, vr.end_date, vr."comments", e.parent_id, vr.state
                    from vrs_employee e join vrs_request vr on vr.requester_id = e.id
                    where not vr.start_date is null
                )
                select row_number() over(order by sub.request_id) as id,
                    sub.request_id,
                    sub.id employee_id,
                    boss.user_id,
                    sub."name",
                    sub.start_date,
                    sub.end_date,
                    sub."comments",
                    sub.state
                from boss join employee sub on sub.parent_id = boss.id
                order by sub.start_date
            )
            """ % (self._table,)
        )

    def action_open_wizard(self):
        pass
