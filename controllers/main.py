# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route(['/vrs/totals'], type='json', auth='public')
    def test(self, **kwargs):
        result = request.env['vrs.request.total.view'].sudo().search([])
        return [{'reason': x.reason, 'total': x.total} for x in result]

    @http.route(['/vrs/totals/secure'], type='json', auth='user')
    def secure(self, **kwargs):
        result = request.env['vrs.request.total.view'].search([])
        return [{'reason': x.reason, 'total': x.total} for x in result]
