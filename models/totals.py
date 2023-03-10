# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.tools import drop_view_if_exists


class Totals(models.Model):
    _name = 'vrs.request.total.view'
    _description = 'Totals'
    _auto = False
    _rec_name = 'id'

    employee_id = fields.Many2one('vrs.employee')
    reason_id = fields.Many2one('vrs.reject.reason')
    reason = fields.Char()
    total = fields.Integer()

    def init(self):
        drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                with rejected(request_id, reason_id, reason_desc) as (
                    select vrr.request_id, vrr2.id, vrr2.name
                    from vrs_rejected_request vrr join vrs_reject_reason vrr2 on vrr2 .id = vrr .reason_id 
                ), requests(request_id, employee_id) as (
                    select vr.id, ve.id 
                    from vrs_request vr join vrs_employee ve on ve.id = vr.requester_id 
                    where vr.state <> 'draft'
                ), accepted(employee_id, request_id) as (
                    select ve2.id, vr2.id 
                    from vrs_request vr2 join vrs_employee ve2 on ve2.id = vr2.requester_id 
                    where vr2.state = 'accepted'
                )
                select row_number() over(order by employee_id) as id,
                    employee_id, 
                    reason_id,
                    coalesce(reason_desc, '%s') as reason, 
                    count(*) as total
                from requests 
                    left join rejected using(request_id)
                    join accepted using(employee_id)
                group by employee_id, reason_id, reason_desc
            )
            """ % (self._table, _('Accepted'))
        )
