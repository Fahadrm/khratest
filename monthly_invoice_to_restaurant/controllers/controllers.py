# -*- coding: utf-8 -*-
# from odoo import http


# class MonthlyInvoiceToRestaurant(http.Controller):
#     @http.route('/monthly_invoice_to_restaurant/monthly_invoice_to_restaurant/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/monthly_invoice_to_restaurant/monthly_invoice_to_restaurant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('monthly_invoice_to_restaurant.listing', {
#             'root': '/monthly_invoice_to_restaurant/monthly_invoice_to_restaurant',
#             'objects': http.request.env['monthly_invoice_to_restaurant.monthly_invoice_to_restaurant'].search([]),
#         })

#     @http.route('/monthly_invoice_to_restaurant/monthly_invoice_to_restaurant/objects/<model("monthly_invoice_to_restaurant.monthly_invoice_to_restaurant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('monthly_invoice_to_restaurant.object', {
#             'object': obj
#         })
