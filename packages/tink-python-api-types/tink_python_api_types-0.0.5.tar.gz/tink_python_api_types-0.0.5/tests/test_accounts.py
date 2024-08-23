from tink_python_api_types.account import (
    AccountsPage,
    Account,
    Balances,
    Identifiers,
    Dates,
    Iban,
    FinancialInstitution,
)
from tink_python_api_types.common import Amount


class TestAccounts:
    def test_accounts_page_is_buildable(self):
        page = AccountsPage(
            **{
                "accounts": [
                    {
                        "balances": {
                            "booked": {
                                "amount": {
                                    "currency_code": "EUR",
                                    "value": {"scale": "-3", "unscaled_value": "19"},
                                }
                            }
                        },
                        "customer_segment": "UNDEFINED_CUSTOMER_SEGMENT",
                        "dates": {"last_refreshed": "2020-12-15T12:16:58Z"},
                        "financial_institution_id": "6e68cc6287704273984567b3300c5822",
                        "id": "ee7ddbd178494220bb184791783f4f63",
                        "identifiers": {
                            "financial_institution": {
                                "account_number": "SE6930000000011273547693"
                            },
                            "iban": {
                                "bban": "0000011273547693",
                                "iban": "SE6930000000011273547693",
                            },
                        },
                        "name": "PERSONKONTO",
                        "type": "CHECKING",
                    }
                ],
                "next_page_token": "",
            }
        )
        assert type(page) is AccountsPage
        assert type(page.accounts[0]) is Account
        assert type(page.accounts[0].balances) is Balances
        assert type(page.accounts[0].balances.booked.amount) is Amount
        assert type(page.accounts[0].identifiers) is Identifiers
        assert type(page.accounts[0].identifiers.iban) is Iban
        assert (
            type(page.accounts[0].identifiers.financial_institution)
            is FinancialInstitution
        )
        assert type(page.accounts[0].dates) is Dates
