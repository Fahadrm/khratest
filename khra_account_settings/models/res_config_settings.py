# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                    related='company_id.customer_receivable_account_id', readonly=False)
    customer_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                  related='company_id.customer_payable_account_id', readonly=False)

    delivery_boy_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                         related='company_id.delivery_boy_receivable_account_id', readonly=False)
    delivery_boy_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                      related='company_id.delivery_boy_payable_account_id', readonly=False)

    # rezoy_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
    #                                               related='company_id.rezoy_receivable_account_id', readonly=False)
    # rezoy_payable_account_id = fields.Many2one('account.account', string="Account Payable",
    #                                            related='company_id.rezoy_payable_account_id', readonly=False)

    restaurant_receivable_account_id = fields.Many2one('account.account', string="Account Receivable",
                                                       related='company_id.restaurant_receivable_account_id', readonly=False)
    restaurant_payable_account_id = fields.Many2one('account.account', string="Account Payable",
                                                    related='company_id.restaurant_payable_account_id', readonly=False)
    order_processed_account_id = fields.Many2one('account.account', string="Order Processed(Sales)",
                                                    related='company_id.order_processed_account_id', readonly=False)
    razor_pay_payment_gateway_account_id = fields.Many2one('account.account', string="Razor Pay Account",
                                                 related='company_id.razor_pay_payment_gateway_account_id', readonly=False)
    customer_wallet_account_id = fields.Many2one('account.account', string="Customer Wallet Account",
                                                 related='company_id.customer_wallet_account_id', readonly=False)
    promotion_account_id = fields.Many2one('account.account', string="Promotion Account",
                                           related='company_id.promotion_account_id', readonly=False)
    food_gst_account_id = fields.Many2one('account.account', string="Food GST Account",
                                          related='company_id.food_gst_account_id', readonly=False)
    delivery_charge_account_id = fields.Many2one('account.account', string="Delivery Charge Account",
                                                 related='company_id.delivery_charge_account_id', readonly=False)
    surge_account_id = fields.Many2one('account.account', string="Delivery Charge Surge Account",
                                       related='company_id.surge_account_id', readonly=False)
    tip_account_id = fields.Many2one('account.account', string="Tip Account",
                                     related='company_id.tip_account_id', readonly=False)

    yelo_first_entry_journal_id = fields.Many2one('account.journal', string="First Entry Journal",
                                                 related='company_id.yelo_first_entry_journal_id', readonly=False)
    yelo_second_entry_journal_id = fields.Many2one('account.journal', string="Second Entry Journal",
                                                  related='company_id.yelo_second_entry_journal_id', readonly=False)
    yelo_third_entry_journal_id = fields.Many2one('account.journal', string="Third Entry Journal",
                                                  related='company_id.yelo_third_entry_journal_id', readonly=False)

    delivery_charge_tax_id = fields.Many2one('account.tax', string="Default Delivery Charge Tax",
                                             related='company_id.account_delivery_charge_tax_id', readonly=False)
    surge_tax_id = fields.Many2one('account.tax', string="Default Surge Tax", related='company_id.account_surge_tax_id',
                                   readonly=False)
    commission_tax_id = fields.Many2one('account.tax', string="Default Commission Tax",
                                        related='company_id.account_commission_tax_id', readonly=False)
    tcs_tax_id = fields.Many2one('account.tax', string="Default Restaurant TCS Tax",
                                        related='company_id.account_tcs_tax_id', readonly=False)
    tds_tax_id = fields.Many2one('account.tax', string="Default Restaurant TDS Tax",
                                            related='company_id.account_tds_tax_id', readonly=False)

