# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrderLine2(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):
        res = super(SaleOrderLine2, self).product_id_change(
                pricelist, product, qty=qty, uom=uom,
                qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            	lang=lang, update_tax=update_tax, date_order=date_order, 
		packaging=packaging, fiscal_position=fiscal_position, 
                flag=flag)
        product_rec = self.env['product.product'].browse(product)
        if res.get('value', {}).get('name') and product_rec.customer_ids.ids:
            pc = product_rec.customer_ids.product_code
            pn = product_rec.customer_ids.product_name
            if pn:
                res['value']['name'] = pc + '--' + pn
        return res
