from .base_api import BaseAPI

class GetLastQuoteArrayShort(BaseAPI):
    def Get_LastQuoteArrayShort(self, exchange, instrument_identifiers):
        endpoint = "GetLastQuoteArrayShort/"
        params = {
            'exchange': exchange,
            'instrumentIdentifiers': instrument_identifiers
        }
        return self._get(endpoint, params)
