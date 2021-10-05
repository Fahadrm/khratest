# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class AccountPayment(models.Model):
    _inherit = "account.payment"

    restaurant_payment_id = fields.Many2one(
        comodel_name='restaurant.payments',
        string='Restaurant Payment', readonly=True, ondelete='cascade')

