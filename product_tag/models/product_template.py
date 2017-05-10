# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.template'

    tag_ids = fields.Many2many('product.tag', string='Tags')
