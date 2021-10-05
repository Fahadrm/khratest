# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class RestaurantPayments(models.Model):
    _inherit = 'restaurant.payments'

    invoice_generated = fields.Boolean(string='Invoice Generated', default=False)


