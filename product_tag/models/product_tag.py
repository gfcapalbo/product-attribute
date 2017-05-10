# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError

class ProductTag(models.Model):
    _name = 'product.tag'
    _description = 'Tags on products'


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        categories = self.search(args, limit=limit)
        return categories.name_get()

    name = fields.Char('Category Name', required=True, translate=True)
    parent_id = fields.Many2one(
        comodel_name='product.tag', string='Parent tag',
        select=True,  ondelete='cascade'
    )
    child_ids = fields.One2many('product.tag', 'parent_id', 'Child Categories')
    active= fields.Boolean('Active', default=True)
    product_ids = fields.Many2many('product.template', string='Products')

    api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_(
                'Error ! You can not create recursive tags.')
            )
