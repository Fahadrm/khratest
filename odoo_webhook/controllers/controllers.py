# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):
    @http.route('/webhook/products', type='json', auth='public', methods=['POST'])
    def webhook(self, **post):
        header_info = request.httprequest.headers
        _logger.info('RESPONSE RECEIVED FROM YELO IS %r', header_info.environ.get('HTTP_X_YELO_TOKEN'))
        # print('post_data', post)
        # yelo_product = request.env["yelo.products"].sudo().search(
        #     [('yelo_order_id', '=', post['order_id'])])
        # if not yelo_product:
        #     request.env["yelo.products"].create({
        #         'yelo_order_id': post['order_id']
        #     })
        yelo_product = request.env["yelo.products"].sudo().search(
            [('yelo_order_id', '=', request.jsonrequest['order_id'])])
        if not yelo_product:
            request.env["yelo.products"].sudo().create({
                'yelo_order_id': request.jsonrequest['order_id']
            })
        return {}

