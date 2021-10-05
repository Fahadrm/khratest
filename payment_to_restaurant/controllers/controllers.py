# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentToRestaurant(http.Controller):
#     @http.route('/payment_to_restaurant/payment_to_restaurant/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_to_restaurant/payment_to_restaurant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_to_restaurant.listing', {
#             'root': '/payment_to_restaurant/payment_to_restaurant',
#             'objects': http.request.env['payment_to_restaurant.payment_to_restaurant'].search([]),
#         })

#     @http.route('/payment_to_restaurant/payment_to_restaurant/objects/<model("payment_to_restaurant.payment_to_restaurant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_to_restaurant.object', {
#             'object': obj
#         })
