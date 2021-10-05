# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _generate_monthly_restaurant_invoice(self):
        date1 = datetime.datetime.today().date() - datetime.timedelta(days=30)
        date2 = datetime.datetime.today().date() - datetime.timedelta(days=1)
        restaurants = self.env['res.partner'].search([('partner_type', '=', 'restaurant'),
                                                      ('yelo_restaurant_id', '!=', False)])
        for restaurant in restaurants:
            monthly_payments = self.env['restaurant.payments'].search([
                ('batch_id.payment_processing_date', '>=', date1),
                ('batch_id.payment_processing_date', '<=', date2),
                ('invoice_generated', '=', False), ('partner_id', '=', restaurant.id)
            ], )
            commission_pdct = self.env['product.product'].search([('restaurant_invoice_pdct_type', '=', 'commission')], limit=1)
            tcs_pdct = self.env['product.product'].search([('restaurant_invoice_pdct_type', '=', 'tcs')],  limit=1)
            tds_pdct = self.env['product.product'].search([('restaurant_invoice_pdct_type', '=', 'tds')], limit=1)
            commission = 0
            tcs = 0
            tds = 0
            for payment in monthly_payments:
                commission += payment.commission_amt
                tcs += payment.tcs
                tds += payment.tds
            if monthly_payments:
                invoice = self.create([{
                    'partner_id': restaurant.id,
                    'move_type': 'out_invoice',
                    'invoice_line_ids': [
                        (0, 0,
                         {
                             'product_id': commission_pdct.id,
                             'price_unit': commission,
                             'tax_ids': commission_pdct.taxes_id,

                         }),
                        (0, 0,
                         {
                             'product_id': tcs_pdct.id,
                             'price_unit': tcs,
                             'tax_ids': tcs_pdct.taxes_id,
                         }),
                        (0, 0,
                         {
                             'product_id': tds_pdct.id,
                             'price_unit': tds,
                             'tax_ids': tds_pdct.taxes_id,
                         }),
                    ]
                }])
                invoice._onchange_partner_id()
                invoice._onchange_invoice_line_ids()
                invoice.action_post()
            for payment in monthly_payments:
                payment.invoice_generated = True


