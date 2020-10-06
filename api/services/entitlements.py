import xmltodict

from .. import origin
from lib import utils

class EntitlementService(object):
    def __init__(self, session):
        self._session = session
    
    def get_owned_games(self):
        response = self._session._get(origin.API_ECOMMERCE_BASEGAMES_URL,
            use_token=True,
            headers={
                "Accept": "application/xml",
                "localeInfo": "en-US"
            }
        )

        return xmltodict.parse(response.text)

    def get_entitlement(self, product_id):
        response = self._session._get(origin.API_ECOMMERCE_ENTITLEMENT_URL,
            use_token=True,
            params={
                "productId": product_id
            },
            headers={
                "Accept": "application/json",
                "localeInfo": "en-US"
            }
        )

        return utils.json_decode(response.text)

    def get_entitlements(self):
        response = self._session._get(origin.API_ECOMMERCE_ENTITLEMENT_URL,
            use_token=True,
            headers={
                "Accept": "application/json",
                "localeInfo": "en-US"
            }
        )

        return utils.json_decode(response.text)

    def get_standard_games(self):
        response = self._session._get(origin.API_ECOMMERCE_VAULT_INFO_STANDARD_URL,
            use_token=True,
            headers={
                "Accept": "application/json",
                "localeInfo": "en-US"
            }
        )

        return utils.json_decode(response.text)

    def get_premium_games(self):
        response = self._session._get(origin.API_ECOMMERCE_VAULT_INFO_PREMIUM_URL,
            use_token=True,
            headers={
                "Accept": "application/json",
                "localeInfo": "en-US"
            }
        )

        return utils.json_decode(response.text)