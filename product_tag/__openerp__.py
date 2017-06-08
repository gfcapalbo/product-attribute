# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Tag",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "sales",
    "summary": "Adds tags to product",
    "depends": [
        'product',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_tag.xml',
    ],
}
