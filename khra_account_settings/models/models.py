# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('delivery_boy', 'Delivery Boy'),
        ('restaurant', 'Restaurant'),
    ], string="Partner Type",)
    yelo_customer_id = fields.Integer(string='Customer ID')
    yelo_restaurant_id = fields.Integer(string='Restaurant ID')
    yelo_delivery_boy_id = fields.Integer(string='Delivery Boy ID')
    restaurant_type = fields.Selection(selection=[
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ], string="Restaurant Type", default='silver')
    restaurant_commission = fields.Float(string="Commission", digits='Product Price')
    # account_properties_partner_type = fields.Boolean('Setting properties',
    #                                                  # compute='_compute_property_values'
    #                                                  )
    # property_account_payable_id = fields.Many2one('account.account',
    #                                               string="Account Payablesssss",
    #                                               domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
    #                                               help="This account will be used instead of the default one as the payable account for the current partner",
    #                                               required=False, compute='_compute_property_values', readonly=False)
    # property_account_receivable_id = fields.Many2one('account.account',
    #                                                  string="Account Receivablesssss",
    #                                                  domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
    #                                                  help="This account will be used instead of the default one as the receivable account for the current partner",
    #                                                  required=False, compute='_compute_property_values')
    #
    # @api.depends('partner_type')
    # @api.depends_context('company')
    # def _compute_property_values(self):
    #     self.ensure_one()
    #     self.account_properties_partner_type = False
    #     if self.partner_type == 'customer':
    #         self.property_account_receivable_id = self.env.company.customer_receivable_account_id
    #         self.property_account_payable_id = self.env.company.customer_payable_account_id
    #         self.account_properties_partner_type = True
    #     if self.partner_type == 'delivery_boy':
    #         self.property_account_receivable_id = self.env.company.delivery_boy_receivable_account_id
    #         self.property_account_payable_id = self.env.company.delivery_boy_payable_account_id
    #         self.account_properties_partner_type = True
    #     if self.partner_type == 'restaurant':
    #         self.property_account_receivable_id = self.env.company.restaurant_receivable_account_id
    #         self.property_account_payable_id = self.env.company.restaurant_payable_account_id
    #         self.account_properties_partner_type = True


    @api.onchange('partner_type')
    @api.depends_context('company')
    def change_account_entries(self):
        if self.partner_type == 'customer':
            self.property_account_receivable_id = self.env.company.customer_receivable_account_id
            self.property_account_payable_id = self.env.company.customer_payable_account_id
        # if self.partner_type == 'rezoy':
        #     self.property_account_receivable_id = self.env.company.rezoy_receivable_account_id
        #     self.property_account_payable_id = self.env.company.rezoy_payable_account_id
        if self.partner_type == 'delivery_boy':
            self.property_account_receivable_id = self.env.company.delivery_boy_receivable_account_id
            self.property_account_payable_id = self.env.company.delivery_boy_payable_account_id
        if self.partner_type == 'restaurant':
            self.property_account_receivable_id = self.env.company.restaurant_receivable_account_id
            self.property_account_payable_id = self.env.company.restaurant_payable_account_id




