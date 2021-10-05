# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    customer_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                     domain="[('deprecated', '=', False), ('internal_type', '=', 'receivable')]")
    customer_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                  domain="[('deprecated', '=', False), ('internal_type', '=', 'payable')]")

    delivery_boy_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                         domain="[('deprecated', '=', False), ('internal_type', '=', 'receivable')]")
    delivery_boy_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                      domain="[('deprecated', '=', False), ('internal_type', '=', 'payable')]")

    # rezoy_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
    #                                               domain="[('deprecated', '=', False), ('internal_type', '=', 'receivable')]")
    # rezoy_payable_account_id = fields.Many2one('account.account', string="Account Payable",
    #                                            domain="[('deprecated', '=', False), ('internal_type', '=', 'payable')]")

    restaurant_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                       domain="[('deprecated', '=', False), ('internal_type', '=', 'receivable')]")
    restaurant_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                    domain="[('deprecated', '=', False), ('internal_type', '=', 'payable')]")
    order_processed_account_id = fields.Many2one('account.account', string="Order Processed(Sales)",
                                                    domain="[('deprecated', '=', False)]")
    razor_pay_payment_gateway_account_id = fields.Many2one('account.account', string="Razor Pay Account",
                                                 domain="[('deprecated', '=', False)]")
    customer_wallet_account_id = fields.Many2one('account.account', string="Customer Wallet Account",
                                                 domain="[('deprecated', '=', False)]")
    promotion_account_id = fields.Many2one('account.account', string="Promotion Account",
                                           domain="[('deprecated', '=', False)]")
    food_gst_account_id = fields.Many2one('account.account', string="Food GST Account",
                                          domain="[('deprecated', '=', False)]")
    delivery_charge_account_id = fields.Many2one('account.account', string="Delivery Charge Account",
                                                 domain="[('deprecated', '=', False)]")
    surge_account_id = fields.Many2one('account.account', string="Delivery Charge Surge Account",
                                          domain="[('deprecated', '=', False)]")
    tip_account_id = fields.Many2one('account.account', string="Tip Account",
                                          domain="[('deprecated', '=', False)]")

    yelo_first_entry_journal_id = fields.Many2one('account.journal', string="First Entry Journal",)
    yelo_second_entry_journal_id = fields.Many2one('account.journal', string="Second Entry Journal", )
    yelo_third_entry_journal_id = fields.Many2one('account.journal', string="Third Entry Journal", )

    account_delivery_charge_tax_id = fields.Many2one('account.tax', string="Default Delivery Charge Tax")
    account_surge_tax_id = fields.Many2one('account.tax', string="Default Surge Tax")
    account_commission_tax_id = fields.Many2one('account.tax', string="Default Commission Tax")
    account_tcs_tax_id = fields.Many2one('account.tax', string="Default Restaurant TCS Tax")
    account_tds_tax_id = fields.Many2one('account.tax', string="Default Restaurant TDS Tax")

