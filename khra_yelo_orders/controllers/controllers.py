# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import datetime

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):
    @http.route('/webhook/orderplaced', type='json', auth='public', methods=['POST'])
    def webhook_yelo_order_placed(self, **post):
        header_info = request.httprequest.headers
        auth_key = request.env["configure.webhook"].sudo().search([], limit=1).webhook_auth_key
        if auth_key and header_info.environ.get('HTTP_X_YELO_TOKEN') and auth_key == header_info.environ.get('HTTP_X_YELO_TOKEN'):
            _logger.info('The webhook signatures match!')
            _logger.info('RESPONSE RECEIVED FROM YELO when an order placed %r', request.jsonrequest)
            if request.jsonrequest['job_status'] == 13:
                new_date = datetime.datetime.strptime(request.jsonrequest['job_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                move_date = new_date.date()
                request.env["yelo.orders"].sudo().create({
                    'yelo_order_id': request.jsonrequest['job_id'],
                    'yelo_customer_id': request.jsonrequest['customer_id'],
                    'yelo_restaurant_id': request.jsonrequest['merchant_id'],
                    'yelo_order_type': 'pickup' if request.jsonrequest['job_type'] == 0 else 'delivery',
                    'yelo_order_status': request.jsonrequest['job_status'],
                    'yelo_order_date': move_date,
                })
        else:
            _logger.info('Warning: the webhook signatures do not match!')
        return {}
