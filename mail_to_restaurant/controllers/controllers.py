# -*- coding: utf-8 -*-
# from odoo import http


# class MailToRestaurant(http.Controller):
#     @http.route('/mail_to_restaurant/mail_to_restaurant/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_to_restaurant/mail_to_restaurant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_to_restaurant.listing', {
#             'root': '/mail_to_restaurant/mail_to_restaurant',
#             'objects': http.request.env['mail_to_restaurant.mail_to_restaurant'].search([]),
#         })

#     @http.route('/mail_to_restaurant/mail_to_restaurant/objects/<model("mail_to_restaurant.mail_to_restaurant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_to_restaurant.object', {
#             'object': obj
#         })
