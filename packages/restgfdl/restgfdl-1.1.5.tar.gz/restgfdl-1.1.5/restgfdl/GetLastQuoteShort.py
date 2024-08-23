from .base_api import BaseAPI

class GetLastQuoteShort(BaseAPI):
    def Get_LastQuoteShort(self, exchange, instrument_identifier):
        endpoint = "GetLastQuoteShort/"
        params = {
            'exchange': exchange,
            'instrumentIdentifier': instrument_identifier
        }
        return self._get(endpoint, params)
