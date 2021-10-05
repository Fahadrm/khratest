# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConfigureWebhook(models.Model):
    _name = 'configure.webhook'
    _description = 'Webhook Configuration'

    name = fields.Char(required=True, string='Name')
    webhook_auth_key = fields.Char(string="Yelo Webhook Auth Key")
    request_url = fields.Char(string="Yelo URL", required=True, default="https://api.yelo.red/open/orders/getDetails")
    api_key = fields.Char(string="Yelo Api Key", required=True)
    tookan_agent_profile_url = fields.Char(string="Tookan View Agent Profile URL", required=True, default="https://api.tookanapp.com/v2/view_fleet_profile")
    tookan_api_key = fields.Char(string="Tookan Api Key", required=True)
