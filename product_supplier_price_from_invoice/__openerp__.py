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
{
    "name": "Update supplier product prices from the invoice view",
    "version": "1.0",
    "author": "Therp BV",
    "license": "AGPL-3",
    "description": """
Allows to manage per-supplier prices directly from the invoice, by adding
an "Update price" button to the invoice when it's in draft state.
Clicking the button will show all products on the invoice
with their prices,it is possible to assign the new unit price
for that supplier.

All new and updated prices are to be considered for quantities of 1.

Supplier prices can be updated from this interface,
all prices are to be considered for quantities of one.
For products with a non zero value in the "new price"
field a new pricelist will be generated or an existing
pricelist for quantities of 1 will be updated.
If more than one pricelist for quantities of 1 exist
the first one will be updated and the others will be deleted.

Note
====================

In Order to use the supplier pricelists, this option must be enabled under
Settings -> Configuration -> Purchases. Apart from that, you need to add a
new rule to the default purchase pricelist version based on 'Supplier
prices on the product form'. This rule must have a higher priority than
the default rule.
""",
    "category": "Accounting & Finance",
    "depends": [
        'product',
        'account',
    ],
    "data": [
        'view/account_invoice_updateprice.xml',
    ],
    'test': [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {'python': [], },
}
