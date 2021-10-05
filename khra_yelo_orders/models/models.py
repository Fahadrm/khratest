# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import logging
import json
import datetime

_logger = logging.getLogger(__name__)


class YeloOrders(models.Model):
    _name = 'yelo.orders'
    _rec_name = 'yelo_order_id'
    _description = 'Yelo Orders'

    yelo_customer_id = fields.Integer(string='Customer ID', required=True)
    yelo_restaurant_id = fields.Integer(string='Restaurant ID', required=True)
    yelo_order_id = fields.Integer(string="Order ID", required=True)
    yelo_order_status = fields.Integer(string="Order Status")
    yelo_order_type = fields.Selection([
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ], string="Order Type")
    yelo_order_date = fields.Date(string='Order Date', index=True)
    sync_status = fields.Boolean(string='Sync status', default=False)
    customer_order_entry_status = fields.Boolean(string='Customer Order Entry status', default=False)
    payment_type_status = fields.Boolean(string='Payment Type Entry status', default=False)
    restaurant_entry_status = fields.Boolean(string='Restaurant Entry status', default=False)
    invoice_status = fields.Boolean(string='Invoice status', default=False)

    @api.model
    def _yelo_order_sync(self):
        # pass
        records = self.search([
            ('sync_status', '=', False)
        ])
        for record in records:
            webhook = self.env["configure.webhook"].search([], limit=1)
            url = webhook.request_url
            api_key = webhook.api_key
            tookan_url = webhook.tookan_agent_profile_url
            tookan_api_key = webhook.tookan_api_key
            # payload = "{\r\n    \"api_key\"   :\" %s\" ,\r\n    \"job_id\"    : %d \r\n}" % (api_key, record.yelo_order_id)
            # headers = {"Content-Type": "application/x-www-form-urlencoded"}
            todo = {"api_key": api_key, "job_id": record.yelo_order_id}

            # response = requests.request("POST", url, headers=headers, data=payload)
            # _logger.info('RESPONSE RECEIVED FROM YELO when an order placed %r', response.text)

            headers = {"Content-type": "application/json",
                       'Accept': 'text/plain'}
            req = requests.post(url, data=json.dumps(todo), headers=headers)
            req.raise_for_status()
            data_received = req.json()
            for data in data_received['data']:
                restaurant = self.env['res.partner'].search([('yelo_restaurant_id', '=', data['merchant_id']), ('partner_type', '=', "restaurant")])
                customer = self.env['res.partner'].search([('yelo_customer_id', '=', data['customer_id']), ('partner_type', '=', "customer")])
                rider = self.env['res.partner'].search([('yelo_delivery_boy_id', '=', data['agent_id']), ('partner_type', '=', "delivery_boy")])
                if not restaurant:
                    restaurant = self.env['res.partner'].create({
                        'name': data['merchant_name'],
                        'partner_type': 'restaurant',
                        'yelo_restaurant_id': data['merchant_id'],
                        'phone': data['merchant_phone_number'],
                        'email': data['merchant_email'],
                        'property_account_receivable_id': self.env.company.restaurant_receivable_account_id.id,
                        'property_account_payable_id': self.env.company.restaurant_payable_account_id.id,
                    })
                if not customer:
                    customer = self.env['res.partner'].create({
                        'name': data['customer_username'],
                        'partner_type': 'customer',
                        'yelo_customer_id': data['customer_id'],
                        'phone': data['customer_phone'],
                        'email': data['customer_email'],
                        'property_account_receivable_id': self.env.company.customer_receivable_account_id.id,
                        'property_account_payable_id': self.env.company.customer_payable_account_id.id,
                    })
                if not rider:
                    tookan_todo = {"api_key": tookan_api_key, "fleet_id": data['agent_id']}
                    tookan_response = requests.post(tookan_url, data=json.dumps(tookan_todo), headers=headers)
                    received_agent_data = tookan_response.json()
                    for agent_data in received_agent_data['data']['fleet_details']:
                        rider = self.env['res.partner'].create({
                            'name': agent_data['username'],
                            'partner_type': 'delivery_boy',
                            'yelo_delivery_boy_id': data['agent_id'],
                            'phone': agent_data['phone'],
                            'email': agent_data['email'],
                            'property_account_receivable_id': self.env.company.delivery_boy_receivable_account_id.id,
                            'property_account_payable_id': self.env.company.delivery_boy_payable_account_id.id,
                        })
                delivery_charge_tax = self.env.company.account_delivery_charge_tax_id.compute_all(data['delivery_charge'], quantity=1)
                surge_tax = self.env.company.account_delivery_charge_tax_id.compute_all(data['delivery_charge_surge_amount'], quantity=1)

                new_date = datetime.datetime.strptime(data['job_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                move_date = new_date.date()
                first_entry_move = self.env['account.move'].create({
                    'date': move_date,
                    'journal_id': self.env.company.yelo_first_entry_journal_id.id,
                    'company_id': self.env.company.id,
                    'user_id': self.env.user.id,
                    'yelo_order_id': record.yelo_order_id,
                    'line_ids': [
                        (0, 0,
                            {
                                'account_id': customer.property_account_receivable_id.id,
                                'name': "Customer Control A/c Sub A/c ( " + customer.name + " A/c)",
                                'debit': data['total_amount'],
                                'credit': 0,
                                'currency_id': self.env.company.currency_id.id,
                                'partner_id': customer.id,
                            }),
                        (0, 0,
                            {
                                'account_id': self.env.company.order_processed_account_id.id,
                                'name': "Order Processed (Sales)",
                                'debit': 0,
                                'credit': data['total_amount'],
                                'currency_id': self.env.company.currency_id.id
                            })
                    ]
                })
                first_entry_move.post()
                record.customer_order_entry_status = True
                if data['payment_type'] == 'CASH':
                    second_entry_move = self.env['account.move'].create({
                        'date': move_date,
                        'journal_id': self.env.company.yelo_second_entry_journal_id.id,
                        'company_id': self.env.company.id,
                        'user_id': self.env.user.id,
                        'yelo_order_id': record.yelo_order_id,
                        'line_ids': [
                            (0, 0,
                                {
                                    'account_id': rider.property_account_receivable_id.id,
                                    'name': "Rider Control A/c Sub A/c ( " + rider.name + " A/c)",
                                    'debit': data['total_amount'],
                                    'credit': 0,
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': rider.id,
                                }),
                            (0, 0,
                                {
                                    'account_id': customer.property_account_receivable_id.id,
                                    'name': "Customer Control A/c Sub A/c ( " + customer.name + " A/c)",
                                    'debit': 0,
                                    'credit': data['total_amount'],
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': customer.id,
                                })
                         ]
                    })
                    second_entry_move.post()
                    record.payment_type_status = True
                if data['payment_type'] == 'RAZORPAY':
                    second_entry_move = self.env['account.move'].create({
                        'date': move_date,
                        'journal_id': self.env.company.yelo_second_entry_journal_id.id,
                        'company_id': self.env.company.id,
                        'user_id': self.env.user.id,
                        'yelo_order_id': record.yelo_order_id,
                        'line_ids': [
                            (0, 0,
                                {
                                    'account_id': self.env.company.razor_pay_payment_gateway_account_id.id,
                                    'name': "Razor pay Payment Gateway A/c",
                                    'debit': data['total_amount'],
                                    'credit': 0,
                                    'currency_id': self.env.company.currency_id.id
                                }),
                            (0, 0,
                                {
                                    'account_id': customer.property_account_receivable_id.id,
                                    'name': "Customer Control A/c Sub A/c ( " + customer.name + " A/c)",
                                    'debit': 0,
                                    'credit': data['total_amount'],
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': customer.id,
                                })
                        ]
                    })
                    second_entry_move.post()
                    record.payment_type_status = True
                if data['payment_type'] == 'WALLET':
                    second_entry_move1 = self.env['account.move'].create({
                        'date': move_date,
                        'journal_id': self.env.company.yelo_second_entry_journal_id.id,
                        'company_id': self.env.company.id,
                        'user_id': self.env.user.id,
                        'yelo_order_id': record.yelo_order_id,
                        'line_ids': [
                            (0, 0,
                                {
                                    'account_id': self.env.company.razor_pay_payment_gateway_account_id.id,
                                    'name': "Razor pay Payment Gateway A/c",
                                    'debit': data['total_amount'],
                                    'credit': 0,
                                    'currency_id': self.env.company.currency_id.id
                                }),
                            (0, 0,
                                {
                                    'account_id': self.env.company.customer_wallet_account_id.id,
                                    'name': "Customer Wallet A/c",
                                    'debit': 0,
                                    'credit': data['total_amount'],
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': customer.id,
                                })
                        ]
                    })
                    second_entry_move1.post()
                    second_entry_move2 = self.env['account.move'].create({
                        'date': move_date,
                        'journal_id': self.env.company.yelo_second_entry_journal_id.id,
                        'company_id': self.env.company.id,
                        'user_id': self.env.user.id,
                        'yelo_order_id': record.yelo_order_id,
                        'line_ids': [
                            (0, 0,
                                {
                                    'account_id': self.env.company.customer_wallet_account_id.id,
                                    'name': "Customer Wallet A/c",
                                    'debit': data['total_amount'],
                                    'credit': 0,
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': customer.id,
                                }),
                            (0, 0,
                                {
                                    'account_id': customer.property_account_receivable_id.id,
                                    'name': "Customer Control A/c Sub A/c ( " + customer.name + " A/c)",
                                    'debit': 0,
                                    'credit': data['total_amount'],
                                    'currency_id': self.env.company.currency_id.id,
                                    'partner_id': customer.id,
                                })
                        ]
                    })
                    second_entry_move2.post()
                    record.payment_type_status = True
                promo_discount = 0
                for promo in data["promoList"]:
                    promo_discount += promo["promo_discount"]
                third_move_line_datas = [
                    (0, 0,
                     {
                         'account_id': self.env.company.order_processed_account_id.id,
                         'name': "To Order Processed (Sales)",
                         'debit': data['total_amount'],
                         'credit': 0,
                         'currency_id': self.env.company.currency_id.id,
                     }),
                    (0, 0,
                     {
                         'account_id': self.env.company.promotion_account_id.id,
                         'name': "Promotion applied",
                         'debit': promo_discount,
                         'credit': 0,
                         'currency_id': self.env.company.currency_id.id
                     }),
                    (0, 0,
                     {
                         'account_id': restaurant.property_account_receivable_id.id,
                         'name': "Restaurant control A/c Sub A/c - " + restaurant.name + " A/c",
                         'debit': 0,
                         'credit': data['order_amount'],
                         'currency_id': self.env.company.currency_id.id,
                         'restaurant_cost_type': 'food_cost',
                         'partner_id': restaurant.id,
                     }),
                    (0, 0,
                     {
                         'account_id': self.env.company.food_gst_account_id.id,
                         'name': "Food GST A/c",
                         'debit': 0,
                         'credit': data['tax'],
                         'currency_id': self.env.company.currency_id.id
                     }),
                    (0, 0,
                     {
                         'account_id': self.env.company.delivery_charge_account_id.id,
                         'name': "Delivery Charge received (by " + rider.name + " )",
                         'debit': 0,
                         'credit': delivery_charge_tax['total_excluded'],
                         'currency_id': self.env.company.currency_id.id
                     }),
                    (0, 0,
                     {
                         'account_id': self.env.company.tip_account_id.id,
                         'name': "Tip received for (by " + rider.name + " )",
                         'debit': 0,
                         'credit': data['tip'],
                         'currency_id': self.env.company.currency_id.id
                     }),
                    (0, 0,
                     {
                         'account_id': self.env.company.surge_account_id.id,
                         'name': "Delivery sur charge received (by " + rider.name + " )",
                         'debit': 0,
                         'credit': surge_tax['total_excluded'],
                         'currency_id': self.env.company.currency_id.id
                     }),
                ]
                for tax in delivery_charge_tax['taxes']:
                    third_move_line_datas.append(
                        (0, 0,
                         {
                             'account_id': tax['account_id'],
                             'name': tax['name'],
                             'debit': 0,
                             'credit': tax['amount'],
                             'currency_id': self.env.company.currency_id.id,
                         }),
                    )

                for tax in surge_tax['taxes']:
                    third_move_line_datas.append(
                        (0, 0,
                         {
                             'account_id': tax['account_id'],
                             'name': tax['name'],
                             'debit': 0,
                             'credit': tax['amount'],
                             'currency_id': self.env.company.currency_id.id,
                         }),
                    )

                third_entry_move1 = self.env['account.move'].create({
                    'date': move_date,
                    'journal_id': self.env.company.yelo_third_entry_journal_id.id,
                    'company_id': self.env.company.id,
                    'user_id': self.env.user.id,
                    'yelo_order_id': record.yelo_order_id,
                    'line_ids': third_move_line_datas,
                })
                #     'line_ids': [
                #         (0, 0,
                #             {
                #                 'account_id': self.env.company.order_processed_account_id.id,
                #                 'name': "To Order Processed (Sales)",
                #                 'debit': data['total_amount'],
                #                 'credit': 0,
                #                 'currency_id': self.env.company.currency_id.id,
                #             }),
                #         (0, 0,
                #             {
                #                 'account_id': self.env.company.promotion_account_id.id,
                #                 'name': "Promotion applied",
                #                 'debit': promo_discount,
                #                 'credit': 0,
                #                 'currency_id': self.env.company.currency_id.id
                #             }),
                #         (0, 0,
                #          {
                #              'account_id': restaurant.property_account_receivable_id.id,
                #              'name': "Restaurant control A/c Sub A/c - " + restaurant.name + " A/c",
                #              'debit': 0,
                #              'credit': data['order_amount'],
                #              'currency_id': self.env.company.currency_id.id,
                #              'restaurant_cost_type': 'food_cost',
                #              'partner_id': restaurant.id,
                #          }),
                #         (0, 0,
                #          {
                #              'account_id': self.env.company.food_gst_account_id.id,
                #              'name': "Food GST A/c",
                #              'debit': 0,
                #              'credit': data['tax'],
                #              'currency_id': self.env.company.currency_id.id
                #          }),
                #         (0, 0,
                #          {
                #              'account_id': self.env.company.delivery_charge_account_id.id,
                #              'name': "Delivery Charge received (by " + rider.name + " )",
                #              'debit': 0,
                #              'credit': delivery_charge_tax['total_excluded'],
                #              'currency_id': self.env.company.currency_id.id
                #          }),
                #         (0, 0,
                #          {
                #              'account_id': self.env.company.tip_account_id.id,
                #              'name': "Tip received for (by " + rider.name + " )",
                #              'debit': 0,
                #              'credit': data['tip'],
                #              'currency_id': self.env.company.currency_id.id
                #          }),
                #         (0, 0,
                #          {
                #              'account_id': self.env.company.surge_account_id.id,
                #              'name': "Delivery sur charge received (by " + rider.name + " )",
                #              'debit': 0,
                #              'credit': surge_tax['total_excluded'],
                #              'currency_id': self.env.company.currency_id.id
                #          }),
                #     ]
                # })
                # for tax in delivery_charge_tax['taxes']:
                #     self.env['account.move.line'].create({
                #         'account_id': tax['account_id'],
                #         'name': tax['name'],
                #         'debit': 0,
                #         'credit': tax['amount'],
                #         'currency_id': self.env.company.currency_id.id,
                #         'move_id': third_entry_move1.id,
                #     })
                # for tax in surge_tax['taxes']:
                #     self.env['account.move.line'].create({
                #         'account_id': tax['account_id'],
                #         'name': tax['name'],
                #         'debit': 0,
                #         'credit': tax['amount'],
                #         'currency_id': self.env.company.currency_id.id,
                #         'move_id': third_entry_move1.id,
                #     })
                third_entry_move1.post()
                third_entry_move2 = self.env['account.move'].create({
                    'date': move_date,
                    'journal_id': self.env.company.yelo_third_entry_journal_id.id,
                    'company_id': self.env.company.id,
                    'user_id': self.env.user.id,
                    'yelo_order_id': record.yelo_order_id,
                    'line_ids': [
                        (0, 0,
                         {
                             'account_id': self.env.company.food_gst_account_id.id,
                             'name': "Food GST A/c",
                             'debit': data['tax'],
                             'credit': 0,
                             'currency_id': self.env.company.currency_id.id,
                             'partner_id': customer.id,
                         }),
                        (0, 0,
                         {
                             'account_id': restaurant.property_account_receivable_id.id,
                             'name': restaurant.name + " A/c)",
                             'debit': 0,
                             'credit': data['tax'],
                             'restaurant_cost_type': 'gst',
                             'currency_id': self.env.company.currency_id.id,
                             'partner_id': restaurant.id,
                         })
                    ]
                })
                third_entry_move2.post()
                record.restaurant_entry_status = True
            record.update({
                'sync_status': True
            })
            _logger.info('RESPONSE RECEIVED FROM YELO DURING API CALL - GET ORDER DETAILS %r', data_received['data'])
