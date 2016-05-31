# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):
        res = super(SaleOrderLine, self).product_id_change(
                pricelist, product, qty=qty, uom=uom,
                qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            	lang=lang, update_tax=update_tax, date_order=date_order, 
		packaging=packaging, fiscal_position=fiscal_position, 
                flag=flag)
        product_rec = self.env['product.product'].browse(product)
        partner_rec = self.env['res.partner'].browse(partner_id)
        if product_rec.customer_ids:
            selected_supplier_info = product_rec.customer_ids.filtered(
                lambda x: x.name == partner_rec).filtered(
                        lambda q: q.qty <= qty).sorted(lambda s: qty - s.qty)
            if res.get('value', {}).get('name') and selected_supplier_info:
                pc = selected_supplier_info.product_code 
                pn = selected_supplier_info.product_name
                if pn and pc:
                    res['value']['name'] = pc + '---' + pn
                if pn and not pc:
                    res['value']['name'] = pn
        return res
