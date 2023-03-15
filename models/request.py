# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.tools import drop_view_if_exists, format_date

_STATES = [
    ('draft', _('Draft')),
    ('accepted', _('Accepted')),
    ('rejected', _('Rejected'))
]


class Request(models.Model):
    _name = 'vrs.request'
    _description = 'Request'

    name = fields.Char(compute='_compute_name')
    requester_id = fields.Many2one('vrs.employee', required=True)
    parent_id = fields.Many2one('vrs.employee', related='requester_id.parent_id')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    comments = fields.Text()
    state = fields.Selection(_STATES, default='draft')

    _sql_constraints = [
        ('check_dates', 'check(start_date < end_date)', _('Starting date should to before end date'))
    ]

    @api.depends('requester_id.name', 'start_date', 'end_date')
    def _compute_name(self):
        for req in self:
            req.name = '%s requests vacation from (%s) to (%s)' % (
                req.requester_id.name,
                format_date(self.env, req.start_date),
                format_date(self.env, req.end_date)
            )

    def reject(self):
        self.write({'state': 'rejected'})

    def accept(self):
        self.write({'state': 'accepted'})


class MyRequests(models.Model):
    _name = 'vrs.request.my.requests.view'
    _description = 'My requests'
    _auto = False
    _rec_name = 'request_id'

    request_id = fields.Many2one('vrs.request')
    user_id = fields.Many2one('res.users')
    days = fields.Integer()
    comments = fields.Text()
    reason_desc = fields.Text(string='Reason for rejection')
    state = fields.Selection(_STATES)

    def init(self):
        drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                WITH reason(request_id, reason_desc) AS (
                    SELECT b.request_id, a.name 
                    FROM vrs_reject_reason a 
                        JOIN vrs_rejected_request b ON b.reason_id = a.id 
                )
                SELECT 
                    row_number() over(order by r.start_date desc) id,
                    r.id request_id,
                    e.user_id,
                    date_part('day', r.end_date::timestamp - r.start_date::timestamp) days,
                    r.comments,
                    x.reason_desc,
                    r.state
                FROM vrs_request r 
                    LEFT JOIN reason x ON x.request_id = r.id
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
                    sub.id as employee_id,
                    boss.user_id,
                    sub."name",
                    sub.start_date,
                    sub.end_date,
                    sub."comments",
                    sub.state
                from boss join employee sub on sub.parent_id = boss.id
                group by
                    sub.request_id,
                    sub.id,
                    boss.user_id,
                    sub."name",
                    sub.start_date,
                    sub.end_date,
                    sub."comments",
                    sub.state
                order by sub.start_date
            )
            """ % (self._table,)
        )

    def action_open_wizard(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Confirm'),
            'res_model': 'vrs.approve.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, default_request_id=self.request_id.id)
        }
        return action
