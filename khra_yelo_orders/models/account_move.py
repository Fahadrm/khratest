# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging
import json
import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    yelo_order_id = fields.Integer(string="Yelo Order Ref")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    restaurant_cost_type = fields.Selection([('food_cost', 'Food Cost'), ('gst', 'Food GST')], string='Restaurant Cost Type')
