# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import SingleTransactionCase
import random


class TestUpdateprice(SingleTransactionCase):

    # number of lines that will be generated
    lines_to_sync = 8

    # number of line that will be changed
    lines_to_change = 3

    def AssertInvoiceState(self, reg, cr, uid, invoice):
        # invoice must be in draft
        state = self.registry('account.invoice').read(
            self.cr, self.uid, invoice, ['state'])['state']
        assert state == 'draft', 'state is not in draft'

    def setup_invoice(self, reg, cr, uid):
        self.invoice_id = reg('account.invoice').create(
            cr, uid, {
                'account_id': 1,
                'company_id': 1,
                'currency_id': 1,
                'journal_id': 1,
                'partner_id': 1,
                'reference_type': 'none',
                })

        for i in range(self.lines_to_sync-1):
            reg('account.invoice.line').create(
                cr, uid, {
                    'invoice_id': self.invoice_id,
                    'account_id': 1,
                    'name': 'TEST LINE ' + str(i),
                    'price_unit': 450.0,
                    'quantity': 1.0,
                    'product_id': 1,
                    'uos_id': 1,
                    })
        return self.invoice_id

    # check if prices are saved correctly

    def check_update_price(self, reg, cr, uid, invoice):

        # check if the update price object has been created
        # with the right values and call the wizard
        invoice_model = reg('account.invoice')
        invoice_obj = invoice_model.browse(cr, uid, [invoice])[0]
        updateprice = invoice_model.generate_lines(cr, uid, [invoice])
        updateprice_obj = reg('account.invoice.updateprice').browse(
            cr, uid, [updateprice['res_id']])[0]

        # check that all the invoice lines are in updateprice
        assert (len(invoice_obj.invoice_line) == len(
            updateprice_obj.update_price_line_ids)), \
            'not all invoice lines are in update screen'

        # put a random price in the first n lines
        for i in range(self.lines_to_change-1):
            updateprice_obj.update_price_line_ids[i].new_price = \
                random.uniform(0, 1000)
        updateprice_obj.save_new_prices()

        # checking that the values have been returned to the invoice
        for invoice_line in invoice_obj.invoice_line:
            for price_line in updateprice_obj.update_price_line_ids:
                if (price_line.product_id ==
                        invoice_line.product_id) and price_line.new_price != 0:
                    assert price_line.new_price == \
                        invoice_line.price_unit, 'invoice updated incorrectly'

    def test_all(self):
        reg, cr, uid, = self.registry, self.cr, self.uid
        invoice = self.setup_invoice(reg, cr, uid)
        self.check_update_price(reg, cr, uid, invoice)
