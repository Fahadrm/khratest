# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    restaurant_invoice_pdct_type = fields.Selection(selection=[
        ('commission', 'Commission'),
        ('tcs', 'TCS'),
        ('tds', 'TDS'),
    ], string="Type")


