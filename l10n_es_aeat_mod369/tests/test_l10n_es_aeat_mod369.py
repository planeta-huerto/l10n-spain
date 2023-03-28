# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import \
    TestL10nEsAeatModBase
from odoo.tests.common import Form

_logger = logging.getLogger('aeat.369')


class TestL10nEsAeatMod369Base(TestL10nEsAeatModBase):

    def setUp(self):
        self.oss_country = self.env.ref("base.fr")
        general_tax = self.env.ref(
            "l10n_es.%s_account_tax_template_s_iva21b" % self.company.id
        )
        wizard = self.env["l10n.eu.oss.wizard"].create(
            {
                "company_id": self.company.id,
                "general_tax": general_tax.id,
                "todo_country_ids": [(4, self.oss_country.id)],
            }
        )
        wizard.generate_eu_oss_taxes()
        self.taxes_sale = {}
        self.oss_tax = self.env["account.tax"].search(
            [
                ("oss_country_id", "=", self.oss_country.id),
                ("company_id", "=", self.company.id),
            ]
        )
        line_data = {
            "name": "Test for OSS tax",
            "account_id": self.accounts["700000"].id,
            "price_unit": 100,
            "quantity": 1,
            "invoice_line_tax_ids": [(4, self.oss_tax.id)],
        }
        line_vals = {"invoice_line_ids": [(0, 0, line_data)]}
        self.inv1 = self._invoice_sale_create("2022-12-01", line_vals)
        self.inv2 = self._invoice_sale_create("2023-01-01", line_vals)

        # Create reports
        mod369_form = Form(self.env["l10n.es.aeat.mod369.report"])
        mod369_form.company_id = self.company
        mod369_form.year = 2022
        mod369_form.period_type = "4T"
        mod369_form.company_vat = "1234567890"
        self.model369 = mod369_form.save()
        self.model369_4t = self.model369.copy(
            {
                "name": "3690000000002",
                "period_type": "4T",
                "date_start": "2022-10-01",
                "date_end": "2022-12-31",
            }
        )

    def test_model_369(self):
        self.model369.button_calculate()
        self._check_field_amount(self.model303, 123, 100)
        self._check_field_amount(self.model303, 126, 0)
        self.model303_4t.button_calculate()
        self._check_field_amount(self.model303_4t, 123, 100)
        self._check_field_amount(self.model303_4t, 126, 200)
