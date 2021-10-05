
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RestaurantPaymentRegister(models.TransientModel):
    _name = 'restaurant.payment.register'
    _description = 'Register Restaurant Payment'

    payment_date = fields.Date(string="Payment Date", required=True,
                               default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False)
    communication = fields.Char(string="Memo", store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  compute='_compute_currency_id',
                                  help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
                                 compute='_compute_journal_id',
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account",
                                      readonly=False, store=True,
                                      compute='_compute_partner_bank_id',
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('partner_id', '=', partner_id)]")
    company_id = fields.Many2one('res.company', store=True, copy=False)
    partner_id = fields.Many2one('res.partner',
                                 string="Customer/Vendor", store=True, copy=False, ondelete='restrict')
    restaurant_payment_id = fields.Many2one(
        comodel_name='restaurant.payments',
        string='Restaurant Payment', readonly=True)

    @api.depends('company_id', 'currency_id')
    def _compute_journal_id(self):
        for wizard in self:
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ]
            journal = None
            if wizard.currency_id:
                journal = self.env['account.journal'].search(
                    domain + [('currency_id', '=', wizard.currency_id.id)], limit=1)
            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)
            wizard.journal_id = journal

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        if self._context.get('active_model') == 'restaurant.payments':
            restaurant_payment = self.env['restaurant.payments'].browse(self._context.get('active_ids', []))
            res.update({
                'amount': restaurant_payment.final_payment,
                'communication': restaurant_payment.name,
                'company_id': self.env.company.id,
                'partner_id': restaurant_payment.partner_id.id,
                'restaurant_payment_id': restaurant_payment.id,
            })
        return res

    @api.depends('partner_id')
    def _compute_partner_bank_id(self):
        ''' The default partner_bank_id will be the first available on the partner. '''
        for wizard in self:
            available_partner_bank_accounts = wizard.partner_id.bank_ids
            if available_partner_bank_accounts:
                wizard.partner_bank_id = available_partner_bank_accounts[0]._origin
            else:
                wizard.partner_bank_id = False

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.company_id.currency_id

    def action_create_payments(self):
        self.ensure_one()
        payment_vals_list = [
            {
                'date': self.payment_date,
                'amount': self.amount,
                'payment_type': 'outbound',
                'partner_type': 'customer',
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': self.partner_bank_id.id,
                'destination_account_id': self.partner_id.property_account_receivable_id.id,
                'restaurant_payment_id': self.restaurant_payment_id.id,
            }
        ]
        payments = self.env['account.payment'].create(payment_vals_list)
        payments.action_post()
        self.restaurant_payment_id.write(
            {
               'account_payment_id': payments.id,
                'payment_state': 'paid',
            })
        return payments

