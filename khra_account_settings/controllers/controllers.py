# -*- coding: utf-8 -*-
# from odoo import http


# class KhraAccountSettings(http.Controller):
#     @http.route('/khra_account_settings/khra_account_settings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/khra_account_settings/khra_account_settings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('khra_account_settings.listing', {
#             'root': '/khra_account_settings/khra_account_settings',
#             'objects': http.request.env['khra_account_settings.khra_account_settings'].search([]),
#         })

#     @http.route('/khra_account_settings/khra_account_settings/objects/<model("khra_account_settings.khra_account_settings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('khra_account_settings.object', {
#             'object': obj
#         })
