# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import base64
import xlsxwriter
from xlsxwriter.utility import xl_range


class RestaurantMailing(models.Model):
    _name = 'restaurant.mailing'
    _description = 'Mail to Restaurants'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _order = 'sent_date DESC'
    _rec_name = "subject"

    active = fields.Boolean(default=True, tracking=True)
    subject = fields.Char('Subject', help='Subject of your Mailing', required=True, translate=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    email_from = fields.Char(string='Send From', required=True,
                             default=lambda self: self.env.user.email_formatted)
    email_to = fields.Text('To', help='Message recipients (emails)')
    email_cc = fields.Char('Cc', help='Carbon copy message recipients')
    recipient_ids = fields.Many2many('res.partner', string='To (Partners)',
                                     context={'active_test': False})
    sent_date = fields.Datetime(string='Sent Date', copy=False)
    schedule_date = fields.Datetime(string='Scheduled for', tracking=True)
    body_html = fields.Text('Rich-text Contents', help="Rich-text/HTML message")
    attachment_ids = fields.Many2many('ir.attachment', 'restaurant_mailing_ir_attachments_rel',
                                      'restaurant_mailing_id', 'attachment_id', string='Attachments')
    state = fields.Selection([('draft', 'Draft'), ('in_queue', 'In Queue'), ('sending', 'Sending'), ('done', 'Sent')],
                             string='Status', required=True, tracking=True, copy=False, default='draft')
    user_id = fields.Many2one('res.users', string='Responsible', tracking=True,  default=lambda self: self.env.user)
    # Restaurant Payment Details
    partner_id = fields.Many2one('res.partner', string='Restaurant/Partner',
                                 domain="[('partner_type', '=', 'restaurant'),('yelo_restaurant_id','!=',False)]")
    yelo_restaurant_id = fields.Integer(string='Yelo Restaurant ID', related='partner_id.yelo_restaurant_id',
                                        readonly=True, store=True)
    food_cost = fields.Float(string='Food Cost', digits='Product Price')
    gst = fields.Float(string='GST', digits='Product Price')
    commission_rate = fields.Float(string='Commission Rate', digits='Product Price',
                                   related='partner_id.restaurant_commission')
    commission_amt = fields.Float(string='Commission Amount', digits='Product Price')
    final_payment = fields.Float(string='Final Payment', digits='Product Price')
    payout_start_date = fields.Date(string='Start Date', readonly=True, copy=False, store=True)
    payout_end_date = fields.Date(string='End Date', readonly=True, copy=False, store=True)
    total_orders = fields.Float(string='Total Orders', digits='Product Unit of Measure')

    def _update_payment_details(self):
        date1 = datetime.datetime.today().date() - datetime.timedelta(days=7)
        date2 = datetime.datetime.today().date() - datetime.timedelta(days=1)
        restaurant_payments = self.env['restaurant.payments'].search([
            ('batch_id.payment_processing_date', '>=', date1),
            ('batch_id.payment_processing_date', '<=', date2),
            ('payout_email', '=', False)])
        restaurant_details = {}
        restaurant_ids = []
        restaurant_data = {}
        for payments in restaurant_payments:
            if payments.partner_id.id not in restaurant_details:
                restaurant_details[payments.partner_id.id] = [{
                    'gst': payments.gst,
                    'food_cost': payments.food_cost,
                    'commission_amt': payments.commission_amt,
                    'final_payment': payments.final_payment,
                    'batch_id': payments.batch_id,
                    'payment_processing_date': payments.batch_id.payment_processing_date,
                }]
                restaurant_ids.append(payments.partner_id.id)
            else:
                restaurant_details[payments.partner_id.id].append(
                    {
                        'gst': payments.gst,
                        'food_cost': payments.food_cost,
                        'commission_amt': payments.commission_amt,
                        'final_payment': payments.final_payment,
                        'batch_id': payments.batch_id,
                        'payment_processing_date': payments.batch_id.payment_processing_date,
                    }
                )
            if payments.partner_id.id not in restaurant_data:
                restaurant_data[payments.partner_id.id] = {
                    'gst': payments.gst,
                    'food_cost': payments.food_cost,
                    'commission_amt': payments.commission_amt,
                    'final_payment': payments.final_payment,
                    'partner_id': payments.partner_id,
                    'total_orders': payments.total_orders,
                }
            else:
                restaurant_data[payments.partner_id.id]['gst'] += payments.gst
                restaurant_data[payments.partner_id.id]['food_cost'] += payments.food_cost
                restaurant_data[payments.partner_id.id]['commission_amt'] += payments.commission_amt
                restaurant_data[payments.partner_id.id]['final_payment'] += payments.final_payment
                restaurant_data[payments.partner_id.id]['total_orders'] += payments.total_orders
            payments.payout_email = True
        for key in restaurant_data:
            email_date = self.create([{
                'subject': restaurant_data[key]['partner_id'].name + " Payout",
                'email_to': restaurant_data[key]['partner_id'].email,
                'partner_id': key,
                'food_cost': restaurant_data[key]['food_cost'],
                'gst': restaurant_data[key]['gst'],
                'commission_rate': restaurant_data[key]['partner_id'].restaurant_commission,
                'commission_amt': restaurant_data[key]['commission_amt'],
                'final_payment': restaurant_data[key]['final_payment'],
                'payout_start_date': date1,
                'payout_end_date': date2,
                'total_orders': restaurant_data[key]['total_orders'],
            }])

    def action_put_in_queue(self):
        self.write({'state': 'in_queue'})

    @api.constrains('schedule_date')
    def _check_schedule_date(self):
        for record in self:
            if record.schedule_date < fields.Datetime.now():
                raise ValidationError(_('Please select a date equal/or greater than the current date.'))

    @api.model
    def _send_payment_details(self):

        mass_mailings = self.search([('state', '=', 'in_queue'), '|', ('schedule_date', '<', fields.Datetime.now()), ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            mass_mailing.state = 'sending'
            mail_to = []
            orders = []
            for recipient in mass_mailing.recipient_ids:
                mail_to.append(recipient.email)
            mail_to.append(mass_mailing.email_to)
            mass_mailing_mail_to = ",".join(mail_to)
            payments = self.env['restaurant.payments'].search([
                ('batch_id.payment_processing_date', '>=', mass_mailing.payout_start_date),
                ('batch_id.payment_processing_date', '<=', mass_mailing.payout_end_date),
                ('partner_id', '=', mass_mailing.partner_id.id)])

            for payment in payments:
                orders.append(
                    {
                        'payout_on': payment.batch_id.payment_processing_date,
                        'order_amount': payment.food_cost,
                        'payout_amount': payment.final_payment,
                        'total_orders': payment.total_orders,
                        'adjust_amt': payment.adjust_amt,
                        'revised_order_amt': payment.revised_order_amount,
                        'tax': payment.gst,
                        'commission': payment.commission_amt,
                        'commission_gst': payment.commission_gst,
                        'commission_tcs': payment.tcs,
                        'commission_tds': payment.tds,
                    }
                )
            attachments = self.create_attachment(orders, mass_mailing)
            template_id = self.env.ref('mail_to_restaurant.restaurant_weekly_payment_mail_template')
            if template_id and mass_mailing_mail_to:
                # template_id.send_mail(self.id, force_send=True)
                template_id.with_context({'email_to': mass_mailing_mail_to, 'email_cc': mass_mailing.email_cc,
                                          'orders': orders, }).\
                    send_mail(mass_mailing.id, force_send=True, raise_exception=False,
                              email_values={'attachment_ids': [attachments.id]}, notif_layout=False)
            mass_mailing.state = 'done'
            mass_mailing.attachment_ids = [(4, attachments .id)] if attachments else []

    @api.model
    def create_attachment(self, orders, mail):

        attachments = []
        workbook = xlsxwriter.Workbook('Restaurant_payment.xlsx')
        sheet1 = workbook.add_worksheet('Order Level Details')
        sheet2 = workbook.add_worksheet('Ledger Extracts')
        sheet3 = workbook.add_worksheet('Adjustment Details')
        bold = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 12})
        head = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 11, 'bg_color': '#000c66', 'border': 1, 'font_color': 'white'})
        body = workbook.add_format({'align': 'center', 'font_size': 10, 'border': 1})
        merge_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 13
        })
        # ------------ORDER LEVEL DETAILS---------------
        sheet1.hide_gridlines(2)
        if orders:
            sheet1.set_column('B:B', 20)
            sheet1.set_column('C:C', 20)
            sheet1.set_column('D:D', 20)
            sheet1.set_column('E:E', 25)
            sheet1.set_column('F:F', 20)
            sheet1.set_column('G:G', 20)
            sheet1.set_column('H:H', 20)
            sheet1.set_column('I:I', 20)
            sheet1.set_column('J:J', 20)
            sheet1.set_column('K:K', 20)
            sheet1.merge_range('B3:C3', "Order Details", merge_format)
            row = 4
            column = 1
            sheet1.write(row, 1, 'Date', head)
            sheet1.write(row, 2, 'Order Amount', head)
            sheet1.write(row, 3, 'Adjustments', head)
            sheet1.write(row, 4, 'Revised Order Amount', head)
            sheet1.write(row, 5, 'Tax', head)
            sheet1.write(row, 6, 'Commission', head)
            sheet1.write(row, 7, 'GST', head)
            sheet1.write(row, 8, 'TCS', head)
            sheet1.write(row, 9, 'TDS', head)
            sheet1.write(row, 10, 'Amount Payable', head)
            row += 1
            for order in orders:
                sheet1.write(row, 1, order['payout_on'], body)
                sheet1.write(row, 2, order['order_amount'], body)
                sheet1.write(row, 3, order['adjust_amt'], body)
                sheet1.write(row, 4, order['revised_order_amt'], body)
                sheet1.write(row, 5, order['tax'], body)
                sheet1.write(row, 6, order['commission'], body)
                sheet1.write(row, 7, order['commission_gst'], body)
                sheet1.write(row, 8, order['commission_tcs'], body)
                sheet1.write(row, 9, order['commission_tds'], body)
                sheet1.write(row, 10, order['payout_amount'], body)
                row += 1

            total_cell_range3 = xl_range(5, 3, row - 1, 3)
            total_cell_range4 = xl_range(5, 4, row - 1, 4)
            total_cell_range5 = xl_range(5, 5, row - 1, 5)
            total_cell_range6 = xl_range(5, 6, row - 1, 6)
            total_cell_range7 = xl_range(5, 7, row - 1, 7)
            total_cell_range8 = xl_range(5, 8, row - 1, 8)
            total_cell_range9 = xl_range(5, 9, row - 1, 9)
            total_cell_range10 = xl_range(5, 10, row - 1, 10)

            sheet1.write(row, 1, "", head)
            sheet1.write(row, 2, "", head)
            sheet1.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', head)
            sheet1.write(row, 4, '=SUM(' + total_cell_range4 + ')', head)
            sheet1.write(row, 5, '=SUM(' + total_cell_range5 + ')', head)
            sheet1.write(row, 6, '=SUM(' + total_cell_range6 + ')', head)
            sheet1.write(row, 7, '=SUM(' + total_cell_range7 + ')', head)
            sheet1.write(row, 8, '=SUM(' + total_cell_range8 + ')', head)
            sheet1.write(row, 9, '=SUM(' + total_cell_range9 + ')', head)
            sheet1.write(row, 10, '=SUM(' + total_cell_range10 + ')', head)

        #----------LEDGER EXTRACTS----------------
        opening_balance = self.get_opening_balance(mail)

        sheet2.hide_gridlines(2)
        sheet2.set_column('A:A', 20)
        sheet2.set_column('B:B', 20)
        sheet2.set_column('C:C', 20)
        sheet2.set_column('D:D', 20)
        sheet2.set_column('E:E', 20)
        sheet2.set_column('F:F', 20)
        sheet2.set_column('G:G', 20)
        sheet2.set_column('H:H', 20)

        sheet2.write('A1', 'Date', head)
        sheet2.write('B1', 'Order ID', head)
        sheet2.write('C1', 'Invoice No./Voucher No.', head)
        sheet2.write('D1', 'Particulars', head)
        sheet2.write('E1', 'Transaction ID', head)
        sheet2.write('F1', 'Debit', head)
        sheet2.write('G1', 'Credit', head)
        sheet2.write('H1', 'Balance', head)
        row = 1
        sheet2.write(row, 0, mail.payout_start_date - datetime.timedelta(days=1), body)
        sheet2.write(row, 1, "", body)
        sheet2.write(row, 2, "", body)
        sheet2.write(row, 3, "Opening Balance", body)
        sheet2.write(row, 4, "", body)
        sheet2.write(row, 5, "", body)
        sheet2.write(row, 6, "", body)
        sheet2.write(row, 7, opening_balance, body)
        row += 1
        for line in self.get_ledger_extracts(mail):
            sheet2.write(row, 0, line['date'], body)
            sheet2.write(row, 1, line['order_id'], body)
            sheet2.write(row, 2, "", body)
            sheet2.write(row, 3, line['particulars'], body)
            sheet2.write(row, 4, "", body)
            sheet2.write(row, 5, line['debit'], body)
            sheet2.write(row, 6, line['credit'], body)
            sheet2.write(row, 7, line['balance'], body)
            row += 1

        # ------------ADJUSTMENT DETAILS---------------
        sheet3.hide_gridlines(2)
        sheet3.set_column('A:A', 20)
        sheet3.set_column('B:B', 20)
        sheet3.set_column('C:C', 20)
        sheet3.set_column('D:D', 20)
        sheet3.set_column('E:E', 20)
        sheet3.set_column('F:F', 20)

        sheet3.write('A1', 'Adjustment Item', head)
        sheet3.write('B1', 'Previous Amount', head)
        sheet3.write('C1', 'Adjusted Amount', head)
        sheet3.write('D1', 'Revised Amount', head)
        sheet3.write('E1', 'Voucher Number', head)
        sheet3.write('F1', 'Remarks', head)
        row = 1

        for line in self.get_adjustment_details(mail):
            sheet3.write(row, 0, line['adjustment_item'], body)
            sheet3.write(row, 1, line['previous_amt'], body)
            sheet3.write(row, 2, line['adjusted_amt'], body)
            sheet3.write(row, 3, line['revised_amt'], body)
            sheet3.write(row, 4, line['voucher_no'], body)
            sheet3.write(row, 5, line['remarks'], body)
            row += 1

        workbook.close()
        fp = open('Restaurant_payment.xlsx', "rb")
        file_data = fp.read()

        attachment = self.env['ir.attachment'].create({
            'datas': base64.b64encode(file_data),
            'name': 'Restaurant_payment.xlsx',
            'type': 'binary',
            'company_id': self.env.company.id
        })

        return attachment

    @api.model
    def get_opening_balance(self, data):
        query = '''select sum(balance) as balance FROM 
            account_move_line WHERE date < %s and parent_state = 'posted' 
            and account_id = %s and partner_id = %s 
        '''
        self.env.cr.execute(query, (data.payout_start_date, data.partner_id.property_account_receivable_id.id, data.partner_id.id))
        value = 0
        for row in self.env.cr.dictfetchall():
            value = row['balance']

        return value

    @api.model
    def get_ledger_extracts(self, data):
        lines = []
        query = '''select aml.date,aml.name,aml.debit,aml.credit,aml.balance, am.yelo_order_id
            from account_move_line aml
            left join account_move am on am.id = aml.move_id
            where aml.partner_id = %s and aml.account_id = %s 
            and aml.parent_state = 'posted'
            and to_char(date_trunc('day',aml.date),'YYYY-MM-DD')::date between %s and %s '''
        self.env.cr.execute(query, (data.partner_id.id, data.partner_id.property_account_receivable_id.id,
                                    data.payout_start_date, data.payout_end_date,))
        for row in self.env.cr.dictfetchall():
            res = {
                'date': row['date'],
                'order_id': row['yelo_order_id'],
                'particulars': row['name'] if row['name'] else " ",
                'debit': row['debit'] if row['debit'] else "",
                'credit': row['credit'] if row['credit'] else "",
                'balance': row['balance'] if row['balance'] else "",
            }
            lines.append(res)
        if lines:
            return lines
        else:
            return []

    @api.model
    def get_adjustment_details(self, data):
        lines = []
        adjustment_entries = self.env['account.move.line'].search([
            ('parent_state', '=', 'posted'), ('move_id.reversed_entry_id.journal_id', '=', self.env.company.yelo_third_entry_journal_id.id),
            ('partner_id', '=', data.partner_id.id)
        ])
        for entries in adjustment_entries:
            previous_entry = self.env['account.move.line'].search([
                ('parent_state', '=', 'posted'),
                ('move_id', '=', entries.move_id.reversed_entry_id.id),
                ('partner_id', '=', data.partner_id.id)
            ])
            previous_amount = sum(line['balance'] for line in previous_entry)
            previous_amt = previous_amount if previous_amount >= 0 else previous_amount * -1
            revised_amt = previous_amt - (entries.balance if entries.balance >= 0 else entries.balance * -1)
            res = {
                'adjustment_item': entries.name,
                'previous_amt': previous_amt,
                'adjusted_amt': entries.balance if entries.balance >= 0 else entries.balance * -1,
                'revised_amt': revised_amt,
                'voucher_no': entries.move_id.name,
                'remarks': entries.move_id.narration,
            }
            lines.append(res)

        if lines:
            return lines
        else:
            return []




