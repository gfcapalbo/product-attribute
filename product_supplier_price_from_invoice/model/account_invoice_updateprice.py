# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
from openerp.osv import fields, orm


class Invoice(orm.Model):
    _inherit = 'account.invoice'

    def generate_lines(self, cr, uid, ids, context=None):
        """
        Create a wizard and lines on the wizard for all invoice
        lines of this invoice with a product on them.
        """
        invoice = self.pool.get('account.invoice').browse(
            cr, uid, ids[0], context=context)
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        pricelistinfo_obj = self.pool.get('pricelist.partnerinfo')
        price_wizard_obj = self.pool.get('account.invoice.updateprice')
        price_wizard_id = price_wizard_obj.create(
            cr, uid, {'account_invoice_id': invoice.id}, context=context)
        line_obj = self.pool.get('account.invoice.line')
        line_ids = line_obj.search(
            cr, uid, [
                ('invoice_id', '=', invoice.id),
                ('product_id', '!=', False),
                ], context=context)
        lines = line_obj.browse(cr, uid, line_ids, context=context)
        for line in lines:
            #  get current supplier price
            info_ids = supplierinfo_obj.search(
                cr, uid, [
                    ('product_id', '=', line.product_id.product_tmpl_id.id),
                    ('name', '=', invoice.partner_id.id),
                    ('qty', '=', 1.00)
                    ], context=context)
            if len(info_ids) > 0:
                for supplierinfo in supplierinfo_obj.browse(cr, uid, info_ids):
                    chosen_pricelist_id = pricelistinfo_obj.search(
                        cr, uid, [
                            ('suppinfo_id', '=', supplierinfo.id)
                        ], context=context)
                    supplier_price = pricelistinfo_obj.browse(
                        cr, uid, chosen_pricelist_id)[0].price
            else:
                supplier_price = 0
            var = {
                'updateprice_id': price_wizard_id,
                'product_id': line.product_id.id,
                'supplier_price': supplier_price,
                'invoice_price': line.price_unit,
                'new_price': 0.0
                }
            self.pool['account.invoice.updateprice.line'].create(
                cr, uid, var, context=context)

        return {
            'view_mode': 'form',
            'res_model': 'account.invoice.updateprice',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'res_id': price_wizard_id
            }


class UpdatePriceLine(orm.TransientModel):

    _name = 'account.invoice.updateprice.line'
    _description = 'update price lines'
    _columns = {
        'updateprice_id': fields.many2one('account.invoice.updateprice'),
        'product_id': fields.many2one('product.product', 'Product name'),
        'invoice_price': fields.float(
            'Invoice price',
            help="Price you have just received in the invoice"),
        'supplier_price': fields.float(
            'Supplier price ',
            help="Price already saved in your product"),
        'new_price': fields.float(
            'New price',
            help="New price you will want to set in the product")
        }


class UpdatePrice(orm.TransientModel):

    _name = 'account.invoice.updateprice'
    _description = 'Update Prices on this invoice'

    def _get_partner_id(self, cr, uid, ids, field_name, args, context=None):
        """
        The invoiced partner can be another partner than the purchase
        partner. Supplier pricelists don't generalize within the same
        partner, but are only retrieved by contact. As a workaround, take
        the partner from the related purchase if any as a best guess.
        If no purchase order can be found, pick the commercial partner
        over an invoice partner.
        """
        purchase_obj = self.pool['purchase.order']
        res = {}
        for wiz in self.browse(cr, uid, ids, context=context):
            purchase_ids = purchase_obj.search(
                cr, uid, [('invoice_ids', '=', wiz.account_invoice_id.id)],
                context=context)
            if purchase_ids:
                purchase = purchase_obj.browse(
                    cr, uid, purchase_ids[0], context=context)
                res[wiz.id] = purchase.partner_id.id
                print purchase.partner_id.name
            else:
                partner = wiz.account_invoice_id.partner_id
                if partner.type == 'invoice':
                    partner = partner.commercial_partner_id
                res[wiz.id] = partner.id
        return res

    _columns = {
        'update_price_line_ids': fields.one2many(
            'account.invoice.updateprice.line', 'updateprice_id'),
        'account_invoice_id': fields.many2one(
            'account.invoice',
            'The invoice this object has been generated from',
            required=True),
        'partner_id': fields.function(
            _get_partner_id, type='many2one', relation='res.partner',
            string='Supplier'),
        'supplier_name': fields.related(
            'partner_id', 'name', type='char', size=256,
            string='Supplier name', readonly=True),
    }
    _defaults = {}

    def save_new_prices(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)[0]
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        pricelistinfo_obj = self.pool.get('pricelist.partnerinfo')
        invoiceline_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        for line in wizard.update_price_line_ids:
            if line.new_price == 0:
                continue
            product = line.product_id
            info_ids = supplierinfo_obj.search(cr, uid, [
                ('product_id', '=', product.product_tmpl_id.id),
                ('name', '=',
                 wizard.partner_id.id),
            ], context=context)
            # supplier exists just change or add pricelists
            if info_ids:
                supplierinfo_id = info_ids[0]
            else:
                vals_si = {
                    'product_id': product.product_tmpl_id.id,
                    'name': wizard.partner_id.id,
                    'min_qty': 1.00,
                    'delay': 0
                    }
                supplierinfo_id = supplierinfo_obj.create(
                    cr, uid, vals_si, context=context)
            # Get all the pricelists with min quantity lower
            # than invoice quantity
            pricelist_ids = pricelistinfo_obj.search(
                cr, uid, [
                    ('suppinfo_id', '=', supplierinfo_id),
                    ('min_quantity', '=', 1)
                    ], context=context)
            # change first pricelist
            if pricelist_ids:
                pricelistinfo_obj.write(
                    cr, uid, pricelist_ids[0],
                    {'price': line.new_price}, context=context)
                pricelistinfo_obj.unlink(
                    cr, uid, pricelist_ids[1:], context=context)
            # no pricelists for q=1 exist create new pricelist
            else:
                vals_pi = {
                    'name': 'price for ' + str(product.name),
                    'price': line.new_price,
                    'min_quantity': 1.00,
                    'qty': 1.00,
                    'suppinfo_id': supplierinfo_id
                    }
                pricelistinfo_obj.create(
                    cr, uid, vals_pi, context=context)

            # Update prices on this invoice's line(s)
            invoice_line_ids = invoiceline_obj.search(
                cr, uid, [
                    ('product_id', '=', product.id),
                    ('invoice_id', '=', wizard.account_invoice_id.id),
                    ], context=context)
            invoiceline_obj.write(
                cr, uid, invoice_line_ids, {
                    'price_unit': line.new_price
                    }, context=context)

        return invoice_obj.button_reset_taxes(
            cr, uid, [wizard.account_invoice_id.id], context=context)
