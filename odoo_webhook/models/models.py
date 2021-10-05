# -*- coding: utf-8 -*-

from odoo import models, fields, api


class YeloProducts(models.Model):
    _name = 'yelo.products'
    _description = 'Yelo products'

    name = fields.Char(string='Product')
    yelo_product_id = fields.Integer(string='Yelo Product ID')
    yelo_order_id = fields.Integer(string="Yelo Order ID")


